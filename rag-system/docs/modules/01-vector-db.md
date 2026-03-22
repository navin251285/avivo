# Module 01 — vector-db

The `vector-db` module is responsible for document ingestion, chunking, embedding generation, and semantic retrieval using ChromaDB.

## Purpose

- Load Employee Handbook content (PDF and supported docs).
- Split documents into retrieval-friendly chunks.
- Convert chunks into vector embeddings.
- Persist vectors in ChromaDB.
- Return top-k relevant matches for a user query.

## Tech Stack

- FastAPI
- LangChain ecosystem
- ChromaDB
- sentence-transformers (`all-MiniLM-L6-v2`)

## Service Location

- Module root: `services/vector-db/vector-db-service`
- API app: `services/vector-db/vector-db-service/app/api.py`
- Config: `services/vector-db/vector-db-service/app/config.py`

## Default Runtime Settings

- Host: `127.0.0.1`
- Port: `8002`
- Default data dir: `data/docs`
- Default DB dir: `db`
- Default retriever k: `4`

## API Endpoints

### `GET /health`

Returns index readiness status:

- `{"status": "ok"}` when retriever is ready
- `{"status": "not_indexed"}` before indexing

### `POST /index`

Indexes documents and persists vectors.

Request:

```json
{ "docs_dir": "optional/custom/path" }
```

- If `docs_dir` is omitted, service uses default `data/docs`.

Response:

```json
{ "indexed": 123 }
```

### `POST /query`

Retrieves top-k chunks for semantic similarity.

Request:

```json
{ "query": "leave policy", "k": 4 }
```

Response (shape):

```json
{
  "matches": [
    {
      "source": "employee_handbook.pdf",
      "preview": "...chunk preview...",
      "metadata": {}
    }
  ]
}
```

## Local Startup

### Relative path (recommended)

```bash
cd services/vector-db/vector-db-service
source venv/bin/activate
uvicorn app.api:app --host 127.0.0.1 --port 8002
```

### Jupyter-path reference

```bash
cd /home/jupyter/avivo/rag-system/services/vector-db/vector-db-service
source venv/bin/activate
uvicorn app.api:app --host 127.0.0.1 --port 8002
```

## Operational Checklist

1. Start service.
2. Call `POST /index` once after document updates.
3. Verify `GET /health` returns `ok`.
4. Use `POST /query` from `rag-api` integration.
