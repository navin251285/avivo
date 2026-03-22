"""Model loading and inference helpers (llama-cpp-python / GGUF backend)."""

import os

from llama_cpp import Llama

from app.config import MAX_TOKENS, MODEL_PATH
from app.download_model import download_model

_llm: Llama | None = None


def _clean_answer(raw: str) -> str:
    """Normalize model output to direct answer text."""
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

    return text or "Not explicitly specified in the provided context."


def is_model_loaded() -> bool:
    """Return True when the Llama model is loaded in memory."""
    return _llm is not None


def load_model() -> None:
    """Download (if needed) and load the GGUF model once; keep it in memory."""
    global _llm

    if _llm is not None:
        return

    download_model()

    _llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=os.cpu_count() or 8,
        n_batch=512,
        verbose=False,
    )


def generate_text(prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Generate a response for *prompt* using the Phi-3 chat template."""
    if _llm is None:
        raise RuntimeError("Model is not loaded")

    formatted = (
        "<|system|>\n"
        "You are a helpful AI assistant. Answer in clear natural sentences.\n\n"
        "<|user|>\n"
        f"{prompt}\n\n"
        "<|assistant|>\n"
    )

    result = _llm(
        formatted,
        max_tokens=max_tokens,
        temperature=0.1,
        stop=["<|end|>"],
    )
    return _clean_answer(result["choices"][0]["text"])
