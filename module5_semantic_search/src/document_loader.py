from pathlib import Path

from parser import parse_markdown

POLICIES_DIR = Path("data/policies")


def load_documents():
    """
    Load all policy documents.
    """
    if not POLICIES_DIR.exists():
        raise FileNotFoundError(
            f"Policies directory not found: {POLICIES_DIR}"
        )

    documents = []

    for file_path in POLICIES_DIR.rglob("*.md"):

        metadata, content = parse_markdown(file_path)

        document = {
            "id": file_path.stem,
            "metadata": metadata,
            "content": content,
            "source_path": str(file_path),
        }

        documents.append(document)

    return documents