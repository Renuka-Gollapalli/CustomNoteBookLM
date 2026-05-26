from rag.retriever import retrieve, format_context
from rag.llm_client import ask_llama
from rag.prompt_templates import build_notebook_prompt, SYSTEM_PROMPT
from processing.vector_store import get_store
import os

def build_notebook() -> dict:
    """Build a topic-wise notebook from ALL uploaded content."""
    store = get_store()
    
    if store.count() == 0:
        return {"content": "No content uploaded yet.", "total_chunks": 0}
    
    # Sample broadly from the vector store
    # Get a diverse sample of chunks by retrieving for generic topics
    sample_queries = [
        "main topic introduction overview",
        "key concepts definitions",
        "important details examples",
        "conclusion summary findings"
    ]
    
    all_chunks = []
    seen = set()
    for q in sample_queries:
        chunks = retrieve(q, top_k=5)
        for c in chunks:
            if c["text"] not in seen:
                seen.add(c["text"])
                all_chunks.append(c)
    
    context = format_context(all_chunks[:16])
    prompt = build_notebook_prompt(context)
    notebook_content = ask_llama(prompt, system=SYSTEM_PROMPT)
    
    return {
        "content": notebook_content,
        "total_chunks": len(all_chunks)
    }

def save_notebook(content: str, filename: str = "notebook.md") -> str:
    os.makedirs("outputs", exist_ok=True)
    path = os.path.join("outputs", filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
