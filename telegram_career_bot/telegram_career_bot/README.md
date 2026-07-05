# Career Assistant Telegram Bot (LangGraph multi-agent + resume profile system)

An agentic Telegram bot built with **LangGraph**. An orchestrator node classifies
each message's intent, then routes it to one of four specialist agents — gated
behind a SQLite-backed user profile that's built up via onboarding and resume
uploads (with free OCR fallback for scanned/photo resumes).

## Conversation flow

```
New chat
  │
  ▼
"What's your name, or upload your resume?"
  │                                  │
  ▼ (types name)                     ▼ (uploads PDF/DOCX/photo)
ask for email                  extract text (+ OCR if scanned)
  │                                  │
  ▼                            parse via LLM -> name/email/profile/
row created in SQLite:         designation/skills
(profile, designation = NULL)        │
                                      ▼
                              "I got name=X, email=Y, profile=Z,
                               looking for=W — update your profile?"
                               [✅ Confirm]  [✏️ Edit]
                                      │
                                      ▼ (confirm)
                              SQLite row updated (fills in whichever
                              of profile/designation/skills were NULL)
```

Once onboarding is done, every message goes through the LangGraph orchestrator:

```
                    ┌──────────────┐
   awaiting_jd OR   │    START     │   fresh message
   pre-set intent   │              │
  ┌──────────────────┤              ├───────────────────┐
  │                  └──────────────┘                    │
  ▼                                                       ▼
job_prep_agent (JD flow)                          orchestrator (LLM intent
  ▲                                                  classifier)
  │                    ┌───────────┬───────────────┬──────┼──────────┐
  │                    ▼           ▼               ▼      ▼          ▼
  │             job_advice   resume_advice*  job_search  request_resume  clarify_agent
  │               _agent       _agent          _agent    (no resume on    (unknown /
  │                  │            │               │       file yet)       greeting)
  └──────────────────┴────────────┴───────────────┴───────────┴───────────┘
                                       │
                                      END
```

`*` `resume_advice_agent` and `job_prep_agent` are **resume-gated** — see below.
`job_search_agent` and `job_advice_agent` are **not** gated (browsing listings
or getting general career guidance doesn't need a resume on file).

## Resume gating + auto-continuation

If the user asks a resume-review or interview-prep question and has **no
resume on file**, the orchestrator routes to `request_resume` instead of the
real agent, and the bot asks them to upload one. `bot.py` remembers which
intent was blocked (`pending_intent` in SQLite). Once the user uploads a
resume and taps **✅ Confirm**, the bot automatically re-invokes the graph
with that same intent pre-set — so the original question gets answered
immediately, no need to re-ask it.

For `job_prep` specifically: once a resume is on file, the agent **skips
asking for a job description** and instead generates interview questions
directly from the candidate's **extracted skills** + target designation —
i.e. "ask questions about the skills they uploaded," as requested. If resume
text exists but skills couldn't be extracted, it falls back to the original
"paste a JD" flow.

## The 4 agents

| # | Agent | What it does | Resume-gated? |
|---|-------|---------------|---|
| 1 | `job_advice_agent` | General career advice. | No |
| 2 | `resume_advice_agent` | Resume/CV feedback — auto-uses the stored resume text as context. | **Yes** |
| 3 | `job_search_agent` | Finds "current" openings via a **dummy tool** (`tools/job_search_tool.py`) reading `data/jobs.json`. Swap for a real job-board API later. | No |
| 4 | `job_prep_agent` | Interview Q&A — either from the candidate's resume skills (default once a resume is on file) or a pasted JD (fallback). | **Yes** |

## Resume extraction pipeline (`resume/`)

- **`extractor.py`** — low-weight, free extraction:
  - PDF → direct text via `pypdf` (fast, works for the vast majority of resumes).
  - DOCX → `python-docx`.
  - If a PDF yields almost no text (scanned/image-based) → **OCR fallback**:
    `pdf2image` rasterizes pages, `pytesseract` (Tesseract, free/open-source OCR)
    reads them.
  - Photo uploads go straight through `pytesseract` OCR.
  - **System dependencies**: `tesseract-ocr` + `poppler-utils` (already installed
    in the provided `Dockerfile`; install them yourself if running outside Docker:
    `apt-get install tesseract-ocr poppler-utils` on Debian/Ubuntu).
- **`parser.py`** — feeds the extracted text to the same `get_structured_llm()`
  helper the orchestrator uses (so it gets Groq/OpenRouter fallback for free)
  with a Pydantic schema: `name`, `email`, `profile`, `designation`, `skills`.
  Email is cross-checked with a regex fallback in case the LLM misses it.
- **`confirmation.py`** — builds the "I got name=X, email=Y..." confirmation
  message, noting which fields were previously `NULL` ("recommended") vs.
  being changed from an existing value.

## SQLite profile store (`db/database.py`)

A `users` table, separate from LangGraph's own conversation checkpointer:

| Column | Notes |
|---|---|
| `telegram_id` | unique, used as the row key |
| `username` | the person's *name* (not their Telegram `@handle`) |
| `email` | |
| `profile` | e.g. "Backend Developer" — NULL until known |
| `designation` | target job title — NULL until known |
| `skills` | JSON list, extracted from resume |
| `resume_text` | raw extracted resume text — used as agent context |
| `onboarding_stage` | `new` → `awaiting_name` → `awaiting_email` → `onboarding_complete` |
| `pending_intent` | set when a resume-gated request is waiting on an upload |
| `pending_extraction` | JSON-staged extraction awaiting ✅/✏️ confirmation |

This is the durable store (survives restarts). LangGraph's `MemorySaver`
checkpoint (message history, in-progress JD flow) is in-memory only — see
"Extending it" below for swapping in a persistent checkpointer too.

## LLM provider — Groq primary, OpenRouter free fallback

Everything routes through one switch in `config.py`:

```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" or "openrouter"
```

* Whichever you set becomes the **primary** model for the orchestrator, all 4
  agents, and the resume parser.
* The other provider is wired in as an automatic **fallback** via LangChain's
  `.with_fallbacks([...])` — if the primary call throws (rate limit, bad key,
  timeout, model deprecated, etc.) the request is silently retried on the
  fallback provider. No agent code needs to know this is happening.

| Provider | Model | Why |
|---|---|---|
| Groq | `openai/gpt-oss-120b` | Groq's current recommended high-capacity production model. `llama-3.3-70b-versatile` is being phased out (shutdown 08/16/2026). |
| OpenRouter | `openrouter/free` | OpenRouter's own router across whatever free model is currently healthy — the free-model roster rotates and gets pulled often, so pinning one `:free` id is fragile. |

Both are overridable via `GROQ_MODEL` / `OPENROUTER_MODEL` env vars.

## Setup

```bash
cd telegram_career_bot
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt

# OCR system deps (skip if running via Docker — already included there)
sudo apt-get install tesseract-ocr poppler-utils    # Debian/Ubuntu

cp .env.example .env
# then edit .env:
#   TELEGRAM_BOT_TOKEN   <- from @BotFather on Telegram
#   GROQ_API_KEY         <- from console.groq.com
#   OPENROUTER_API_KEY   <- from openrouter.ai (free, no card needed)
#   LLM_PROVIDER=groq    <- or "openrouter"

python3 bot.py
```

`/start` kicks off onboarding (or shows the menu if you're already set up),
`/profile` shows what's on file for you, `/reset` clears the in-progress
chat context (job description / intent) but **not** your stored profile.

## Running with Docker

```bash
docker build -t career-bot .
docker run --env-file .env -v $(pwd)/data:/app/data career-bot
```

(The `-v` volume mount keeps `data/bot.db` — your user profiles — outside the
container so they survive rebuilds. `docker-compose.yml` is set up the same way.
If you hit a permission error writing `bot.db` from the non-root `botuser` in
the container, run `chmod 777 data` on the host once, or drop the `USER botuser`
line in the `Dockerfile`.)

## Running the offline tests (no API keys needed)

`tests/test_graph_offline.py` stubs out the LLM calls entirely and validates
graph routing, resume gating, and the multi-turn flows without hitting Groq
or OpenRouter:

```bash
python3 tests/test_graph_offline.py
```

## Project layout

```
telegram_career_bot/
├── bot.py                      # Telegram entrypoint: onboarding wizard, document/
│                                #   photo upload handlers, confirmation callback
├── config.py                    # 🔧 GLOBAL provider switch + get_llm()/get_structured_llm()
├── utils.py                      # small shared helpers
├── data/jobs.json                 # dummy job listings dataset
├── data/bot.db                     # SQLite profile DB (created at runtime)
├── db/database.py                  # SQLite profile store (users table)
├── resume/
│   ├── extractor.py                 # PDF/DOCX/image text extraction + OCR fallback
│   ├── parser.py                     # LLM structured extraction (name/email/profile/...)
│   └── confirmation.py               # builds the "I got name=X..." confirmation text
├── tools/job_search_tool.py          # dummy tool — reads data/jobs.json
├── agents/
│   ├── job_advice_agent.py
│   ├── resume_advice_agent.py         # auto-uses db_profile.resume_text as context
│   ├── job_search_agent.py            # tool-calling agent (langchain.agents.create_agent)
│   └── job_prep_agent.py              # JD flow OR auto skills-based Q&A
├── graph/
│   ├── state.py                        # shared LangGraph state schema (+ db_profile)
│   ├── nodes.py                        # orchestrator + clarify + request_resume + gating logic
│   └── build.py                        # wires nodes + conditional routing + checkpointer
└── tests/test_graph_offline.py
```

## Extending it

- **Real job listings:** replace the body of `search_jobs()` in
  `tools/job_search_tool.py` with a call to a real job-board API.
- **Gate job_search/job_advice behind a resume too:** add their intent names
  to `RESUME_GATED_INTENTS` in `graph/nodes.py`.
- **More agents:** add a node in `graph/build.py`, add the label to
  `IntentClassification` in `graph/nodes.py`, and add it to `ROUTE_MAP`.
- **Persistent LangGraph checkpointer:** swap `MemorySaver()` in
  `graph/build.py` for `SqliteSaver`/`PostgresSaver` so chat history survives
  restarts too (the SQLite *profile* DB already does).

