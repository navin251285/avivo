# llm-service

FastAPI microservice that serves **Phi-3-mini-4k-instruct** (quantised GGUF) via
[llama-cpp-python](https://github.com/abetlen/llama-cpp-python).  
The 2.4 GB model is downloaded **once** and cached in `models/`; every restart
reuses the cached file so there is no redundant download.

---

## Running locally

```bash
cd services/llm-service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Download model once (skips automatically if already present)
python -m app.download_model

# Start the API
uvicorn app.api:app --host 0.0.0.0 --port 8001
```

## Smoke-test without the HTTP layer

```bash
python -m app.main
```

---

## Endpoints

| Method | Path        | Description                        |
|--------|-------------|------------------------------------|
| GET    | `/`         | Health check                       |
| GET    | `/health`   | Health check (alias)               |
| POST   | `/ask`      | Primary inference endpoint         |
| POST   | `/generate` | Backwards-compatible alias         |

### POST /ask

```json
{ "question": "First Prime Minister of India", "max_tokens": 400 }
```

Response:
```json
{ "question": "...", "answer": "..." }
```

### POST /generate

```json
{ "prompt": "Explain RAG simply", "max_tokens": 400 }
```

Response:
```json
{ "response": "..." }
```

---

## Running via Docker Compose

```bash
# From the repo root
docker compose up --build llm-service
```

The `models/` directory is bind-mounted so the GGUF file survives container
restarts without being re-downloaded.

---

## Query from the command line

```bash
# From the repo root
python scripts/query_llm.py "Who invented the telephone?"
```
