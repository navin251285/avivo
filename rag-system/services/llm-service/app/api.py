"""FastAPI routes for the LLM service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.model import generate_text, is_model_loaded, load_model


# ── Request schemas ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    max_tokens: int = 200


class GenerateRequest(BaseModel):
    """Kept for backwards-compatibility with the rag-api /generate callers."""
    prompt: str
    max_tokens: int = 200


# ── App lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_: FastAPI):
    load_model()
    yield


app = FastAPI(title="Phi LLM Service", lifespan=lifespan)


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/")
@app.get("/health")
def health() -> dict:
    return {"status": "LLM service running", "model_loaded": is_model_loaded()}


# ── /ask  (primary endpoint) ─────────────────────────────────────────────────

@app.post("/ask")
def ask(req: QueryRequest):
    try:
        answer = generate_text(req.question, req.max_tokens)
        return {"question": req.question, "answer": answer}
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"error": str(exc)})
    except Exception:
        return JSONResponse(status_code=500, content={"error": "Failed to generate text"})


# ── /generate  (backwards-compatible alias) ──────────────────────────────────

@app.post("/generate")
def generate(payload: GenerateRequest):
    prompt = payload.prompt.strip()
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "Prompt cannot be empty"})
    try:
        text = generate_text(prompt, payload.max_tokens)
        return {"response": text}
    except RuntimeError as exc:
        return JSONResponse(status_code=503, content={"error": str(exc)})
    except Exception:
        return JSONResponse(status_code=500, content={"error": "Failed to generate text"})
