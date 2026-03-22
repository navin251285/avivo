"""Configuration values for the LLM service."""

# HuggingFace repo and GGUF filename for Phi-3-mini quantised model
MODEL_REPO = "microsoft/Phi-3-mini-4k-instruct-gguf"
MODEL_FILE = "Phi-3-mini-4k-instruct-q4.gguf"
MODEL_DIR = "models"
MODEL_PATH = f"{MODEL_DIR}/{MODEL_FILE}"

MAX_TOKENS = 200
