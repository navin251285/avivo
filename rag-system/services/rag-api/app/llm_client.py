"""HTTP client for llm-service."""

import requests

from app.config import LLM_ASK_PATH, LLM_SERVICE_URL, REQUEST_TIMEOUT_SECONDS


def ask_llm(question: str, max_tokens: int) -> str:
	"""Call llm-service /ask and return answer text."""
	response = requests.post(
		f"{LLM_SERVICE_URL}{LLM_ASK_PATH}",
		json={"question": question, "max_tokens": max_tokens},
		timeout=REQUEST_TIMEOUT_SECONDS,
	)
	response.raise_for_status()
	payload = response.json()
	return payload.get("answer", "")
