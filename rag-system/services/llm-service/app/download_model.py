"""Download the Phi-3 GGUF model from HuggingFace Hub.

Run once before starting the service:
    python -m app.download_model

The model is saved to models/ and reused on every subsequent start.
"""

import os

from huggingface_hub import hf_hub_download

from app.config import MODEL_DIR, MODEL_FILE, MODEL_PATH, MODEL_REPO


def download_model(save_dir: str = MODEL_DIR) -> str:
    """Download GGUF model if not already present; return local path."""
    if os.path.exists(MODEL_PATH):
        print(f"Model already present at: {MODEL_PATH}")
        return MODEL_PATH

    os.makedirs(save_dir, exist_ok=True)
    print(f"Downloading {MODEL_FILE} from {MODEL_REPO} …")

    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        local_dir=save_dir,
        local_dir_use_symlinks=False,
    )

    print(f"\n✅ Model downloaded at: {model_path}")
    return model_path


if __name__ == "__main__":
    download_model()
