# Customer Support Augmentation

**An email support agent that answers product questions from a maintained knowledge base and hands sensitive cases to a person.**

Built for Harbor & Pine, a fictional home and outdoor store, this project connects Gmail to a two-stage AI pipeline and a React support dashboard. A customer sends a normal email; the app classifies the request, retrieves the relevant product and policy information, checks the proposed response, and replies in the same Gmail thread. Operators can inspect conversations, review processing events, and edit the knowledge base.

## Watch the demo

https://github.com/user-attachments/assets/a46d88ac-3bce-4dc3-a4e1-2327046f263f

A 73-second silent, captioned walkthrough of the real email workflow, with still inserts and waiting time removed.

[Watch or download the MP4](media/customer-support-demo.mp4) · [Walkthrough notes](media/walkthrough.md)

The demo follows a paddle-board sizing question from the customer mailbox to the integrated support mailbox, then shows the answer, ticket history, knowledge-base content, processing events, and evaluation results.

## What it does

- **Email triage:** categorizes messages into paddle boards, shelving, returns and warranty, shipping, or other.
- **Grounded replies:** a Pydantic AI agent uses `get_section` and `list_sections` to retrieve live PostgreSQL knowledge-base entries, including brand tone and escalation policy.
- **Human handoff:** attachments, refund requests, safety concerns, unsupported questions, and other escalation conditions receive an acknowledgement and the `needs-human` Gmail label. Python rules choose the next step for structured product issues.
- **Conversation history:** inbound and outbound messages are stored against the Gmail thread; answered and escalated tickets appear in the dashboard.
- **Operational visibility:** events record processing status, attempts, errors, and the structured final decision. The current Events UI displays status, attempts, errors, and creation time.
- **Editable knowledge base:** operators update product and policy entries without changing agent code.

The agent proposes a structured answer; application code decides whether to send it or substitute a handoff acknowledgement. It does not arrange shipments, replacements, refunds, or calls.

## How an email is handled

```mermaid
flowchart LR
    A[Customer email] --> B[Gmail poller]
    B --> C[Duplicate claim and mail guards]
    C --> D[Classifier]
    D --> E[Support agent]
    K[(Knowledge base)] --> E
    E --> F[Python decision rules]
    D --> F
    F --> G[Reply or human-handoff acknowledgement]
    G --> H[Gmail thread]
    G --> I[(Tickets, messages, events)]
    I --> J[React dashboard]
    J --> K
```

The classifier defaults to `openai:gpt-5-mini`; the support agent defaults to `openai:gpt-5`. Both are configurable. Retrieval loads whole named sections from PostgreSQL rather than using a vector database.

The poller selects up to ten inbox messages without the `ai-processed` label per pass. It skips sent/self-authored messages and recognized automatic or bulk mail. A `needs-human` thread stays with a person until that label is removed. Processing failures are recorded and retried on later polls, with a three-attempt label cutoff.

## Stack

| Layer | Technology |
| --- | --- |
| API and worker | Python 3.13+, FastAPI |
| AI orchestration | Pydantic AI, structured Pydantic outputs, OpenAI models |
| Email | Gmail API and OAuth refresh tokens |
| Storage | PostgreSQL / Supabase, psycopg |
| Dashboard | React, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Evaluation | Pydantic Evals, six golden email cases |

## Run locally

Use a dedicated test support mailbox: starting the worker or clicking **Check inbox now** can send real replies to unprocessed inbox messages, including older mail.

### 1. Install dependencies

```bash
uv sync
cd dashboard
npm ci
cd ..
cp .env.example .env
```

Use a current Node.js version compatible with the locked Vite dependency (Node 22.12+ is a suitable baseline).

### 2. Configure Gmail and the database

Enable the Gmail API in a Google Cloud project and configure a Desktop OAuth client. Save its downloaded client configuration as `credentials.json` in the project root. Add the support account as a test user when the OAuth consent application is in testing mode.

```bash
uv run python scripts/get_refresh_token.py
```

Authorize the support mailbox and copy the generated client ID, client secret, and refresh token into `.env`. The script prints credentials locally; keep them out of recordings and Git.

Set these values in `.env`:

| Variable | Purpose |
| --- | --- |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` | Gmail OAuth credentials (`gmail.modify` scope) |
| `OPENAI_API_KEY` | Model API access |
| `DATABASE_URL` | PostgreSQL connection string for the backend |
| `DASHBOARD_USERNAME`, `DASHBOARD_PASSWORD` | Dashboard Basic authentication; a nonempty password is required |
| `CLASSIFIER_MODEL`, `AGENT_MODEL` | Model identifiers |
| `POLL_INTERVAL_SECONDS` | Worker interval; example configuration uses 30 seconds, code default is 60 |

Apply [the schema migration](supabase/migrations/20261103124722_create_tables.sql) to a new PostgreSQL database using your database SQL editor or migration tooling. The tables enable row-level security; the backend connection needs a role permitted to access them. Then seed the knowledge base:

```bash
uv run python -m scripts.seed_knowledge_base
```

Seeding upserts by section/title and overwrites matching entry content. Dashboard edits update database rows; they do not rewrite the Markdown source files.

### 3. Start the app

Run each command in its own terminal from the repository root:

```bash
# API
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000

# Dashboard (proxies /api to port 8000)
cd dashboard && npm run dev

# Email worker — starts real inbox processing
uv run python -m app.poller
```

Open [localhost:5173](http://localhost:5173), sign in with the configured dashboard credentials, and explore **Events**, **Tickets**, and **Knowledge base**. The API is healthy when [localhost:8000/health](http://localhost:8000/health) returns `{"status":"ok"}`.

For a single-server build, run `npm run build` inside `dashboard`, then restart the API. FastAPI serves `dashboard/dist` when it exists. Use HTTPS and appropriate access controls before exposing this Basic-authenticated service beyond localhost.

## Evaluation

```bash
uv run python -m evals.run_evals
```

The evaluation invokes the live decision pipeline and reads the configured knowledge base. It requires model credentials and database access, but does not send Gmail messages. Cases cover board sizing, a slow leak after a valve check, shelf assembly, an angry refund request, replacement shipping time, and prompt injection.

Each case has two deterministic assertions: **section matches** and **action matches**. These judge routing and reply-versus-escalation decisions, not the full factual quality of the generated email.

![Recorded Pydantic Evals result](media/evaluation-summary.png)

The supplied run records **91.7% across 12 assertions (11/12)**. One assertion failed for `angry-refund`; the screenshot preserves that failure. This is a small development evaluation and a historical result, not a guarantee of future performance or an overall answer-quality score.

## Project layout

```text
app/
  ai/              Classification, support agent, schemas, decision rules
  gmail.py         Gmail API, threading, parsing, labels
  guards.py        Automatic/self-mail checks
  pipeline.py      Message processing and persistence
  poller.py        Recurring inbox worker
  db.py            PostgreSQL queries
  main.py          Authenticated API and static dashboard serving
dashboard/         React operator interface
knowledge_base/    Seed product, brand, and policy Markdown
evals/             Golden emails and section/action evaluators
scripts/           OAuth, Gmail check, knowledge-base seeding
supabase/          Database schema migration and local configuration
media/             Demo and evaluation evidence
```

## Current boundaries

This is a portfolio prototype for one support mailbox. The dashboard has one shared configured login. There is no approval queue before automatic replies, ticket reassignment interface, or refund/shipping integration. The Events API stores final decisions, but the UI does not expose a live planning or tool-call trace.

Database claims reduce duplicate processing, but Gmail sending and database writes are not one transaction: an interruption after sending can lead to incomplete records or a duplicate reply on retry. A worker interruption can also leave an event in `processing`. Model-provided classifications and issue fields can be wrong, and mail guards do not recognize every automated sender. Broader evaluations and stronger recovery controls are needed before production use.
