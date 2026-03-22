"""FastAPI application — Vector DB Service."""

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.chunking import hybrid_chunk
from app.config import DATA_DIR, DB_DIR
from app.loader import load_documents
from app.retriever import build_retriever, retrieve
from app.vector_store import get_vector_store, index_documents

app = FastAPI(title="Vector DB Service", version="1.0.0")

_store = None
_retriever = None


@app.on_event("startup")
def startup() -> None:
    """Load existing vector store once at startup (if DB already exists)."""
    global _store, _retriever
    if DB_DIR.exists() and any(DB_DIR.iterdir()):
        _store = get_vector_store(str(DB_DIR))
        _retriever = build_retriever(_store)


# ── Models ─────────────────────────────────────────────────────────────────

class IndexRequest(BaseModel):
    docs_dir: str | None = None  # defaults to data/docs/


class IndexResponse(BaseModel):
    indexed: int


class QueryRequest(BaseModel):
    query: str
    k: int = 4


class Match(BaseModel):
    source: str
    preview: str
    metadata: dict[str, Any]


class QueryResponse(BaseModel):
    matches: list[Match]


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok" if _retriever is not None else "not_indexed"}


@app.post("/index", response_model=IndexResponse)
def index(request: IndexRequest) -> IndexResponse:
    """Load documents, chunk, embed, and persist to ChromaDB."""
    global _store, _retriever

    docs_dir = Path(request.docs_dir) if request.docs_dir else DATA_DIR
    if not docs_dir.exists():
        raise HTTPException(status_code=404, detail=f"docs_dir not found: {docs_dir}")

    documents = load_documents(docs_dir)
    if not documents:
        raise HTTPException(status_code=422, detail="No supported documents found.")

    chunks = hybrid_chunk(documents)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    count = index_documents(chunks, str(DB_DIR))

    _store = get_vector_store(str(DB_DIR))
    _retriever = build_retriever(_store)

    return IndexResponse(indexed=count)


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    """Retrieve top-k matching chunks for a query."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    if _retriever is None:
        raise HTTPException(status_code=503, detail="Index not ready. POST /index first.")

    retriever = build_retriever(_store, k=request.k)
    docs = retrieve(retriever, request.query)

    return QueryResponse(
        matches=[
            Match(
                source=doc.metadata.get("source", "unknown"),
                preview=" ".join(doc.page_content.split())[:280],
                metadata=doc.metadata,
            )
            for doc in docs
        ]
    )
