"""Improved chunking for PDF-based RAG with better recall."""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def hybrid_chunk(documents: List[Document]) -> List[Document]:
    """
    Improved chunking for PDF-based RAG:
    - Smaller chunks
    - Higher overlap
    - Better recall
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,          # 🔥 smaller chunks (was probably 800+)
        chunk_overlap=120,       # 🔥 higher overlap
        separators=[
            "\n\n", "\n", ".", " ", ""
        ],  # better semantic breaks
    )

    chunks = splitter.split_documents(documents)

    # Add chunk IDs (VERY useful for debugging + citations)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return chunks
