from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed texts into normalized vectors (unit length), so cosine similarity
    equals a plain dot product -- lets us use FAISS's IndexFlatIP for
    cosine-similarity search.
    """
    model = get_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 20,
    )
    return embeddings.astype("float32")
