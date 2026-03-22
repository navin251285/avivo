# Module 03 — rag-api

The `rag-api` module orchestrates retrieval-augmented generation by combining context retrieval from `vector-db` and answer generation from `llm-service`.

## Purpose

- Accept HR questions from clients (Telegram or direct API callers).
- Retrieve semantically relevant handbook chunks.
- Build grounded prompts using retrieved context.
- Generate final answer through Phi-3 inference service.

## Tech Stack

- FastAPI
- requests
- Internal HTTP clients for dependent services

## Service Location

- Module root: `services/rag-api`
- API app: `services/rag-api/app/api.py`
- Config: `services/rag-api/app/config.py`
- Pipeline: `services/rag-api/app/rag_pipeline.py`

## Dependency Configuration

Environment variables:

- `VECTOR_DB_URL` (default `http://127.0.0.1:8002`)
- `LLM_SERVICE_URL` (default `http://127.0.0.1:8001`)
- `VECTOR_QUERY_PATH` (default `/query`)
- `LLM_ASK_PATH` (default `/ask`)

## API Endpoints

### `GET /health`

Returns service status and active dependency URLs.

### `POST /retrieve`

Retrieves context chunks only.

Request:

```json
{ "question": "leave policy", "k": 5 }
```

### `POST /ask-rag` (full pipeline)

Request:

```json
{ "question": "What is the leave policy?", "user_id": "123", "max_tokens": 400, "k": 5 }
```

Response (shape):

```json
{
  "question": "...",
  "answer": "...",
  "answer_source": "pdf",
  "matches": []
}
```

### `POST /ask` (alias)

Alias endpoint to run same full RAG flow as `/ask-rag`.

## Local Startup

### Relative path (recommended)

```bash
cd services/rag-api
pip install -r requirements.txt
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

### Jupyter-path reference

```bash
cd /home/jupyter/avivo/rag-system/services/rag-api
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

## Behavior Notes

- Returns greeting on first interaction for a user session id.
- Rejects completely unrelated queries with handbook-only guidance.
- Uses retrieved handbook context to keep answers grounded.
