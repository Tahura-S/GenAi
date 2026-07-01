import re
from typing import List

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

SEPARATORS = [
    "\n\n",   # Paragraph
    "\n",     # Line
    ". ",     # Sentence
    " ",      # Word
]

SECTION_PATTERN = re.compile(r"(?m)^##\s+(.+)$")


def split_into_sections(content: str) -> List[dict]:
    """
    Document-aware split: break the body on markdown '## ' headers so each
    policy section (Purpose, Scope, Policy, ...) stays intact as one unit.
    """
    matches = list(SECTION_PATTERN.finditer(content))

    if not matches:
        return [{"heading": None, "text": content.strip()}]

    sections = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections.append({"heading": heading, "text": content[start:end].strip()})

    return sections


def recursive_split(text: str, separators: List[str]) -> List[str]:
    """
    Fallback for sections still bigger than CHUNK_SIZE: recursively split on
    decreasing granularity of separators until every chunk fits.
    """

    if len(text) <= CHUNK_SIZE:
        return [text.strip()] if text.strip() else []

    if not separators:
        step = CHUNK_SIZE - CHUNK_OVERLAP
        return [text[i:i + CHUNK_SIZE] for i in range(0, len(text), step)]

    separator = separators[0]
    pieces = text.split(separator)

    chunks = []
    current = ""

    for piece in pieces:

        candidate = (
            piece
            if not current
            else current + separator + piece
        )

        if len(candidate) <= CHUNK_SIZE:
            current = candidate
        else:
            if current:
                chunks.extend(
                    recursive_split(current, separators[1:])
                )
            current = piece

    if current:
        chunks.extend(
            recursive_split(current, separators[1:])
        )

    return chunks


def chunk_document(document: dict) -> List[dict]:
    """
    Chunk one document: split by markdown section first (document-aware),
    then recursively split any section still larger than CHUNK_SIZE.
    """

    sections = split_into_sections(document["content"])

    chunks = []
    chunk_index = 0

    for section in sections:
        heading = section["heading"]
        text = section["text"]

        if not text:
            continue

        pieces = (
            [text]
            if len(text) <= CHUNK_SIZE
            else recursive_split(text, SEPARATORS)
        )

        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue

            chunk_index += 1
            # Prefix the section heading so the chunk stays understandable
            # in isolation once it's embedded and retrieved out of context.
            content = f"{heading}\n{piece}" if heading else piece

            chunks.append(
                {
                    "chunk_id": f'{document["id"]}_chunk_{chunk_index}',
                    "document_id": document["id"],
                    "section": heading,
                    "content": content,
                    "metadata": document["metadata"],
                    "source_path": document["source_path"],
                }
            )

    return chunks
