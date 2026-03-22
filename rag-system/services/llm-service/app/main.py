"""Local smoke-test: download model + run one inference without the HTTP layer."""

from app.download_model import download_model
from app.model import generate_text, load_model


def main() -> None:
    download_model()
    load_model()
    question = "Who was the first Prime Minister of India?"
    print(f"Q: {question}")
    print(f"A: {generate_text(question)}")


if __name__ == "__main__":
    main()
