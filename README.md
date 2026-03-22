# Avivo RAG System (HR Assistant)

RAG-based HR assistant that answers questions from the Employee Handbook PDF:

- Source PDF: https://resources.workable.com/wp-content/uploads/2017/09/Employee-Handbook.pdf
- Architecture: 4 independent FastAPI-based modules (plus Telegram client runtime)
- Goal: keep each service independently deployable and manageable

## NavRag on Telegram

For bot-focused details and user experience (including screenshot-based chat examples), see:

- [NavRag Telegram Bot Guide](NAVRAG_TELEGRAM_BOT.md)

## Architecture

For full system design, component flow, and Jupyter-style startup commands, see:

- [Architecture Document](ARCHITECTURE.md)

![Avivo RAG Architecture Overview](docs/images/architecture-overview.svg)

## Module Documentation

Read module-level guides in this order:

1. [01 — vector-db](docs/modules/01-vector-db.md)
2. [02 — llm-service](docs/modules/02-llm-service.md)
3. [03 — rag-api](docs/modules/03-rag-api.md)
4. [04 — telegram-bot](docs/modules/04-telegram-bot.md)

## Modules

### 1) `vector-db` (port `8002`)

Responsibilities:
- Loads handbook documents
- Chunks and embeds content
- Stores vectors in Chroma DB
- Serves retrieval API for top-k matches

Main endpoints:
- `GET /health`
- `POST /index`
- `POST /query`

### 2) `llm-service` (port `8001`)

Responsibilities:
- Downloads and caches `Phi-3-mini-4k-instruct-q4.gguf`
- Loads model into memory at startup
- Exposes text generation API

Main endpoints:
- `GET /`
- `GET /health`
- `POST /ask`
- `POST /generate` (alias)

### 3) `rag-api` (port `8000`)

Responsibilities:
- Orchestrates full RAG flow
- Calls `vector-db` for retrieval and `llm-service` for generation
- Applies HR assistant prompt and response rules

Main endpoints:
- `GET /health`
- `POST /retrieve`
- `POST /ask-rag`
- `POST /ask` (alias)

### 4) `telegram-bot`

Responsibilities:
- Receives user messages from Telegram
- Forwards questions to `rag-api`
- Sends generated answers back to Telegram chat

---

## Project Structure

```text
services/
	vector-db/
		vector-db-service/
	llm-service/
	rag-api/
	telegram-bot/
```

---

## Local Run (Recommended Order)

Open separate terminals and run services in this order:

1. `vector-db`
2. `llm-service`
3. `rag-api`
4. `telegram-bot`

> Run all commands from the repository root (`rag-system`) using relative paths.

### Terminal 1 — Start `vector-db`

```bash
cd services/vector-db/vector-db-service

# If venv already exists
source venv/bin/activate

# If venv does not exist yet:
# python -m venv venv
# source venv/bin/activate
# pip install -r requirements.txt

uvicorn app.api:app --host 127.0.0.1 --port 8002
```

### Terminal 2 — Start `llm-service`

```bash
cd services/llm-service
pip install -r requirements.txt
uvicorn app.api:app --host 127.0.0.1 --port 8001
```

Notes:
- Model download happens automatically on first startup.
- Downloaded GGUF model is reused on next runs.

### Terminal 3 — Start `rag-api`

```bash
cd services/rag-api
pip install -r requirements.txt

# Optional local overrides (defaults already point to localhost)
# export VECTOR_DB_URL=http://127.0.0.1:8002
# export LLM_SERVICE_URL=http://127.0.0.1:8001

uvicorn app.api:app --host 127.0.0.1 --port 8000
```

### Terminal 4 — Start `telegram-bot`

```bash
cd services/telegram-bot
pip install -r requirements.txt

# Ensure env vars are set (BOT_TOKEN and RAG_API_URL)
# Example:
# export BOT_TOKEN="<your-telegram-bot-token>"
# export RAG_API_URL="http://127.0.0.1:8000/ask"

cd app
python bot.py
```

---

## One-Time Indexing Step (Required)

Before asking RAG questions, index your documents once:

```bash
curl -X POST "http://127.0.0.1:8002/index" \
	-H "Content-Type: application/json" \
	-d '{}'
```

Expected response:

```json
{ "indexed": 123 }
```

---

## Quick API Checks

### Check `llm-service`

```bash
curl -X POST "http://127.0.0.1:8001/ask" \
	-H "Content-Type: application/json" \
	-d '{"question":"What is probation period?","max_tokens":400}'
```

### Check `vector-db` retrieval

```bash
curl -X POST "http://127.0.0.1:8002/query" \
	-H "Content-Type: application/json" \
	-d '{"query":"leave policy","k":4}'
```

### Check full RAG flow (`rag-api`)

```bash
curl -X POST "http://127.0.0.1:8000/ask-rag" \
	-H "Content-Type: application/json" \
	-d '{"question":"What is the leave policy?","max_tokens":400,"k":5}'
```

---

## Environment Variables

### `rag-api`
- `VECTOR_DB_URL` (default: `http://127.0.0.1:8002`)
- `LLM_SERVICE_URL` (default: `http://127.0.0.1:8001`)
- `VECTOR_QUERY_PATH` (default: `/query`)
- `LLM_ASK_PATH` (default: `/ask`)

### `telegram-bot`
- `BOT_TOKEN` (required)
- `RAG_API_URL` (required, example: `http://127.0.0.1:8000/ask`)

---

## Troubleshooting

- `503 Index not ready` from `vector-db /query`:
	run `POST /index` first.
- `Dependency service unavailable` from `rag-api`:
	verify `vector-db` and `llm-service` are running on expected ports.
- Telegram bot not responding:
	check `BOT_TOKEN`, `RAG_API_URL`, and internet access for Telegram polling.
- Slow first response from `llm-service`:
	first startup downloads and initializes model; subsequent runs are faster.
