from rag.retriever import retrieve, format_context
from rag.llm_client import ask_llama
from rag.prompt_templates import SYSTEM_PROMPT, build_qa_prompt


def answer_question(question: str, mode: str = "exam", history: list = []) -> dict:
    """Full RAG Q&A pipeline with study mode."""
    # Retrieve relevant chunks
    chunks = retrieve(question, top_k=6)
    
    if not chunks:
        return {
            "answer": "No relevant content found. Please upload study materials first.",
            "sources": [],
            "confidence": "low",
            "chunks_used": 0
        }
    
    context = format_context(chunks)
    prompt = build_qa_prompt(question, context, mode)
    answer = ask_llama(prompt, system=SYSTEM_PROMPT, history=history)
    
    # Build source list
    sources = []
    seen = set()
    for chunk in chunks:
        src = chunk.get("source", "")
        if src not in seen:
            seen.add(src)
            sources.append({
                "file": src,
                "type": chunk.get("source_type", ""),
                "page": chunk.get("page"),
                "timestamp": chunk.get("timestamp")
            })
    
    # Confidence based on number of supporting chunks
    confidence = "high" if len(chunks) >= 4 else ("medium" if len(chunks) >= 2 else "low")
    
    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "chunks_used": len(chunks)
    }
