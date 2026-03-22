"""Retrieval helpers."""

from typing import List

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.config import RETRIEVER_K


def build_retriever(vector_store, k: int = RETRIEVER_K) -> BaseRetriever:
    """Create a similarity retriever from the vector store."""
    return vector_store.as_retriever(search_kwargs={"k": k})


def retrieve(retriever: BaseRetriever, query: str) -> List[Document]:
    """Run similarity retrieval for a query."""
    return retriever.invoke(query)
