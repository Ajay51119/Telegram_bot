"""
Central configuration for the career-assistant bot.

This is the ONLY place you need to touch to change which LLM backend
the whole app uses.

------------------------------------------------------------------
HOW THE AUTO-SELECTION WORKS
------------------------------------------------------------------
LLM_PROVIDER (below) is a single global switch: "groq" or "openrouter".

  * Whichever provider you set becomes the PRIMARY model used everywhere
    (orchestrator + all 4 agents).
  * The OTHER provider is automatically wired in as a FALLBACK using
    LangChain's `.with_fallbacks()` — if the primary call raises an
    exception (rate limit, timeout, invalid key, model decommissioned,
    etc.) the request is silently retried on the fallback provider.

So you never have to touch agent code to switch providers — just flip
LLM_PROVIDER (or set the LLM_PROVIDER env var) and everything re-routes.
------------------------------------------------------------------
"""

import os
from typing import Literal, Type

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# ============================================================
# 🔧 GLOBAL PROVIDER SWITCH — change this or set the env var
# ============================================================
LLM_PROVIDER: Literal["groq", "openrouter"] = os.getenv("LLM_PROVIDER", "groq").lower()  # type: ignore

# ── Secrets ───────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ── Model picks per provider ───────────────────────────────────
# Groq: openai/gpt-oss-120b is Groq's currently recommended production
# model (Llama-3.3-70b-versatile is being deprecated 08/16/2026) — big
# context, strong reasoning, native tool-use, and very fast on Groq's LPUs.
# OpenRouter: "openrouter/free" is OpenRouter's own auto-router across
# whatever free models are currently healthy. The free-model roster on
# OpenRouter rotates/gets pulled often (Qwen3 Coder free and DeepSeek R1
# free both disappeared in June 2026) so pinning a single ":free" model id
# is fragile — the router model avoids that breakage. Swap in a pinned
# model below if you'd rather control it explicitly.
MODELS = {
    "groq": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    "openrouter": os.getenv("OPENROUTER_MODEL", "openrouter/free"),
    # Other solid OpenRouter free alternatives, if you want to pin one:
    #   "meta-llama/llama-3.3-70b-instruct:free"
    #   "openai/gpt-oss-120b:free"
}

DEFAULT_TEMPERATURE = 0.4


def _build_groq(temperature: float = DEFAULT_TEMPERATURE):
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=MODELS["groq"],
        temperature=temperature,
        api_key=GROQ_API_KEY,
    )


def _build_openrouter(temperature: float = DEFAULT_TEMPERATURE):
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=MODELS["openrouter"],
        temperature=temperature,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )


def _primary_and_fallback(temperature: float):
    """Return (primary_llm, fallback_llm) based on LLM_PROVIDER."""
    groq_llm = _build_groq(temperature)
    openrouter_llm = _build_openrouter(temperature)
    if LLM_PROVIDER == "openrouter":
        return openrouter_llm, groq_llm
    return groq_llm, openrouter_llm  # default: groq primary


def get_llm(temperature: float = DEFAULT_TEMPERATURE):
    """
    Plain chat model for free-form text generation (advice, Q&A, etc).
    Automatically falls back to the other provider on error.
    """
    primary, fallback = _primary_and_fallback(temperature)
    return primary.with_fallbacks([fallback])


def get_structured_llm(schema: Type[BaseModel], temperature: float = 0.0):
    """
    Structured-output chat model (used by the orchestrator's intent
    classifier). `.with_structured_output()` has to be applied to each
    underlying chat model BEFORE chaining the fallback, since the
    fallback wrapper itself isn't a chat model.
    """
    primary, fallback = _primary_and_fallback(temperature)
    primary_structured = primary.with_structured_output(schema)
    fallback_structured = fallback.with_structured_output(schema)
    return primary_structured.with_fallbacks([fallback_structured])
