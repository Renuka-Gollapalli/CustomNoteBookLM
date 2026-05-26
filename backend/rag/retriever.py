from processing.embedder import embed_query
from processing.vector_store import get_store

def retrieve(query: str, top_k: int = 6) -> list[dict]:
    """Retrieve top-k relevant chunks for a query."""
    store = get_store()
    q_vec = embed_query(query)
    results = store.search(q_vec, top_k=top_k)
    return results

def format_context(chunks: list[dict]) -> str:
    """Format chunks into a context string with source labels."""
    parts = []
    for i, chunk in enumerate(chunks):
        source = chunk.get("source", "Unknown")
        page = chunk.get("page", "")
        ts = chunk.get("timestamp", "")
        label = f"[Source {i+1}: {source}"
        if page:
            label += f", Page {page}"
        if ts:
            label += f", {ts}"
        label += "]"
        parts.append(f"{label}\n{chunk['text']}")
    return "\n\n".join(parts)
