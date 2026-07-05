"""Agent 3 — Current job openings (tool-calling agent over the dummy JSON dataset)."""

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from config import get_llm
from graph.state import AgentState
from tools.job_search_tool import search_jobs
from utils import get_last_human_message

SYSTEM_PROMPT = """You help users find current job openings using the search_jobs tool.
Extract a role/skill keyword and an optional location from the user's message, call the
tool, then present the results conversationally on Telegram (keep the tool's formatting,
just add a one-line friendly intro/outro). If the tool finds nothing, suggest the user
try a broader search term."""


def job_search_agent(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0.2)
    agent = create_agent(llm, tools=[search_jobs], system_prompt=SYSTEM_PROMPT)

    last_user_msg = get_last_human_message(state["messages"])
    result = agent.invoke({"messages": [HumanMessage(content=last_user_msg)]})

    state["response"] = result["messages"][-1].content
    return state
