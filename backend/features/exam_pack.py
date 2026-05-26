from rag.retriever import retrieve, format_context
from rag.llm_client import ask_llama
from rag.prompt_templates import build_exam_pack_prompt, SYSTEM_PROMPT
import os

def generate_exam_pack(topics: str) -> dict:
    """Generate a full exam prep pack for given topics."""
    # Use topics as query to retrieve relevant content
    all_chunks = []
    for topic in topics.split(","):
        chunks = retrieve(topic.strip(), top_k=4)
        all_chunks.extend(chunks)
    
    # Deduplicate chunks
    seen_texts = set()
    unique_chunks = []
    for c in all_chunks:
        if c["text"] not in seen_texts:
            seen_texts.add(c["text"])
            unique_chunks.append(c)
    
    context = format_context(unique_chunks[:12])  # limit context
    prompt = build_exam_pack_prompt(topics, context)
    content = ask_llama(prompt, system=SYSTEM_PROMPT)
    
    return {
        "topics": topics,
        "content": content,
        "sources_used": len(unique_chunks)
    }

def save_exam_pack_as_txt(content: str, filename: str = "exam_pack.txt") -> str:
    os.makedirs("outputs", exist_ok=True)
    path = os.path.join("outputs", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
