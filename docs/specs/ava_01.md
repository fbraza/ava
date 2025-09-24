# AVA — Agent Planner MVP (Backend-First)

## 1. Context

The goal is to prototype a lightweight **AI agent** that can take a natural language prompt,
decide which Slack tool to use, and execute the action. Think of it as a tiny Codex/Claude-like assistant focused on Slack.

We want to validate the **core loop**:

**prompt → AI planner → structured plan (JSON) → execute → Slack post**

Voice/STT, mobile, multi-tool orchestration will come later. This first milestone proves the agent pattern works.

---

## 2. Scope (Block 1 MVP)

- **In scope**
  - Backend in Python (FastAPI).
  - AI planner service using LLM (Claude or GPT).
  - Tool registry (start with one tool).
  - `/plan` endpoint to generate plan (no side effects).
  - `/execute` endpoint to run plan (perform action).
  - Minimal in-memory plan store.

- **Out of scope (for now)**
  - Speech-to-text, mobile UI, reminders, history reads, summaries.
  - Full DB, user management, high-availability.

---

## 3. Tech Stack

- **Language:** Python 3.11+
- **Framework:** FastAPI + Uvicorn
- **Validation:** Pydantic v2
- **AI Orchestration:** Pydantic AI (agents + tool execution)
- **Slack API:** slack_sdk
- **HTTP Client:** httpx (for AI calls)
- **AI Provider:** OpenAI or Anthropic (via Pydantic AI models)
- **Secrets:** python-dotenv for `.env`
- **Storage:** in-memory dict (later: SQLite/Postgres)
- **Dev tools:** black, ruff, pytest

---

## 4. Environment Setup

### 4.1 Slack App
1. Create a Slack app (bot user).
2. Add bot scope: `chat:write`.
3. Install to workspace, get **Bot Token** (`xoxb-...`).
4. Invite bot to test channel (e.g., `#sandbox`).

### 4.2 `.env`

```
SLACK_BOT_TOKEN=xoxb-...your-bot-token...
AI_PROVIDER=openai        # or "anthropic"
OPENAI_API_KEY=sk-...     # if provider=openai
ANTHROPIC_API_KEY=...     # if provider=anthropic
```

Install dependencies (choose provider extras):

```
pip install "pydantic-ai[openai]"  # or [anthropic]
```

---

## 5. API Contracts

### 5.1 `POST /plan`

Generate a plan from user prompt.

**Request**

```json
{ "prompt": "Post hello to #sandbox" }
```

**Response**

```json
{
  "actionId": "uuid-123",
  "plan": {
    "steps": [
      {
        "tool": "slack.chat.postMessage",
        "params": { "channel": "sandbox", "text": "hello" }
      }
    ]
  },
  "summary": "Will post 'hello' to #sandbox as the bot."
}
```

### 5.2 `POST /execute`
Execute a plan by ID.

**Request**
```json
{ "actionId": "uuid-123" }
```

**Response**

```json
{
  "status": "success",
  "outputs": {
    "permalink": "https://workspace.slack.com/archives/C123/p169000",
    "ts": "1690000000.000100",
    "channel": "C123"
  }
}
```

---

## 6. Data Structures

### 6.1 Plan Schema (Pydantic)

```python
class PlanStep(BaseModel):
    tool: Literal["slack.chat.postMessage"]
    params: dict

class Plan(BaseModel):
    steps: list[PlanStep]
```

### 6.2 Tool Params

```python
class PostMessageParams(BaseModel):
    channel: str
    text: str
```

### 6.3 Plan Store

```python
PLANS: dict[str, dict] = {}  # actionId -> { plan: Plan, executed: bool }
```

---

## 7. Tool Registry

```python
async def post_message(client, params: PostMessageParams):
    resp = client.chat_postMessage(channel=params.channel, text=params.text)
    return {"ok": resp["ok"], "ts": resp["ts"], "channel": resp["channel"], "permalink": resp["message"]["permalink"]}

TOOLS = {
  "slack.chat.postMessage": {
    "schema": PostMessageParams,
    "fn": post_message
  }
}
```

---

## 8. Planner (AI Brain)

### 8.1 Pydantic AI Agent

Use `pydantic_ai.Agent` to encapsulate prompt construction, model selection, and output validation. The agent will:

- Load the system prompt from a template.
- Call the chosen LLM through `pydantic_ai.models` (e.g., `OpenAIModel` or `AnthropicMessagesModel`).
- Produce structured output validated against the `Plan` schema using the library's `agent.run()` helpers.

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

planner_agent = Agent[
    Plan,
](
    model=OpenAIModel(model="gpt-4o-mini"),
    system_prompt="""
    You are a planning assistant. Your job is to convert user requests into tool calls.

    Available tools:
    1) slack.chat.postMessage(channel, text)

    Rules:
    - Output ONLY JSON with this schema:
      {
        "steps": [
          { "tool": "slack.chat.postMessage", "params": { "channel": "string", "text": "string" } }
        ]
      }
    - "channel" should be Slack channel name without '#'. Example: "sandbox".
    - If request cannot be mapped, output: { "steps": [] }
    """,
)

plan_result = await planner_agent.run(prompt)
plan = plan_result.data
```

### 8.2 Tool Validation & Dependencies
- Wrap Slack tool parameters as `pydantic_ai.tools.Tool` definitions so the agent understands what can be called.
- For multi-provider support, swap the `model` import (`AnthropicMessagesModel`, `AzureOpenAIModel`, etc.).
- Reuse existing Pydantic schemas (`Plan`, `PlanStep`, `PostMessageParams`) as the agent output type to keep validation centralized.

### 8.3 Example Interaction
- User: `Post hello to #sandbox`
- Agent returns `Plan(steps=[...])` ready for storage/execution.
- If no mapping is possible, Pydantic AI automatically returns validation errors that we convert into `400` responses.

---

## 9. Execution Flow

1. Client → `/plan` with natural language prompt.
2. Backend → AI (Claude/GPT) → JSON plan.
3. Backend validates plan, assigns `actionId`, stores it.
4. Client → `/execute { actionId }`.
5. Backend executes each step (Slack API call).
6. Return outputs (permalink, ts).

---

## 10. Error Handling

- 400 — Bad prompt or invalid plan.
- 404 — Unknown actionId.
- 409 — Plan already executed (idempotency).
- 422 — Plan invalid at execution.
- 502/503 — Slack API errors (rate limits).

---

## 11. Next Steps

- **Block 2:** Add second tool `slack.conversations.history`.
- **Block 3:** Add summarizer (LLM tool).
- **Block 4:** Introduce approval flow (dry-run → approve → execute).
- **Block 5:** Move plan storage to database.
- **Later:** iOS client, voice/STT, more integrations.

---

```
ava-backend/
  ├── app/
  │   ├── api/
  │   │   ├── routers/
  │   │   │   ├── plan.py
  │   │   │   └── execute.py
  │   │   └── deps.py
  │   ├── core/
  │   │   ├── config.py
  │   │   └── logging.py
  │   ├── models/
  │   │   ├── plan.py          # Plan, PlanStep, PostMessageParams
  │   │   └── execution.py
  │   ├── planner/
  │   │   ├── agent.py         # Pydantic AI Agent setup
  │   │   ├── prompts.py
  │   │   └── providers.py     # OpenAIModel, AnthropicMessagesModel helpers
  │   ├── tools/
  │   │   ├── slack/
  │   │   │   ├── client.py
  │   │   │   └── post_message.py
  │   │   └── registry.py
  │   ├── services/
  │   │   ├── planning.py      # orchestrates Agent calls + plan store
  │   │   └── execution.py
  │   ├── storage/
  │   │   └── memory.py
  │   └── main.py              # FastAPI app factory
  ├── config/
  │   └── env.example
  ├── docs/
  │   └── specs/
  │       └── ava_01.md
  ├── scripts/
  │   ├── lint.sh
  │   └── runserver.sh
  ├── tests/
  │   ├── api/
  │   ├── planner/
  │   └── tools/
  ├── pyproject.toml
  ├── requirements.txt
  └── README.md
```
