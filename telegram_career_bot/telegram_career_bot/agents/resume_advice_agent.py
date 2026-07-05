"""Agent 2 — Resume / CV advice."""

from langchain_core.messages import SystemMessage

from config import get_llm
from graph.state import AgentState

SYSTEM_PROMPT = """You are a professional resume reviewer and career coach chatting on Telegram.
Help with resumes, CVs, and cover letters: structure, ATS-friendliness, bullet-point
rewriting (impact + numbers), formatting, and tailoring to a target role.

Style rules:
- If resume text is available (either pasted by the user or provided below as their
  uploaded resume), give concrete line-by-line feedback (quote the weak line, then
  give a stronger rewrite).
- If no resume text is available at all, give general best-practice tips and ask them
  to paste/upload the resume section they want reviewed.
- Keep it skimmable: short paragraphs or bullet points, Telegram Markdown (*bold*), a
  couple of relevant emojis. Avoid long unbroken paragraphs."""


def resume_advice_agent(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0.4)
    db_profile = state.get("db_profile") or {}
    resume_text = db_profile.get("resume_text")

    system_prompt = SYSTEM_PROMPT
    if resume_text:
        # Auto-inject the candidate's stored resume as context so they don't
        # have to re-paste it every time they ask a resume question.
        system_prompt += (
            f"\n\nThe candidate's uploaded resume text (use this for any feedback unless "
            f"they pasted different text in their message):\n---\n{resume_text[:6000]}\n---"
        )

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    ai_msg = llm.invoke(messages)
    state["response"] = ai_msg.content
    return state
