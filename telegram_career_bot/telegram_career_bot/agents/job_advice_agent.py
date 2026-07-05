"""Agent 1 — Job / career advice."""

from langchain_core.messages import SystemMessage

from config import get_llm
from graph.state import AgentState

SYSTEM_PROMPT = """You are an experienced, encouraging career coach chatting with someone on Telegram.
Give practical, specific career advice — career switching, upskilling paths, salary
negotiation, choosing between offers, work-life balance, etc.

Style rules:
- Keep replies tight: 4-8 short lines, not an essay.
- Use a couple of emojis and Telegram-friendly Markdown (*bold*, bullet points).
- Ask at most one short follow-up question if you genuinely need more context,
  otherwise just answer directly."""


def job_advice_agent(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0.5)
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    ai_msg = llm.invoke(messages)
    state["response"] = ai_msg.content
    return state
