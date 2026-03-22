# NavRag — AI-Powered HR Assistant on Telegram

NavRag is the Telegram interface for this RAG-based HR system. It lets employees ask HR policy questions in natural language and receive concise answers grounded in the Employee Handbook PDF.

- Handbook source: https://resources.workable.com/wp-content/uploads/2017/09/Employee-Handbook.pdf
- Telegram bot username: `@NaviRagHrBot`
- Bot display name: `NavRag`

## What NavRag Does

- Accepts user questions directly in Telegram chat.
- Sends each question to the RAG API (`/ask`) endpoint.
- Uses retrieved handbook context + local LLM generation.
- Returns a clear, user-friendly HR answer in chat.

## User Experience (Based on Shared Screenshots)

### 1) Welcome and onboarding

When a user sends `/start`, NavRag responds with a greeting like:

> Hi 👋 I am your RAG assistant. Ask me anything!

This confirms the bot is active and ready to answer HR questions.

### 2) Real-time HR Q&A

In the shared conversation, NavRag answered practical HR questions such as:

- **Paid time off** question:
  - User: "Tell me about paid time off"
  - Bot: "Employees receive 20 days of paid time off (PTO)."

- **Workplace visitors policy** question:
  - User: "Tell me about workplace visitors policy"
  - Bot: "You should have visitors sign in and show identification, and they will receive passes to be returned upon completion of their visit."

These examples show the expected chat flow: ask a policy question → receive a focused handbook-based answer.

## How NavRag Connects to the RAG Stack

1. Telegram user sends a message to NavRag.
2. `telegram-bot` forwards the request to `rag-api` (`RAG_API_URL`).
3. `rag-api` retrieves relevant chunks from `vector-db`.
4. `rag-api` asks `llm-service` to generate the final answer.
5. Final answer is sent back to Telegram user.

## Run NavRag Locally

From repository root:

```bash
cd services/telegram-bot
pip install -r requirements.txt

export BOT_TOKEN="<your-telegram-bot-token>"
export RAG_API_URL="http://127.0.0.1:8000/ask"

cd app
python bot.py
```

## Notes

- Start `vector-db`, `llm-service`, and `rag-api` first.
- Ensure `RAG_API_URL` points to the running RAG API endpoint.
- Keep the bot token private and avoid committing it to Git.
