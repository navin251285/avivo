"""RAG orchestration pipeline."""

from typing import Any

from app.llm_client import ask_llm
from app.vector_client import fetch_matches


GREETING_MESSAGE = (
	"👋 Hi! I’m your HR Assistant Bot. I can help with company policies, benefits, "
	"and workplace guidelines using our employee handbook 📄 "
	"(https://resources.workable.com/wp-content/uploads/2017/09/Employee-Handbook.pdf). "
	"Please ask your HR-related question 😊"
)

UNSURE_MESSAGE = "I’m not fully sure, please check with HR for confirmation."
HANDBOOK_ONLY_MESSAGE = (
	"Sorry, I can only answer based on the Employee Handbook PDF: "
	"https://resources.workable.com/wp-content/uploads/2017/09/Employee-Handbook.pdf"
)
OUT_OF_SCOPE_MESSAGE = HANDBOOK_ONLY_MESSAGE


_seen_users: set[str] = set()

UNRELATED_KEYWORDS = {
	"cricket",
	"football",
	"world cup",
	"election",
	"politics",
	"prime minister",
	"president",
	"stock market",
	"bitcoin",
	"weather",
	"movie",
	"song",
	"recipe",
	"python code",
	"javascript",
	"programming",
	"bug fix",
}


def _build_context(matches: list[dict[str, Any]]) -> str:
	parts: list[str] = []
	for index, match in enumerate(matches, start=1):
		source = match.get("source", "unknown")
		preview = str(match.get("preview", "")).strip()
		parts.append(f"[{index}] Source: {source}\n{preview}")
	return "\n\n".join(parts)


def _clean_answer(raw: str) -> str:
	"""Normalize model output to a direct answer-only string."""
	text = raw.strip()

	cut_markers = [
		"\nQuestion:",
		"\nUser Question:",
		"\nQ:",
		"\nContext:",
		"\nEmployee Handbook Context:",
		"\n<|assistant|>",
		"\n<|user|>",
	]
	for marker in cut_markers:
		if marker in text:
			text = text.split(marker, 1)[0].strip()

	prefixes = [
		"based on the provided context",
		"based on the provided context,",
		"based on the provided employee handbook context",
		"based on the provided employee handbook context,",
		"based on the employee handbook context",
		"based on the employee handbook context,",
		"based on the employee handbook",
		"based on the employee handbook,",
		"according to the provided context",
		"according to the provided context,",
		"according to the provided employee handbook context",
		"according to the provided employee handbook context,",
		"according to the employee handbook context",
		"according to the employee handbook context,",
		"according to the employee handbook",
		"according to the employee handbook,",
		"from the provided context",
		"from the provided context,",
		"from the provided employee handbook context",
		"from the provided employee handbook context,",
		"from the employee handbook context",
		"from the employee handbook context,",
		"from the employee handbook",
		"from the employee handbook,",
	]

	lower_text = text.lower()
	for prefix in prefixes:
		if lower_text.startswith(prefix):
			text = text[len(prefix):].lstrip(" ,:")
			lower_text = text.lower()

	inline_cut_markers = ["User Question:", "Question:", "Q:"]
	for marker in inline_cut_markers:
		if marker in text:
			text = text.split(marker, 1)[0].strip()

	if text.startswith("Answer:"):
		text = text[len("Answer:"):].lstrip()

	if not text:
		return UNSURE_MESSAGE
	return text


def _is_completely_unrelated(question: str) -> bool:
	query = question.strip().lower()
	return any(keyword in query for keyword in UNRELATED_KEYWORDS)


def _is_first_interaction(user_id: str | None) -> bool:
	if not user_id:
		return False
	if user_id in _seen_users:
		return False
	_seen_users.add(user_id)
	return True


def answer_with_rag(question: str, max_tokens: int, k: int, user_id: str | None = None) -> dict[str, Any]:
	"""Retrieve top-k chunks from vector-db and generate final answer with llm-service."""
	if _is_first_interaction(user_id):
		return {
			"question": question,
			"answer": GREETING_MESSAGE,
			"matches": [],
		}

	if _is_completely_unrelated(question):
		return {
			"question": question,
			"answer": OUT_OF_SCOPE_MESSAGE,
			"matches": [],
		}

	matches = fetch_matches(question, k)
	context = _build_context(matches)
	has_context = bool(context.strip())
	answer_source = "pdf" if has_context else "none"

	if not has_context:
		return {
			"question": question,
			"answer": UNSURE_MESSAGE,
			"answer_source": answer_source,
			"matches": matches,
		}

	prompt = (
		"You are an HR Assistant Bot. "
		"You MUST answer using the provided Employee Handbook context only. "
		"If relevant context is provided, always answer from it. "
		"Do not say 'I don't know' when context exists. "
		"Only say 'I’m not fully sure, please check with HR for confirmation.' when no relevant context is available. "
		"If question is HR-related, try your best using context. "
		"If slightly unclear, still attempt answer from context. "
		"Reject only completely unrelated topics (politics, coding, sports, etc.). "
		"Keep tone clear, helpful, and concise. "
		"Start directly with the answer sentence. "
		"Never begin with phrases like 'According to the Employee Handbook', 'Based on the context', or 'From the context'. "
		"Return only the final answer text.\n\n"
		f"Employee Handbook Context:\n{context}\n\n"
		f"User Question: {question}"
	)
	answer = _clean_answer(ask_llm(prompt, max_tokens=max_tokens))
	return {
		"question": question,
		"answer": answer,
		"answer_source": answer_source,
		"matches": matches,
	}
