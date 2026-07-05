"""
Agent 4 — Interview preparation.

Flow:
  1. User asks for interview prep -> agent asks them to paste a job description
     (and sets `awaiting_jd=True` so the NEXT message is treated as the JD,
     bypassing the orchestrator entirely — see graph/build.py's entry routing).
  2. User pastes the JD -> agent generates a tailored Q&A set and stores the
     JD in state so later "more questions" follow-ups don't require re-pasting it.
  3. If the user asks a follow-up while a JD is already on file (e.g. "give me
     5 more on system design"), the agent reuses the stored JD plus the new
     instruction to generate more targeted questions.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from config import get_llm
from graph.state import AgentState
from utils import get_last_human_message

ASK_FOR_JD_MESSAGE = (
    "🎯 Happy to help you prep! Paste the *job description* you're targeting "
    "(role title + responsibilities/requirements is enough) and I'll build a "
    "set of likely interview questions with strong model answers."
)

QNA_SYSTEM_PROMPT = """You are an interview coach. Given a job description, produce a
focused interview-prep set for a Telegram chat:

- 2 short behavioral/HR questions with strong sample answers
- 4-6 technical/role-specific questions (derived from the actual JD requirements)
  with concise model answers (3-5 sentences each, not essays)
- End with 2 quick tips specific to this role

Format with clear numbering, *bold* question headers, and keep each answer tight
and skimmable on a phone screen. Use Telegram Markdown, not heavy headers."""

SKILLS_QNA_SYSTEM_PROMPT = """You are an interview coach. Given a candidate's extracted
resume skills and (optionally) their target role, produce a focused interview-prep set
for a Telegram chat — questions they're likely to actually be asked given THIS skill set:

- 2 short behavioral/HR questions with strong sample answers
- 4-6 technical questions, one per (or combining) the candidate's listed skills, with
  concise model answers (3-5 sentences each)
- End with 2 quick tips for presenting these specific skills well

Format with clear numbering, *bold* question headers, Telegram Markdown, skimmable on
a phone screen."""


def _generate_qna(job_description: str, extra_instruction: str = "") -> str:
    llm = get_llm(temperature=0.5)
    user_content = f"Job description:\n{job_description}"
    if extra_instruction:
        user_content += f"\n\nAdditional request from the candidate: {extra_instruction}"

    ai_msg = llm.invoke(
        [SystemMessage(content=QNA_SYSTEM_PROMPT), HumanMessage(content=user_content)]
    )
    return ai_msg.content


def _generate_qna_from_skills(
    skills: list, designation: str = None, profile: str = None, extra_instruction: str = ""
) -> str:
    llm = get_llm(temperature=0.5)
    user_content = f"Skills from resume: {', '.join(skills)}"
    if profile:
        user_content += f"\nCurrent profile: {profile}"
    if designation:
        user_content += f"\nTarget role: {designation}"
    if extra_instruction:
        user_content += f"\n\nAdditional request from the candidate: {extra_instruction}"

    ai_msg = llm.invoke(
        [SystemMessage(content=SKILLS_QNA_SYSTEM_PROMPT), HumanMessage(content=user_content)]
    )
    return ai_msg.content


def job_prep_agent(state: AgentState) -> AgentState:
    last_msg = get_last_human_message(state["messages"])
    db_profile = state.get("db_profile") or {}
    skills = db_profile.get("skills") or []

    # Case 1: we asked for the JD last turn -> this message IS the JD.
    if state.get("awaiting_jd"):
        state["job_description"] = last_msg
        state["awaiting_jd"] = False
        state["response"] = _generate_qna(last_msg)
        return state

    # Case 2: fresh "job_prep" intent, no JD on file yet.
    if not state.get("job_description"):
        if skills:
            # We already have a resume on file (this is how we got routed
            # here at all — see resolve_route_for_intent) -> go straight to
            # generating questions about the candidate's actual skills
            # instead of asking them to paste a JD they may not have.
            state["response"] = _generate_qna_from_skills(
                skills, designation=db_profile.get("designation"), profile=db_profile.get("profile")
            )
            state["job_description"] = f"[Derived from uploaded resume skills: {', '.join(skills)}]"
            return state

        # No skills on file either (shouldn't normally happen once gating is
        # in place, but kept as a safe fallback) -> ask for a JD directly.
        state["response"] = ASK_FOR_JD_MESSAGE
        state["awaiting_jd"] = True
        return state

    # Case 3: JD (or skills-derived session) already on file — treat this as
    # a follow-up request (e.g. "give me more questions on system design").
    if skills and state["job_description"].startswith("[Derived from uploaded resume skills"):
        state["response"] = _generate_qna_from_skills(
            skills,
            designation=db_profile.get("designation"),
            profile=db_profile.get("profile"),
            extra_instruction=last_msg,
        )
    else:
        state["response"] = _generate_qna(state["job_description"], extra_instruction=last_msg)
    return state
