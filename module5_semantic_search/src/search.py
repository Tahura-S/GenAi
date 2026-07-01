import json
from pathlib import Path

import faiss

from embedder import embed_texts

MODULE_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = MODULE_ROOT / "index"
INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.json"

TOP_K = 5
FILTERABLE_FIELDS = {"department", "document_type", "access_level"}


def load_index():
    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        raise FileNotFoundError(
            "No index found. Run `python main.py` from the "
            "module5_semantic_search folder first to build the index."
        )

    index = faiss.read_index(str(INDEX_PATH))
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return index, metadata


def parse_query(raw_query: str):
    """
    Pulls "key=value" filter tokens out of the input, e.g.
    "department=hr how many vacation days do I get" ->
    ({"department": "hr"}, "how many vacation days do I get")
    """
    filters = {}
    words = []

    for token in raw_query.split():
        if "=" in token:
            key, value = token.split("=", 1)
            key = key.strip().lower()
            if key in FILTERABLE_FIELDS:
                filters[key] = value.strip().lower()
                continue
        words.append(token)

    return filters, " ".join(words)


def matches_filters(entry: dict, filters: dict) -> bool:
    return all(
        str(entry.get(key, "")).lower() == value
        for key, value in filters.items()
    )


def search(query_text: str, filters: dict, index, metadata, top_k: int = TOP_K):
    query_vector = embed_texts([query_text])

    # Plain IndexFlatIP can't filter natively, so over-fetch candidates and
    # filter against the metadata sidecar in Python.
    fetch_k = min(len(metadata), max(top_k * 10, 50))
    scores, indices = index.search(query_vector, fetch_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        entry = metadata[idx]
        if not matches_filters(entry, filters):
            continue
        results.append((float(score), entry))
        if len(results) >= top_k:
            break

    return results


def print_results(results):
    if not results:
        print("No matching results.\n")
        return

    for rank, (score, entry) in enumerate(results, start=1):
        print(f"[{rank}] score={score:.3f} | {entry['source_path']} | section: {entry['section']}")
        print(
            f"    department={entry.get('department')} "
            f"type={entry.get('document_type')} "
            f"access={entry.get('access_level')} "
            f"effective_date={entry.get('effective_date')}"
        )
        snippet = entry["content"].replace("\n", " ")
        print(f"    {snippet[:220]}{'...' if len(snippet) > 220 else ''}")
    print()


def main():
    index, metadata = load_index()
    print(f"Loaded index with {len(metadata)} chunks.")
    print("Type a query. Optionally prefix filters, e.g.:")
    print("  department=hr how many vacation days do I get")
    print("Type 'exit' to quit.\n")

    while True:
        raw_query = input("query> ").strip()
        if raw_query.lower() in {"exit", "quit"}:
            break
        if not raw_query:
            continue

        filters, query_text = parse_query(raw_query)
        if not query_text:
            print("Please include some search text, not just filters.\n")
            continue

        results = search(query_text, filters, index, metadata)
        print_results(results)


if __name__ == "__main__":
    main()
