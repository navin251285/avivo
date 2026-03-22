"""Application configuration."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "docs"
DB_DIR = BASE_DIR / "db"

CHROMA_COLLECTION_NAME = "rag_docs"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 120
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "4"))
