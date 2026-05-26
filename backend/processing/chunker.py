def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def chunk_document(doc_chunks: list[dict]) -> list[dict]:
    """Take raw extracted pages/segments and chunk them further."""
    result = []
    for item in doc_chunks:
        text_chunks = chunk_text(item["text"])
        for i, chunk in enumerate(text_chunks):
            result.append({
                **item,
                "text": chunk,
                "chunk_id": i
            })
    return result
