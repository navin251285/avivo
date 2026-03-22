"""Load documents from supported file types (.pdf, .md, .txt)."""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


def load_documents(docs_dir: Path) -> List[Document]:
    """Recursively load all supported files from docs_dir."""
    documents: List[Document] = []

    for path in sorted(docs_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        text = _read_file(path)
        if not text:
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={"source": str(path.relative_to(docs_dir.parent.parent))},
            )
        )

    return documents


def _read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()
