"""Shared state schema passed between all LangGraph nodes."""

from typing import Annotated, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    # Full chat history for this Telegram user. `add_messages` is a reducer
    # that APPENDS new messages instead of overwriting the list, so the
    # LangGraph checkpointer accumulates conversation history turn-by-turn.
    messages: Annotated[List[BaseMessage], add_messages]

    # Telegram chat id, used as the LangGraph thread_id too.
    user_id: str

    # Set by the orchestrator node. One of: job_advice, resume_advice,
    # job_search, job_prep, unknown.
    intent: Optional[str]

    # Sticky fields for the multi-turn "job prep" flow.
    job_description: Optional[str]
    awaiting_jd: Optional[bool]

    # The reply text the bot will send back to the user this turn.
    response: Optional[str]

    # Snapshot of the user's SQLite profile row (see db/database.py), injected
    # by bot.py on every invoke so agents can personalize without querying the
    # DB themselves. Expected keys: username, email, profile, designation,
    # skills (list[str]), resume_text. May be None/empty for a brand-new user.
    db_profile: Optional[dict]
