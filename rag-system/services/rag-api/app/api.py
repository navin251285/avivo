"""RAG API - FastAPI routes."""

from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import DEFAULT_MAX_TOKENS, DEFAULT_TOP_K, LLM_SERVICE_URL, VECTOR_DB_URL
from app.rag_pipeline import answer_with_rag
from app.vector_client import fetch_matches

app = FastAPI(title="RAG API Service", version="1.0.0")


class RetrieveRequest(BaseModel):
	question: str
	k: int = Field(default=DEFAULT_TOP_K, ge=1, le=10)


class RagRequest(BaseModel):
	question: str
	user_id: str | int | None = None
	max_tokens: int = Field(default=DEFAULT_MAX_TOKENS, ge=32, le=512)
	k: int = Field(default=DEFAULT_TOP_K, ge=1, le=10)


@app.get("/health")
def health() -> dict[str, str]:
	return {
		"status": "ok",
		"vector_db_url": VECTOR_DB_URL,
		"llm_service_url": LLM_SERVICE_URL,
	}


@app.post("/retrieve")
def retrieve_context(req: RetrieveRequest) -> dict[str, Any]:
	if not req.question.strip():
		raise HTTPException(status_code=400, detail="Question cannot be empty")

	try:
		matches = fetch_matches(req.question, req.k)
	except requests.HTTPError as exc:
		status = exc.response.status_code if exc.response is not None else 502
		detail = exc.response.text if exc.response is not None else str(exc)
		raise HTTPException(status_code=status, detail=detail) from exc
	except requests.RequestException as exc:
		raise HTTPException(status_code=503, detail=f"vector-db unavailable: {exc}") from exc

	return {"question": req.question, "matches": matches}


@app.post("/ask-rag")
def ask_rag(req: RagRequest) -> dict[str, Any]:
	if not req.question.strip():
		raise HTTPException(status_code=400, detail="Question cannot be empty")

	try:
		user_id = str(req.user_id) if req.user_id is not None else None
		return answer_with_rag(req.question, max_tokens=req.max_tokens, k=req.k, user_id=user_id)
	except requests.HTTPError as exc:
		status = exc.response.status_code if exc.response is not None else 502
		detail = exc.response.text if exc.response is not None else str(exc)
		raise HTTPException(status_code=status, detail=detail) from exc
	except requests.RequestException as exc:
		raise HTTPException(status_code=503, detail=f"Dependency service unavailable: {exc}") from exc


@app.post("/ask")
def ask_alias(req: RagRequest) -> dict[str, Any]:
	"""Backward-friendly alias that runs full RAG flow."""
	return ask_rag(req)
