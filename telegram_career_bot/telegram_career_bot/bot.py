"""
Telegram bot entrypoint.

Run with:  python bot.py
Requires TELEGRAM_BOT_TOKEN (and GROQ_API_KEY / OPENROUTER_API_KEY) in .env

Onboarding + resume pipeline (high level):
  /start (or first message ever) -> ask for name+email OR a resume upload
  -> name/email build a bare profile row (profile/designation NULL)
  -> a resume upload (PDF/DOCX/photo, OCR-backed) extracts name, email,
     profile, designation, skills -> staged for confirmation via inline
     buttons -> on confirm, written to SQLite.
  -> Asking a resume/interview-prep question with no resume on file gets
     gated: the bot asks for a resume first, then automatically resumes
     that original request once the resume is confirmed.
"""

import logging
import os
import tempfile
from pathlib import Path

from langchain_core.messages import HumanMessage
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import db.database as db
from config import LLM_PROVIDER, TELEGRAM_BOT_TOKEN
from graph.build import build_graph
from resume.confirmation import build_confirmation_text
from resume.extractor import extract_resume_text, is_valid_email
from resume.parser import parse_resume_text

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", level=logging.INFO
)
logger = logging.getLogger("career_bot")

career_graph = build_graph()

ONBOARDING_INTRO = (
    "👋 *Welcome to your AI Career Assistant!*\n\n"
    "Let's get you set up — you can either:\n"
    "📝 Tell me your *name*, or\n"
    "📄 Upload your *resume* (PDF, DOCX, or a clear photo) and I'll grab everything "
    "automatically.\n\n"
    "What's your name?"
)

RETURNING_USER_MENU = (
    "👋 Welcome back{name_suffix}!\n\n"
    "I can help you with:\n"
    "🧭 Career advice\n"
    "📄 Resume / CV feedback\n"
    "🔍 Current job openings (demo dataset)\n"
    "🎯 Interview prep\n\n"
    "Use /reset to clear the current chat context, or /profile to see what I know about you."
)

SUPPORTED_DOC_EXTS = (".pdf", ".docx", ".doc", ".txt")


def _db_profile_dict(user: dict) -> dict:
    user = user or {}
    return {
        "username": user.get("username"),
        "email": user.get("email"),
        "profile": user.get("profile"),
        "designation": user.get("designation"),
        "skills": user.get("skills") or [],
        "resume_text": user.get("resume_text"),
    }


async def _safe_reply(update: Update, text: str) -> None:
    try:
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception:
        # Fall back to plain text if the model produced Markdown Telegram can't parse.
        await update.message.reply_text(text)


# ───────────────────────────── Commands ─────────────────────────────


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = str(update.effective_chat.id)
    user = db.get_or_create_user(telegram_id)

    if user["onboarding_stage"] == "new":
        db.update_user(telegram_id, onboarding_stage="awaiting_name")
        await update.message.reply_text(ONBOARDING_INTRO, parse_mode="Markdown")
    else:
        name_suffix = f", {user['username']}" if user.get("username") else ""
        await update.message.reply_text(
            RETURNING_USER_MENU.format(name_suffix=name_suffix), parse_mode="Markdown"
        )


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = str(update.effective_chat.id)
    user = db.get_user(telegram_id)
    if not user:
        await update.message.reply_text("I don't have a profile for you yet — send /start to get going!")
        return

    skills = ", ".join(user.get("skills") or []) or "—"
    text = (
        "🗂️ *Your profile*\n"
        f"🙋 Name: {user.get('username') or '—'}\n"
        f"📧 Email: {user.get('email') or '—'}\n"
        f"🧩 Profile: {user.get('profile') or '—'}\n"
        f"🎯 Looking for: {user.get('designation') or '—'}\n"
        f"🛠️ Skills: {skills}\n"
        f"📄 Resume on file: {'Yes' if user.get('resume_text') else 'No'}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clears LangGraph conversation context only — NOT the stored profile."""
    chat_id = str(update.effective_chat.id)
    config = {"configurable": {"thread_id": chat_id}}
    career_graph.update_state(
        config, {"job_description": None, "awaiting_jd": False, "intent": None}
    )
    await update.message.reply_text("🔄 Context cleared — starting fresh!")


# ───────────────────────────── Text messages ─────────────────────────────


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = str(update.effective_chat.id)
    user_text = update.message.text
    user = db.get_or_create_user(telegram_id)
    stage = user.get("onboarding_stage", "new")

    # ── Onboarding wizard ──
    if stage == "new":
        db.update_user(telegram_id, onboarding_stage="awaiting_name")
        await update.message.reply_text(ONBOARDING_INTRO, parse_mode="Markdown")
        return

    if stage == "awaiting_name":
        name = user_text.strip()
        db.update_user(telegram_id, username=name, onboarding_stage="awaiting_email")
        await update.message.reply_text(f"Nice to meet you, {name}! 📧 What's your email?")
        return

    if stage == "awaiting_email":
        email = user_text.strip()
        if not is_valid_email(email):
            await update.message.reply_text(
                "Hmm, that doesn't look like a valid email — mind trying again?"
            )
            return
        db.update_user(telegram_id, email=email, onboarding_stage="onboarding_complete")
        await update.message.reply_text(
            "🎉 You're all set! Upload your resume anytime (PDF/DOCX/photo) and I'll auto-fill "
            "your profile, target role, and skills."
        )
        return

    # ── Normal LangGraph flow ──
    graph_config = {"configurable": {"thread_id": telegram_id}}
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    db_profile = _db_profile_dict(user)

    allowed, _ = db.consume_tokens(telegram_id)
    if not allowed:
        await update.message.reply_text(
            "⚠️ Your token limit has been reached. Please recharge your wallet to continue."
        )
        return

    try:
        result = career_graph.invoke(
            {
                "messages": [HumanMessage(content=user_text)],
                "user_id": telegram_id,
                "db_profile": db_profile,
            },
            config=graph_config,
        )
        reply = result.get("response") or "Sorry, I didn't get a response there — try rephrasing?"

        # If this request just got gated behind a resume upload, remember
        # which intent to resume once the user uploads + confirms one.
        intent = result.get("intent")
        if intent in ("resume_advice", "job_prep") and not db_profile.get("resume_text"):
            db.update_user(telegram_id, pending_intent=intent)
    except Exception:
        logger.exception("Error while processing message for chat %s", telegram_id)
        reply = "⚠️ I hit an error processing that. Please try again in a moment."

    await _safe_reply(update, reply)


# ───────────────────────────── Resume uploads ─────────────────────────────


async def _process_resume_text(update: Update, telegram_id: str, resume_text: str) -> None:
    if not resume_text or len(resume_text.strip()) < 20:
        await update.message.reply_text(
            "⚠️ I couldn't pull readable text out of that file (it may be a low-quality scan). "
            "Could you try a clearer photo/PDF, or paste your resume text directly?"
        )
        return

    extracted = parse_resume_text(resume_text)
    existing_user = db.get_user(telegram_id) or {}

    # Stage the extraction for confirmation rather than writing straight to
    # the profile — see handle_confirmation_callback.
    pending = {
        "name": extracted.name,
        "email": extracted.email,
        "profile": extracted.profile,
        "designation": extracted.designation,
        "skills": extracted.skills,
        "resume_text": resume_text,
    }
    db.update_user(telegram_id, pending_extraction=pending)

    text = build_confirmation_text(extracted, existing_user)
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Yes, update my profile", callback_data="resume_confirm"),
                InlineKeyboardButton("✏️ No, let me correct it", callback_data="resume_edit"),
            ]
        ]
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = str(update.effective_chat.id)
    document = update.message.document
    file_name = document.file_name or "resume"
    ext = Path(file_name).suffix.lower() or ".pdf"

    if ext not in SUPPORTED_DOC_EXTS:
        await update.message.reply_text(
            "I can read PDF, DOCX, or TXT resumes (or a clear photo) — could you upload one of those?"
        )
        return

    db.get_or_create_user(telegram_id)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text("📄 Got it — reading your resume now...")

    tg_file = await document.get_file()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp_path = tmp.name
        await tg_file.download_to_drive(tmp_path)
        resume_text = extract_resume_text(tmp_path, ext)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    await _process_resume_text(update, telegram_id, resume_text)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = str(update.effective_chat.id)
    photo = update.message.photo[-1]  # largest available size

    db.get_or_create_user(telegram_id)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    await update.message.reply_text("📸 Got it — running OCR on your resume photo...")

    tg_file = await photo.get_file()
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        await tg_file.download_to_drive(tmp_path)
        resume_text = extract_resume_text(tmp_path, ".jpg")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    await _process_resume_text(update, telegram_id, resume_text)


# ─────────────────────── Confirmation button callback ───────────────────────


async def _continue_pending_intent(query, telegram_id: str, intent: str) -> None:
    user = db.get_user(telegram_id) or {}
    db_profile = _db_profile_dict(user)
    graph_config = {"configurable": {"thread_id": telegram_id}}
    placeholder = "[Resume uploaded and confirmed — please continue.]"

    try:
        result = career_graph.invoke(
            {
                "messages": [HumanMessage(content=placeholder)],
                "user_id": telegram_id,
                "intent": intent,
                "db_profile": db_profile,
            },
            config=graph_config,
        )
        reply = result.get("response") or "Let's continue — what would you like to know?"
    except Exception:
        logger.exception("Error continuing pending intent for chat %s", telegram_id)
        reply = "⚠️ I hit an error continuing that — feel free to just ask again."

    try:
        await query.message.reply_text(reply, parse_mode="Markdown")
    except Exception:
        await query.message.reply_text(reply)


async def handle_confirmation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    telegram_id = str(query.message.chat_id)
    await query.answer()

    user = db.get_user(telegram_id) or {}

    if query.data == "resume_edit":
        db.update_user(telegram_id, pending_extraction=None, onboarding_stage="awaiting_name")
        await query.edit_message_text("No problem! What's your name?")
        return

    pending = user.get("pending_extraction")
    if not pending:
        await query.edit_message_text("That confirmation has expired — please re-upload your resume.")
        return

    update_fields = {
        "username": pending.get("name") or user.get("username"),
        "email": pending.get("email") or user.get("email"),
        "profile": pending.get("profile") or user.get("profile"),
        "designation": pending.get("designation") or user.get("designation"),
        "skills": pending.get("skills") or user.get("skills") or [],
        "resume_text": pending.get("resume_text"),
        "pending_extraction": None,
    }
    if user.get("onboarding_stage") in ("new", "awaiting_name", "awaiting_email"):
        update_fields["onboarding_stage"] = "onboarding_complete"

    db.update_user(telegram_id, **update_fields)
    await query.edit_message_text(
        "✅ Profile updated! Thanks — I'll use this to personalize things going forward."
    )

    # If this resume upload was triggered by a gated resume_advice/job_prep
    # request, automatically pick that conversation back up now.
    pending_intent = user.get("pending_intent")
    if pending_intent:
        db.update_user(telegram_id, pending_intent=None)
        await _continue_pending_intent(query, telegram_id, pending_intent)


# ───────────────────────────── Entrypoint ─────────────────────────────


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set. Copy .env.example to .env and fill it in."
        )

    db.init_db()
    logger.info("Starting career bot with LLM_PROVIDER=%s", LLM_PROVIDER)

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CallbackQueryHandler(handle_confirmation_callback, pattern="^resume_(confirm|edit)$"))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
