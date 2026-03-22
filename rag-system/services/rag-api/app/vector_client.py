"""HTTP client for vector-db service."""

from typing import Any

import requests

from app.config import REQUEST_TIMEOUT_SECONDS, VECTOR_DB_URL, VECTOR_QUERY_PATH


def fetch_matches(query: str, k: int) -> list[dict[str, Any]]:
	"""Call vector-db /query and return matched chunks."""
	response = requests.post(
		f"{VECTOR_DB_URL}{VECTOR_QUERY_PATH}",
		json={"query": query, "k": k},
		timeout=REQUEST_TIMEOUT_SECONDS,
	)
	response.raise_for_status()
	payload = response.json()
	return payload.get("matches", [])
