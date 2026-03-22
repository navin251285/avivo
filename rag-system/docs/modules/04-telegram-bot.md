# Module 04 — telegram-bot

The `telegram-bot` module (NavRag) is the user-facing chat interface that connects Telegram users to the RAG backend.

## Purpose

- Receive user messages and commands from Telegram.
- Forward HR queries to `rag-api`.
- Return answer messages in the same chat.

## Tech Stack

- python-telegram-bot
- httpx
- python-dotenv

## Service Location

- Module root: `services/telegram-bot`
- Bot app: `services/telegram-bot/app/bot.py`

## Required Environment Variables

- `BOT_TOKEN` — Telegram bot token from BotFather.
- `RAG_API_URL` — RAG endpoint URL (example `http://127.0.0.1:8000/ask`).

The bot loads environment values from:

1. repo-level `.env` (if present)
2. current process environment

## Runtime Behavior

- `/start` command sends greeting message.
- Plain text messages are treated as user questions.
- Bot sends payload to RAG API:

```json
{ "question": "<user text>", "user_id": "<chat id>" }
```

- Bot replies with `answer` from RAG API response.

## Local Startup

### Relative path (recommended)

```bash
cd services/telegram-bot
pip install -r requirements.txt

export BOT_TOKEN="<your-telegram-bot-token>"
export RAG_API_URL="http://127.0.0.1:8000/ask"

cd app
python bot.py
```

### Jupyter-path reference

```bash
cd /home/jupyter/avivo/rag-system/services/telegram-bot/app
python bot.py
```

## Dependencies Before Starting Bot

Start backend services first:

1. `vector-db` (8002)
2. `llm-service` (8001)
3. `rag-api` (8000)

Then start `telegram-bot`.
