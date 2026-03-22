# Avivo RAG System Architecture

This document defines the technical architecture of the Avivo HR RAG system and explains how each component works together to answer Employee Handbook questions.

- Handbook source PDF: https://resources.workable.com/wp-content/uploads/2017/09/Employee-Handbook.pdf
- Inference model: `Phi-3-mini-4k-instruct-q4.gguf`
- Vector store: ChromaDB
- APIs: FastAPI microservices
- Chat interface: Telegram bot (NavRag)

Mermaid source: [architecture-overview.mmd](docs/images/architecture-overview.mmd)

## 1) High-Level Architecture

```mermaid
flowchart TD
  U[User\nTelegram UI]

  subgraph TBOT[telegram-bot (Python bot)]
    TB1[Entry point for user]
    TB2[Receives user message]
    TB3[Calls rag-api]
    TB4[Sends response back to user]
  end

  subgraph RAG[rag-api service (Port 8000)]
    R1[Central orchestrator]
    R2[Handles greeting and prompt logic]
    R3[Receives query from telegram-bot]
    R4[Calls vector-db-service to retrieve relevant chunks]
    R5[Calls llm-service with question + retrieved chunks]
    R6[Returns final answer to telegram-bot]
  end

  subgraph VDB[vector-db-service (Port 8002)]
    V1[Chunking PDF]
    V2[Generating embeddings]
    V3[Used only for retrieval by rag-api]
  end

  subgraph LLM[llm-service (Port 8001)]
    L1[Hosts model: Phi-3-mini-4k-instruct-q4.gguf]
    L2[Loads model once\nno repeated download]
    L3[Provides inference API]
    L4[Only called by rag-api]
  end

  U -->|ask question| TB1
  TB1 --> TB2
  TB2 -->|send query| TB3
  TB3 --> R3
  R3 --> R1
  R1 --> R2
  R2 -->|retrieve relevant chunks| R4
  R4 --> V3
  V3 --> V1
  V1 --> V2
  V2 -->|return chunks| R5
  R5 -->|question + chunks| L3
  L3 --> L1
  L1 --> L2
  L2 --> L4
  L4 -->|generated answer| R6
  R6 -->|final answer| TB4
  TB4 -->|response| U

  classDef user fill:#e5e7eb,stroke:#6b7280,color:#111827;
  classDef tbot fill:#ede9fe,stroke:#7c3aed,color:#111827;
  classDef rag fill:#ffedd5,stroke:#ea580c,color:#111827;
  classDef vdb fill:#dbeafe,stroke:#2563eb,color:#111827;
  classDef llm fill:#dcfce7,stroke:#16a34a,color:#111827;

  class U user;
  class TB1,TB2,TB3,TB4 tbot;
  class R1,R2,R3,R4,R5,R6 rag;
  class V1,V2,V3 vdb;
  class L1,L2,L3,L4 llm;
```

Current behavior in `rag-api` is sequential (not parallel): it first calls `vector-db`, then calls `llm-service` after context is retrieved.

## 1.1) Actual Execution Order in Code (Current)

The current implementation order is:

1. Telegram user sends message to `telegram-bot`.
2. `telegram-bot` calls `rag-api` `POST /ask`.
3. `api.py` routes `/ask` (or `/ask-rag`) to `answer_with_rag(...)` in `rag_pipeline.py`.
4. `answer_with_rag(...)` calls `fetch_matches(...)` in `vector_client.py`.
5. `vector-db` returns top-k matches (retrieval context).
6. `answer_with_rag(...)` builds prompt from retrieved context.
7. `answer_with_rag(...)` calls `ask_llm(...)` in `llm_client.py`.
8. `llm-service` returns generated answer text.
9. `rag-api` returns response JSON to `telegram-bot`.
10. `telegram-bot` sends final message back to Telegram user.

There is no parallel fan-out from `rag-api` to `vector-db` and `llm-service` in the current code path.

`ChromaDB` is the internal vector storage engine used by the `vector-db` service. It is not a separate API hop from `rag-api`.

## 2) Component Breakdown

### A. `vector-db` service (Port 8002)

Purpose:
- Ingest and chunk handbook documents.
- Convert chunks to embeddings.
- Persist vectors in ChromaDB.
- Retrieve top-k semantically similar chunks for a query.

Key internals:
- Chunking: hybrid chunking pipeline.
- Embeddings: sentence-transformers model (`all-MiniLM-L6-v2`).
- Persistence: local Chroma DB directory.

API endpoints:
- `GET /health`: service/index status.
- `POST /index`: load docs, chunk, vectorize, persist.
- `POST /query`: retrieve relevant chunks.

### B. `llm-service` service (Port 8001)

Purpose:
- Load and serve the local GGUF model for answer generation.
- Provide generation API for downstream RAG orchestration.

Key internals:
- Runtime: `llama-cpp-python`.
- Model file: `Phi-3-mini-4k-instruct-q4.gguf`.
- Model lifecycle: downloaded once, reused from local cache (`models/`).

API endpoints:
- `GET /` and `GET /health`: service and model status.
- `POST /ask`: main text generation endpoint.
- `POST /generate`: backward-compatible alias.

### C. `rag-api` service (Port 8000)

Purpose:
- Orchestrate complete RAG flow.
- Fetch top-k context from `vector-db`.
- Build HR prompt with handbook context.
- Request final answer from `llm-service`.

Key internals:
- Dependency URLs configurable with env vars:
  - `VECTOR_DB_URL`
  - `LLM_SERVICE_URL`
- Includes answer normalization and HR-focused response behavior.

API endpoints:
- `GET /health`
- `POST /retrieve`
- `POST /ask-rag`
- `POST /ask` (alias)

### D. `telegram-bot` (NavRag)

Purpose:
- User-facing chat entry point on Telegram.
- Accept messages and `/start` command.
- Forward user question + user_id to `rag-api`.
- Return RAG answer back to the same chat.

Key runtime inputs:
- `BOT_TOKEN`
- `RAG_API_URL` (example: `http://127.0.0.1:8000/ask`)

## 3) End-to-End Data Flow

1. User asks HR question in Telegram.
2. `telegram-bot` forwards payload to `rag-api`.
3. `rag-api` calls `vector-db /query` for top-k relevant chunks.
4. `vector-db` searches ChromaDB internally and returns matched context.
5. `rag-api` composes prompt using handbook context.
6. `rag-api` calls `llm-service /ask`.
7. `llm-service` runs inference using Phi-3 GGUF.
8. `rag-api` returns final answer to `telegram-bot`.
9. Telegram bot sends answer back to the user.

This is a dependency chain (sequential): retrieval must complete before generation starts.

## 4) Why ChromaDB + Vectorization + Phi-3

- ChromaDB provides lightweight local semantic retrieval and persistence.
- Vectorization enables meaning-based search instead of keyword-only matching.
- RAG grounds responses in handbook evidence, reducing hallucinations.
- Phi-3-mini-4k-instruct-q4.gguf gives efficient local inference for API usage.

## 5) Startup Commands (Jupyter User Reference)

The following reflects your Jupyter-style startup sequence.

### 5.1 Start vector-db first

```bash
cd /home/jupyter/avivo/rag-system/services/vector-db/vector-db-service
source venv/bin/activate
uvicorn app.api:app --host 127.0.0.1 --port 8002
```

### 5.2 Start llm-service second

```bash
cd /home/jupyter/avivo/rag-system/services/llm-service
uvicorn app.api:app --host 127.0.0.1 --port 8001
```

### 5.3 Start rag-api third

```bash
cd /home/jupyter/avivo/rag-system/services/rag-api
uvicorn app.api:app --host 127.0.0.1 --port 8000
```

### 5.4 Start telegram-bot last

```bash
cd /home/jupyter/avivo/rag-system/services/telegram-bot/app
python bot.py
```

Note: For the bot command, `cd` should target the `app` directory (not `bot.py` file path).

## 6) Operational Notes

- Index documents once before asking RAG questions (`vector-db /index`).
- Keep all services running in separate terminals.
- Verify dependency URLs from `rag-api` health endpoint.
- If retrieval fails, confirm `vector-db` is indexed and reachable.
- If generation fails, confirm model is loaded in `llm-service`.
