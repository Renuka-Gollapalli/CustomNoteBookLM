from sentence_transformers import SentenceTransformer
import numpy as np

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedder()
    return model.encode(texts, show_progress_bar=False)

def embed_query(query: str) -> np.ndarray:
    return get_embedder().encode([query])[0]
