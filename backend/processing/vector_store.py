import faiss
import numpy as np
import pickle
import os

STORE_PATH = "vector_store/index.faiss"
META_PATH = "vector_store/metadata.pkl"

class VectorStore:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []  # list of dicts with source info
    
    def add(self, embeddings: np.ndarray, metadata: list[dict]):
        self.index.add(embeddings.astype("float32"))
        self.metadata.extend(metadata)
    
    def search(self, query_vec: np.ndarray, top_k: int = 5) -> list[dict]:
        if self.index.ntotal == 0:
            return []
        D, I = self.index.search(query_vec.reshape(1, -1).astype("float32"), top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.metadata):
                item = self.metadata[idx].copy()
                item["score"] = float(dist)
                results.append(item)
        return results
    
    def save(self):
        os.makedirs("vector_store", exist_ok=True)
        faiss.write_index(self.index, STORE_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(self.metadata, f)
    
    def load(self):
        if os.path.exists(STORE_PATH):
            self.index = faiss.read_index(STORE_PATH)
            with open(META_PATH, "rb") as f:
                self.metadata = pickle.load(f)
    
    def clear(self):
        self.index = faiss.IndexFlatL2(self.dim)
        self.metadata = []
        if os.path.exists(STORE_PATH):
            os.remove(STORE_PATH)
        if os.path.exists(META_PATH):
            os.remove(META_PATH)
    
    def count(self) -> int:
        return self.index.ntotal

# Singleton instance
_store = None

def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
        _store.load()
    return _store
