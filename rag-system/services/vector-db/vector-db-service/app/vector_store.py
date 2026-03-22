"""Chroma vector store with singleton embeddings model."""

import hashlib
from typing import Iterable, List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import CHROMA_COLLECTION_NAME, EMBEDDING_MODEL_NAME

_embeddings: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return singleton embeddings model (loaded once, reused on every request)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return _embeddings


def get_vector_store(persist_directory: str) -> Chroma:
    """Return a persistent Chroma vector store."""
    return Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=persist_directory,
    )


def _stable_id(doc: Document) -> str:
    """Deterministic document ID for idempotent indexing."""
    raw = f"{doc.metadata.get('source', '')}::{doc.page_content}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def index_documents(documents: Iterable[Document], persist_directory: str) -> int:
    """Insert chunks into ChromaDB with stable IDs (safe to re-run)."""
    docs: List[Document] = list(documents)
    if not docs:
        return 0
    store = get_vector_store(persist_directory)
    store.add_documents(documents=docs, ids=[_stable_id(d) for d in docs])
    return len(docs)
