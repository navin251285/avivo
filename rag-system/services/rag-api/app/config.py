"""Configuration for rag-api service."""

import os


VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "http://127.0.0.1:8002")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://127.0.0.1:8001")

VECTOR_QUERY_PATH = os.getenv("VECTOR_QUERY_PATH", "/query")
LLM_ASK_PATH = os.getenv("LLM_ASK_PATH", "/ask")

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "180"))
