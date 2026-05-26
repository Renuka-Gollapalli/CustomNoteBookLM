# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil

# Add backend to path
import sys
sys.path.insert(0, os.path.dirname(__file__))

from ingestion import ingest_file, ingest_youtube
from processing.chunker import chunk_document
from processing.embedder import embed_texts
from processing.vector_store import get_store
from features.study_modes import answer_question
from features.exam_pack import generate_exam_pack, save_exam_pack_as_txt
from features.notebook_builder import build_notebook, save_notebook
from features.followup import get_followup_questions
from rag.llm_client import set_provider, get_provider_info   # ⭐ Groq support

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("vector_store", exist_ok=True)

def cleanup_storage():
    """Wipe all data: clears files inside uploads/outputs, clears vector store."""
    # 1. Clear Vector Store
    try:
        store = get_store()
        store.clear()
    except Exception as e:
        print(f"Error clearing vector store: {e}")

    # 2. Delete files inside folders (keep folders intact to avoid Windows PermissionError)
    for folder in ["uploads", "outputs"]:
        os.makedirs(folder, exist_ok=True)
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            try:
                if os.path.isfile(filepath) or os.path.islink(filepath):
                    os.unlink(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
            except Exception as e:
                print(f"Could not delete {filepath}: {e}")

    print("🧹 Storage cleaned up (startup/reset).")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs cleanup on startup. Modern replacement for deprecated on_event."""
    cleanup_storage()
    yield

app = FastAPI(title="OpenStudyLM API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ─── MODELS ────────────────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    mode: str = "exam"  # beginner | exam | revision
    history: list = []  # List of {"role": str, "content": str}

class YouTubeRequest(BaseModel):
    url: str

class ExamPackRequest(BaseModel):
    topics: str

class FollowUpRequest(BaseModel):
    question: str
    answer: str

class ProviderSwitchRequest(BaseModel):
    provider: str           # "ollama" | "groq"
    groq_model: str = None  # e.g. "llama3-70b-8192"
    ollama_model: str = None  # e.g. "llama3"
    api_key: str = None


# ─── FILE UPLOAD ────────────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save file
        dest = os.path.join("uploads", file.filename)
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Ingest
        raw_chunks = ingest_file(dest)
        chunked = chunk_document(raw_chunks)
        
        if not chunked:
            return {"status": "warning", "message": "No text extracted from file", "chunks": 0}
        
        # Embed and store
        texts = [c["text"] for c in chunked]
        embeddings = embed_texts(texts)
        
        store = get_store()
        store.add(embeddings, chunked)
        store.save()
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_added": len(chunked),
            "total_chunks": store.count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-youtube")
async def upload_youtube(req: YouTubeRequest):
    try:
        raw_chunks = ingest_youtube(req.url)
        chunked = chunk_document(raw_chunks)
        
        texts = [c["text"] for c in chunked]
        embeddings = embed_texts(texts)
        
        store = get_store()
        store.add(embeddings, chunked)
        store.save()
        
        return {
            "status": "success",
            "url": req.url,
            "chunks_added": len(chunked),
            "total_chunks": store.count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Q&A ────────────────────────────────────────────────────────────────────────

@app.post("/ask")
async def ask(req: QuestionRequest):
    try:
        result = answer_question(req.question, req.mode, req.history)
        
        # Get follow-up suggestions
        followups = get_followup_questions(req.question, result["answer"])
        result["followup_questions"] = followups
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── EXAM PACK ──────────────────────────────────────────────────────────────────

@app.post("/exam-pack")
async def exam_pack(req: ExamPackRequest):
    try:
        result = generate_exam_pack(req.topics)
        path = save_exam_pack_as_txt(result["content"], "exam_pack.txt")
        result["download_path"] = path
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/exam-pack")
async def download_exam_pack():
    path = "outputs/exam_pack.txt"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Exam pack not generated yet")
    return FileResponse(path, filename="exam_pack.txt")


# ─── NOTEBOOK ───────────────────────────────────────────────────────────────────

@app.post("/build-notebook")
async def notebook():
    try:
        result = build_notebook()
        path = save_notebook(result["content"], "notebook.md")
        result["download_path"] = path
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/notebook")
async def download_notebook():
    path = "outputs/notebook.md"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Notebook not built yet")
    return FileResponse(path, filename="notebook.md")


# ─── LLM PROVIDER SWITCH ────────────────────────────────────────────────────────

@app.post("/set-provider")
async def switch_provider(req: ProviderSwitchRequest):
    """Switch between Ollama (local) and Groq (cloud) at runtime."""
    if req.provider not in ("ollama", "groq"):
        raise HTTPException(status_code=400, detail="provider must be 'ollama' or 'groq'")
    
    set_provider(
        provider=req.provider,
        groq_model=req.groq_model,
        ollama_model=req.ollama_model,
        api_key=req.api_key
    )
    info = get_provider_info()
    return {"status": "switched", **info}


# ─── STATUS ─────────────────────────────────────────────────────────────────────

@app.get("/status")
async def status():
    store = get_store()
    provider_info = get_provider_info()
    return {
        "total_chunks": store.count(),
        "vector_store_ready": store.count() > 0,
        **provider_info   # includes provider, groq_model, ollama_model, groq_api_key_set
    }

@app.delete("/clear")
async def clear_store():
    cleanup_storage()
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
