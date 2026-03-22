"""Optional CLI — index documents or query the vector store."""

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.chunking import hybrid_chunk
from app.config import DATA_DIR, DB_DIR
from app.loader import load_documents
from app.retriever import build_retriever, retrieve
from app.vector_store import get_vector_store, index_documents


def cmd_index(docs_dir: Path) -> None:
    documents = load_documents(docs_dir)
    if not documents:
        print(f"No documents found in: {docs_dir}")
        return
    chunks = hybrid_chunk(documents)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    count = index_documents(chunks, str(DB_DIR))
    print(f"Indexed {count} chunks into {DB_DIR}")


def cmd_query(query: str, k: int) -> None:
    store = get_vector_store(str(DB_DIR))
    retriever = build_retriever(store, k=k)
    docs = retrieve(retriever, query)
    for doc in docs:
        print(json.dumps({
            "source": doc.metadata.get("source"),
            "preview": doc.page_content[:200],
        }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Vector DB CLI")
    sub = parser.add_subparsers(dest="command")

    idx = sub.add_parser("index", help="Index documents into ChromaDB")
    idx.add_argument("--docs-dir", default=str(DATA_DIR))

    qry = sub.add_parser("query", help="Query the vector store")
    qry.add_argument("query", help="Query text")
    qry.add_argument("--k", type=int, default=4)

    args = parser.parse_args()

    if args.command == "index":
        cmd_index(Path(args.docs_dir))
    elif args.command == "query":
        cmd_query(args.query, args.k)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
