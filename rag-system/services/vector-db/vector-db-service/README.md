# vector-db-service

Standalone FastAPI vector database service. Loads documents, applies hybrid chunking, generates embeddings, and persists vectors in ChromaDB.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| POST | `/index` | Load, chunk, and index docs |
| POST | `/query` | Top-k similarity retrieval |

## Run

```bash
pip install -r requirements.txt
uvicorn app.api:app --host 0.0.0.0 --port 8002 --reload
```

## Index documents

Place `.pdf`, `.md`, or `.txt` files into `data/docs/`, then:

```bash
# via API
curl -X POST http://localhost:8002/index

# via CLI
python app/main.py index
```

## Query

```bash
# via API
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What does the handbook say about overtime?", "k": 4}'

# via CLI
python app/main.py query "What does the handbook say about overtime?"
```

## Notes

- Embedding model and vector store are loaded once at startup (singleton pattern).
- Document IDs are deterministic — safe to re-index without duplicates.
- ChromaDB is persisted in `db/`.
