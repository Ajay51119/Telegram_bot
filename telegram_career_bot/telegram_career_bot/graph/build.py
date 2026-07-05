"""
Builds the multi-agent LangGraph:

                         ┌─────────────┐
            awaiting_jd  │             │  intent already set   not set / fresh
        ┌────────────────┤    START    ├───────────┐            (normal case)
        │                └─────────────┘           │                 │
        ▼                                           ▼                 ▼
 job_prep_agent                          (same routing as below) orchestrator (LLM
        │                                                          intent classifier)
        │                                                               │
        │                ┌──────────────┬───────────────┬───────────────┼──────────────┐
        │                ▼              ▼               ▼               ▼              ▼
        │         job_advice_agent  resume_advice   job_search_agent  request_resume  clarify_agent
        │                │            _agent*            │            (no resume on    (unknown/
        │                │               │               │             file yet for     greeting)
        │                │               │               │             resume_advice/
        │                │               │               │             job_prep)
        │                └───────────────┴───────────────┴───────────────┴──────────────┘
        │                                                │
        ▼                                               END
       END

*resume_advice_agent / job_prep_agent are only reachable once a resume is on
file (db_profile.resume_text) — see graph/nodes.py:resolve_route_for_intent.

The "intent already set" entry path lets bot.py resume a gated flow right
after the user uploads + confirms their resume: it re-invokes the graph with
`intent` pre-filled (skipping a redundant orchestrator call) and the agent
picks up immediately, e.g. job_prep_agent auto-generating Q&A from the
candidate's freshly-extracted skills instead of asking for a JD again.

A `MemorySaver` checkpoint keeps each Telegram chat's conversation state
(messages, job_description, awaiting_jd) persisted across turns, keyed by
`thread_id` = the Telegram chat id. The user's *profile* (name/email/resume/
skills) lives in SQLite (db/database.py) instead — that's the durable store;
db_profile is just injected into the graph state per-invoke.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents.job_advice_agent import job_advice_agent
from agents.job_prep_agent import job_prep_agent
from agents.job_search_agent import job_search_agent
from agents.resume_advice_agent import resume_advice_agent
from graph.nodes import (
    clarify_node,
    orchestrator_node,
    request_resume_node,
    resolve_route_for_intent,
)
from graph.state import AgentState

# Every possible destination reachable from either START (when intent is
# pre-set) or "orchestrator" (after classification). Passing the same
# superset map to both add_conditional_edges calls keeps the gating logic
# defined in exactly one place (resolve_route_for_intent).
ROUTE_MAP = {
    "orchestrator": "orchestrator",
    "job_prep_agent": "job_prep_agent",
    "job_advice": "job_advice_agent",
    "resume_advice": "resume_advice_agent",
    "job_search": "job_search_agent",
    "job_prep": "job_prep_agent",
    "request_resume": "request_resume",
    "unknown": "clarify_agent",
}


def _route_initial(state: AgentState) -> str:
    """If we're mid-way through the job-prep JD flow, skip straight there.
    If bot.py already pre-set `intent` (continuing a gated flow after a
    resume upload), skip the orchestrator and resolve directly. Otherwise,
    classify the message normally."""
    if state.get("awaiting_jd"):
        return "job_prep_agent"
    if state.get("intent"):
        return resolve_route_for_intent(state)
    return "orchestrator"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("job_advice_agent", job_advice_agent)
    graph.add_node("resume_advice_agent", resume_advice_agent)
    graph.add_node("job_search_agent", job_search_agent)
    graph.add_node("job_prep_agent", job_prep_agent)
    graph.add_node("clarify_agent", clarify_node)
    graph.add_node("request_resume", request_resume_node)

    graph.add_conditional_edges(START, _route_initial, ROUTE_MAP)
    graph.add_conditional_edges("orchestrator", resolve_route_for_intent, ROUTE_MAP)

    for node in (
        "job_advice_agent",
        "resume_advice_agent",
        "job_search_agent",
        "job_prep_agent",
        "clarify_agent",
        "request_resume",
    ):
        graph.add_edge(node, END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)
