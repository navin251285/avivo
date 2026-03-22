# Module 02 — llm-service

The `llm-service` module serves local inference APIs powered by the quantized Phi-3 GGUF model.

## Purpose

- Download and cache `Phi-3-mini-4k-instruct-q4.gguf`.
- Load the model into memory at service startup.
- Expose inference APIs consumed by `rag-api`.

## Tech Stack

- FastAPI
- llama-cpp-python
- huggingface_hub

## Service Location

- Module root: `services/llm-service`
- API app: `services/llm-service/app/api.py`
- Model runtime: `services/llm-service/app/model.py`
- Download helper: `services/llm-service/app/download_model.py`

## Model Details

- Repo: `microsoft/Phi-3-mini-4k-instruct-gguf`
- File: `Phi-3-mini-4k-instruct-q4.gguf`
- Local model path: `models/Phi-3-mini-4k-instruct-q4.gguf`

## API Endpoints

### `GET /` and `GET /health`

Health endpoints that report service and model status.

### `POST /ask` (primary)

Request:

```json
{ "question": "What is probation period?", "max_tokens": 400 }
```

Response:

```json
{ "question": "...", "answer": "..." }
```

### `POST /generate` (alias)

Request:

```json
{ "prompt": "Explain leave policy", "max_tokens": 400 }
```

Response:

```json
{ "response": "..." }
```

## Local Startup

### Relative path (recommended)

```bash
cd services/llm-service
pip install -r requirements.txt
uvicorn app.api:app --host 127.0.0.1 --port 8001
```

### Jupyter-path reference

```bash
cd /home/jupyter/avivo/rag-system/services/llm-service
uvicorn app.api:app --host 127.0.0.1 --port 8001
```

## Notes

- First startup may take longer due to model download/loading.
- Later runs reuse cached model file from `models/`.
- `rag-api` calls this service via `/ask`.
