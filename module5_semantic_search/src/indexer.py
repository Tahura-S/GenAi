import json
from pathlib import Path

import faiss

from document_loader import load_documents
from chunker import chunk_document
from embedder import embed_texts

MODULE_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = MODULE_ROOT / "index"
INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.json"


def build_index():
    """
    Full pipeline: load documents -> chunk -> embed -> build FAISS index.

    FAISS itself has no metadata store, so we keep a parallel metadata
    sidecar (JSON list) whose order matches the vectors added to the index --
    metadata[i] describes the vector at index position i.
    """
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.")

    chunks = []
    for document in documents:
        chunks.extend(chunk_document(document))
    print(f"Split into {len(chunks)} chunks.")

    texts = [chunk["content"] for chunk in chunks]
    embeddings = embed_texts(texts)
    print(f"Embedded chunks into {embeddings.shape[1]}-dim vectors.")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    INDEX_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))

    metadata = [
        {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "section": chunk["section"],
            "content": chunk["content"],
            "source_path": chunk["source_path"],
            **chunk["metadata"],
        }
        for chunk in chunks
    ]
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2, default=str), encoding="utf-8"
    )

    print(f"Index written to {INDEX_PATH}")
    print(f"Metadata written to {METADATA_PATH}")

    return index, metadata


if __name__ == "__main__":
    build_index()
