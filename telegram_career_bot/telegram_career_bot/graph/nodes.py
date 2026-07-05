"""
Orchestrator layer.

This is the "brain" that reads the user's latest message and decides
which of the 4 specialist agents should handle it. It uses structured
output (a Pydantic schema) so the LLM is forced to return exactly one
of the 4 valid labels rather than free text we'd need to parse.
"""

from typing import Literal

from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field

from config import get_structured_llm
from graph.state import AgentState

ORCHESTRATOR_SYSTEM_PROMPT = """You are the intent router for a career-assistant Telegram bot.
Read the user's latest message and classify it into exactly ONE category:

- job_advice: general career guidance — career switching, upskilling advice,
  choosing a career path, motivation, salary negotiation, work-life questions.
- resume_advice: anything about resumes/CVs/cover letters — review, formatting,
  ATS optimization, what to include/remove, bullet-point rewriting.
- job_search: the user wants to see/find current job openings or listings.
- job_prep: the user wants interview preparation — mock questions and answers,
  ideally for a specific role or job description.
- unknown: greetings, small talk, or anything that clearly doesn't fit above.

Pick the single best-fitting category. When in doubt between job_advice and
one of the others, prefer the more specific category."""


class IntentClassification(BaseModel):
    intent: Literal["job_advice", "resume_advice", "job_search", "job_prep", "unknown"] = Field(
        description="The single best-matching category for the user's message."
    )


def orchestrator_node(state: AgentState) -> AgentState:
    # Use a short window of recent turns (not just the bare latest message)
    # so a follow-up like "give me 3 more questions" gets classified using
    # the actual conversation thread instead of in isolation.
    recent_messages = state["messages"][-6:]

    system_prompt = ORCHESTRATOR_SYSTEM_PROMPT
    if state.get("job_description"):
        system_prompt += (
            "\n\nContext: the user already has an active interview-prep session with "
            "a job description on file. If this message is a follow-up asking for "
            "more/different interview questions, or otherwise continues that thread, "
            "classify it as job_prep."
        )

    classifier = get_structured_llm(IntentClassification, temperature=0.0)
    result: IntentClassification = classifier.invoke(
        [SystemMessage(content=system_prompt)] + recent_messages
    )

    state["intent"] = result.intent
    return state


def clarify_node(state: AgentState) -> AgentState:
    """Fallback node for greetings / unclear intent."""
    state["response"] = (
        "👋 Hi! I'm your AI career assistant. I can help with:\n\n"
        "🧭 *Career advice* — e.g. \"should I switch from QA to dev?\"\n"
        "📄 *Resume feedback* — paste your resume text and ask for a review\n"
        "🔍 *Job search* — e.g. \"show me python developer jobs in Hyderabad\"\n"
        "🎯 *Interview prep* — e.g. \"prep me for this job description\"\n\n"
        "What would you like help with?"
    )
    return state


# Intents that genuinely need resume content to give a good answer. job_search
# (browsing listings) and job_advice (general guidance) are deliberately left
# ungated — only resume review and interview prep require a resume on file.
RESUME_GATED_INTENTS = {"resume_advice", "job_prep"}


def request_resume_node(state: AgentState) -> AgentState:
    """Routed to instead of the real agent when the user asked a resume- or
    interview-prep-related question but has no resume on file yet."""
    state["response"] = (
        "📄 To give you tailored help here, I'll need your resume first.\n\n"
        "Please upload it as a *PDF, DOCX, or even a clear photo* and I'll "
        "pull out your details automatically — then we'll pick this right back up."
    )
    return state


def resolve_route_for_intent(state: AgentState) -> str:
    """Shared routing decision used both as the graph's entry router (when an
    intent has already been pre-set, e.g. resuming after a resume upload) and
    as the orchestrator's own conditional edge. Centralizing this means the
    resume-gating rule only has to be written once."""
    intent = state.get("intent") or "unknown"
    db_profile = state.get("db_profile") or {}
    has_resume = bool(db_profile.get("resume_text"))

    if intent in RESUME_GATED_INTENTS and not has_resume:
        return "request_resume"
    return intent
