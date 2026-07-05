"""
Offline test harness — stubs out get_llm/get_structured_llm so we can validate
graph wiring, routing, resume-gating, and the multi-turn flows WITHOUT hitting
any real Groq/OpenRouter network calls (this sandbox has no egress to those APIs).
"""
import os
import sys

os.environ.setdefault("GROQ_API_KEY", "dummy")
os.environ.setdefault("OPENROUTER_API_KEY", "dummy")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import AIMessage  # noqa: E402

import graph.nodes as nodes_mod  # noqa: E402
import agents.job_advice_agent as job_advice_mod  # noqa: E402
import agents.resume_advice_agent as resume_advice_mod  # noqa: E402
import agents.job_prep_agent as job_prep_mod  # noqa: E402


class FakeIntentResult:
    def __init__(self, intent):
        self.intent = intent


class FakeStructuredLLM:
    """Returns a fixed/derived intent based on simple keyword sniffing,
    mimicking what a real classifier would decide for these test inputs."""

    def invoke(self, messages):
        system_text = messages[0].content.lower()
        text = messages[-1].content.lower()
        active_jd_session = "active interview-prep session" in system_text

        if active_jd_session and ("question" in text or "interview" in text):
            intent = "job_prep"
        elif "resume" in text or "cv " in text:
            intent = "resume_advice"
        elif "job opening" in text or "job listing" in text or "find me a job" in text:
            intent = "job_search"
        elif "interview" in text or "prep" in text:
            intent = "job_prep"
        elif "career" in text or "switch" in text:
            intent = "job_advice"
        else:
            intent = "unknown"
        return FakeIntentResult(intent)


class FakeChatLLM:
    """Generic fake chat model — echoes back a recognizable canned reply."""

    def __init__(self, tag):
        self.tag = tag

    def invoke(self, messages):
        last_human = messages[-1].content
        return AIMessage(content=f"[{self.tag} REPLY] (saw: {last_human[:60]!r})")


def fake_get_structured_llm(schema, temperature=0.0):
    return FakeStructuredLLM()


def fake_get_llm(temperature=0.4):
    return FakeChatLLM("GENERIC")


# Patch the names each module imported at module-load time.
nodes_mod.get_structured_llm = fake_get_structured_llm
job_advice_mod.get_llm = fake_get_llm
resume_advice_mod.get_llm = fake_get_llm
job_prep_mod.get_llm = fake_get_llm

from graph.build import build_graph  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402

graph_app = build_graph()


def send(thread_id, text, db_profile=None, intent=None):
    config = {"configurable": {"thread_id": thread_id}}
    input_state = {"messages": [HumanMessage(content=text)], "user_id": thread_id}
    if db_profile is not None:
        input_state["db_profile"] = db_profile
    if intent is not None:
        input_state["intent"] = intent
    result = graph_app.invoke(input_state, config=config)
    print(f">>> USER: {text}")
    print(f"<<< INTENT: {result.get('intent')} | awaiting_jd: {result.get('awaiting_jd')}")
    print(f"<<< BOT: {result.get('response')}\n")
    return result


print("=== Test 1: career advice routing (no resume needed) ===")
r = send("user1", "I want to switch my career from QA to backend dev, any advice?")
assert r["intent"] == "job_advice"
assert "[GENERIC REPLY]" in r["response"]

print("=== Test 2: resume_advice GATED when no resume on file ===")
r = send("user2", "Can you review my resume?", db_profile={})
assert r["intent"] == "resume_advice"
assert "resume" in r["response"].lower() and "upload" in r["response"].lower(), (
    "Expected the resume-gating prompt, got: " + r["response"]
)

print("=== Test 3: resume_advice UNGATED once resume_text is on file ===")
r = send(
    "user3",
    "Can you review my resume?",
    db_profile={"resume_text": "Some stored resume text...", "skills": ["Python"]},
)
assert r["intent"] == "resume_advice"
assert "[GENERIC REPLY]" in r["response"], "Expected the real resume_advice_agent to run"

print("=== Test 4: unknown/greeting routing ===")
r = send("user4", "hey there")
assert r["intent"] == "unknown"

print("=== Test 5: job_prep GATED when no resume on file (manual JD path blocked) ===")
r = send("user5", "Can you help me prep for an interview?", db_profile={})
assert r["intent"] == "job_prep"
assert r.get("awaiting_jd") is not True, "Should NOT fall into the manual-JD flow while gated"
assert "resume" in r["response"].lower()

print("=== Test 6: job_prep auto-generates from resume skills (no JD asked) ===")
r = send(
    "user6",
    "Can you help me prep for an interview?",
    db_profile={
        "resume_text": "stored text",
        "skills": ["Python", "FastAPI", "AWS"],
        "designation": "Senior Backend Engineer",
        "profile": "Backend Developer",
    },
)
assert r["intent"] == "job_prep"
assert r.get("awaiting_jd") is not True, "Should skip asking for a JD when skills are known"
assert r["job_description"].startswith("[Derived from uploaded resume skills"), r["job_description"]
assert "[GENERIC REPLY]" in r["response"]

print("=== Test 7: job_prep follow-up reuses the skills-derived session ===")
r2 = send(
    "user6",
    "Give me 3 more questions on system design",
    db_profile={
        "resume_text": "stored text",
        "skills": ["Python", "FastAPI", "AWS"],
        "designation": "Senior Backend Engineer",
        "profile": "Backend Developer",
    },
)
assert r2["intent"] == "job_prep"
assert r2["job_description"].startswith("[Derived from uploaded resume skills")

print("=== Test 8: legacy manual-JD job_prep flow still works once resume is on file ===")
r3 = send(
    "user7",
    "Can you help me prep for an interview?",
    db_profile={"resume_text": "stored text", "skills": []},  # resume on file but no skills extracted
)
assert r3.get("awaiting_jd") is True, "With no skills, should fall back to asking for a JD"
r4 = send("user7", "We are hiring a Python backend developer with FastAPI and AWS experience.")
assert r4["awaiting_jd"] is False
assert "FastAPI" in r4["job_description"]

print("=== Test 9: post-confirmation continuation — intent pre-set, resume now on file ===")
# Simulates bot.py's _continue_pending_intent(): graph is invoked with `intent`
# already set (skipping the orchestrator) right after a resume gets confirmed.
r5 = send(
    "user8",
    "[Resume uploaded and confirmed — please continue.]",
    db_profile={
        "resume_text": "stored text",
        "skills": ["React", "TypeScript"],
        "designation": "Frontend Engineer",
    },
    intent="job_prep",
)
assert r5["intent"] == "job_prep"
assert r5["job_description"].startswith("[Derived from uploaded resume skills")
assert "[GENERIC REPLY]" in r5["response"]

print("=== Test 10: /reset equivalent (manual state wipe) check ===")
config = {"configurable": {"thread_id": "user7"}}
graph_app.update_state(config, {"job_description": None, "awaiting_jd": False, "intent": None})
state_after_reset = graph_app.get_state(config).values
print("State after reset:", {k: state_after_reset.get(k) for k in ("job_description", "awaiting_jd", "intent")})
assert state_after_reset.get("job_description") is None
assert state_after_reset.get("awaiting_jd") is False

print("\nALL ROUTING / GATING / STATE TESTS PASSED ✅")
