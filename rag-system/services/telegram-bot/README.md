# telegram-bot

Telegram interface for the Avivo RAG system. This module receives user messages in Telegram, forwards them to `rag-api`, and sends generated responses back to the chat.

## Role in Architecture

`telegram-bot` is the user-facing entry point:

1. User sends `/start` or a question.
2. Bot sends payload to `rag-api` (`question`, `user_id`).
3. `rag-api` performs retrieval + generation.
4. Bot returns the final answer message to the user.

Default backend target: `http://127.0.0.1:8000/ask`

## Implementation Summary

Main file: `app/bot.py`

- Uses `python-telegram-bot` for polling and handlers.
- Uses `httpx` async client to call `rag-api`.
- Loads environment values from:
	- `rag-system/.env` (if present)
	- process environment variables

Handlers:

- `/start`
	- Responds with: `Hi 👋 I am your RAG assistant. Ask me anything!`
- Text message handler
	- Sends request to `RAG_API_URL`
	- Request JSON:

```json
{
	"question": "<user message>",
	"user_id": 123456789
}
```

	- Expects JSON response with `answer` field.
	- On failure, sends a warning message with the exception text.

## Telegram UX Snapshots

The bot flow shown in project screenshots:

- [Chat snapshot 1](../../docs/images/1_hr.JPG)
- [Chat snapshot 2](../../docs/images/2_hr.JPG)

These show `/start`, HR policy question flow, and response behavior.

## How to Run

From this module directory:

```bash
pip install -r requirements.txt
cd app
python bot.py
```

Before running, set required environment variables in your shell or `.env`:

- `BOT_TOKEN` (Telegram bot token)
- `RAG_API_URL` (example: `http://127.0.0.1:8000/ask`)

Do not commit real tokens to Git.

## Dependencies

- `python-telegram-bot`
- `httpx`
- `python-dotenv`

## Integration Notes

- `rag-api` must be running and reachable.
- `vector-db` and `llm-service` should also be up for full RAG responses.
- If `rag-api` returns non-200, the bot relays an error warning to the user.

## Troubleshooting

- Bot exits with `BOT_TOKEN is not set`
	- Set `BOT_TOKEN` in environment or `.env`.

- Bot exits with `RAG_API_URL is not set`
	- Set `RAG_API_URL` correctly.

- Bot receives messages but replies with error
	- Check `rag-api` health and URL path (`/ask`).
	- Verify network reachability from bot process.

- No replies in Telegram
	- Confirm polling process is running.
	- Verify bot token matches the intended Telegram bot.
