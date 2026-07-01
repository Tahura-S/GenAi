from pathlib import Path

from parser import parse_markdown

MODULE_ROOT = Path(__file__).resolve().parent.parent
POLICIES_DIR = MODULE_ROOT / "data" / "policies"


def load_documents():
    """
    Load all policy documents.
    """
    if not POLICIES_DIR.exists():
        raise FileNotFoundError(
            f"Policies directory not found: {POLICIES_DIR}"
        )

    documents = []

    for file_path in sorted(POLICIES_DIR.rglob("*.md")):

        metadata, content = parse_markdown(file_path)

        document = {
            "id": file_path.stem,
            "metadata": metadata,
            "content": content,
            "source_path": str(file_path.relative_to(MODULE_ROOT)),
        }

        documents.append(document)

    return documents