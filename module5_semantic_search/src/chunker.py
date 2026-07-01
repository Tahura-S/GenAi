from typing import List

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

SEPARATORS = [
    "\n\n",   # Paragraph
    "\n",     # Line
    ". ",     # Sentence
    " ",      # Word
]


def recursive_split(text: str, separators: List[str]) -> List[str]:
    """
    Recursively split text until every chunk is <= CHUNK_SIZE.
    """

    # Base case
    if len(text) <= CHUNK_SIZE:
        return [text.strip()]

    # No separators left
    if not separators:
        return [
            text[i:i + CHUNK_SIZE]
            for i in range(0, len(text), CHUNK_SIZE)
        ]

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
    Split one document into chunks.
    """

    raw_chunks = recursive_split(
        document["content"],
        SEPARATORS
    )

    chunks = []

    for index, chunk in enumerate(raw_chunks):
        chunks.append(
            {
                "chunk_id": f'{document["id"]}_chunk_{index + 1}',
                "document_id": document["id"],
                "content": chunk,
                "metadata": document["metadata"],
                "source_path": document["source_path"],
            }
        )

    return chunks


# from langchain_text_splitters import RecursiveCharacterTextSplitter

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200,
#     separators=["\n\n", "\n", ". ", " "],
# )

# chunks = text_splitter.split_text(text)