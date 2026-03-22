# rag-api

Core RAG orchestrator service. Handles `/ask` requests, retrieves context from vector-db, and calls llm-service for generation.

## Configurable URLs

Update these values in [app/config.py](app/config.py):

- `VECTOR_DB_URL` (default: `http://127.0.0.1:8002`)
- `LLM_SERVICE_URL` (default: `http://127.0.0.1:8001`)

You can also override them with environment variables of the same names.

## Endpoints

- `GET /health` → service status + active dependency URLs
- `POST /retrieve` → fetch top-k chunks from vector-db
- `POST /ask-rag` → full RAG flow (retrieve first, then generate answer)
- `POST /ask` → alias of `/ask-rag`
