# vector-db

Vector retrieval service for the Avivo RAG stack. This module ingests handbook documents, chunks them, converts chunks to embeddings, stores vectors in ChromaDB, and returns top-k semantic matches for downstream answer generation.

## Role in Architecture

`vector-db` is the retrieval layer used by `rag-api`:

1. Documents are loaded from disk (`.pdf`, `.md`, `.txt`).
2. Text is chunked using a hybrid splitter.
3. Chunks are embedded using `sentence-transformers/all-MiniLM-L6-v2`.
4. Embeddings are persisted in a local Chroma collection (`rag_docs`).
5. At query time, the service returns top-k relevant chunks to `rag-api`.

Default runtime endpoint: `http://127.0.0.1:8002`

## Folder Layout

```text
vector-db/
	README.md
	vector-db-service/
		app/
			api.py
			config.py
			loader.py
			chunking.py
			vector_store.py
			retriever.py
			main.py
		data/docs/
		db/
		requirements.txt
```

## Core Functionality

### 1) Document loading

Implemented in `app/loader.py`:

- Recursively scans the docs folder.
- Supports `.pdf`, `.md`, `.txt`.
- PDF content is extracted with `pypdf`.
- Adds source metadata for each document.

### 2) Chunking strategy

Implemented in `app/chunking.py` using `RecursiveCharacterTextSplitter`:

- `chunk_size=400`
- `chunk_overlap=120`
- Separators: paragraph, newline, sentence break, space

This setup improves recall for policy-style content by keeping chunks focused while preserving nearby context through overlap.

Each chunk also gets a deterministic `chunk_id` in metadata for traceability.

### 3) Vectorization and storage

Implemented in `app/vector_store.py`:

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Backing store: `langchain-chroma` + `chromadb`
- Collection name: `rag_docs`
- Persistence directory: `app/db`

The service computes stable SHA-256 IDs from `(source + chunk text)` before insert, making indexing idempotent/safe to re-run.

### 4) Retrieval

Implemented in `app/retriever.py` and `app/api.py`:

- Builds a similarity retriever from Chroma.
- Default `k=4` (override in query request).
- Returns source + preview + metadata for each match.

## API Endpoints

Base URL: `http://127.0.0.1:8002`

### `GET /health`

- Returns `{"status":"ok"}` when retriever is initialized.
- Returns `{"status":"not_indexed"}` before first indexing.

### `POST /index`

Indexes all supported docs from folder.

Request body:

```json
{
	"docs_dir": "optional/path/to/docs"
}
```

- If `docs_dir` is omitted, defaults to `app/data/docs`.
- Creates/updates Chroma index.

Response:

```json
{
	"indexed": 123
}
```

### `POST /query`

Semantic retrieval from indexed chunks.

Request body:

```json
{
	"query": "What is PTO policy?",
	"k": 4
}
```

Response shape:

```json
{
	"matches": [
		{
			"source": "services/vector-db/vector-db-service/data/docs/avivo_employee_handbook.pdf",
			"preview": "Employees receive ...",
			"metadata": {
				"chunk_id": 42,
				"source": "..."
			}
		}
	]
}
```

## How to Run

From this module directory:

```bash
cd vector-db-service
pip install -r requirements.txt
uvicorn app.api:app --host 127.0.0.1 --port 8002
```

Then index once:

```bash
curl -X POST http://127.0.0.1:8002/index -H "Content-Type: application/json" -d '{}'
```

Test retrieval:

```bash
curl -X POST http://127.0.0.1:8002/query -H "Content-Type: application/json" -d '{"query":"Tell me about paid time off","k":4}'
```

## Startup Behavior

On service startup, if `app/db` already contains persisted Chroma data, the service auto-loads it and `health` becomes `ok` without re-indexing.

## Integration Contract with rag-api

- `rag-api` expects `vector-db` to be reachable and indexed.
- Typical flow:
	1. `rag-api` calls `POST /query`
	2. receives top-k matches
	3. injects match previews into LLM prompt

## Troubleshooting

- `Index not ready. POST /index first.`
	- Run `/index` once and retry.

- `No supported documents found.`
	- Ensure docs exist and use `.pdf`, `.md`, or `.txt`.

- Empty/weak matches
	- Re-index after updating docs.
	- Increase `k` in query.

- Slow indexing
	- First run downloads embedding model and builds vectors; later runs are faster due to cache/persistence.
