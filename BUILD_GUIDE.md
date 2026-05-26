# OpenStudyLM — Complete Vibe-Coding Build Guide
### Smart Multi-Source Study Assistant (Open-Source NotebookLM)
> **Stack:** Python · FastAPI · Streamlit · Ollama (LLaMA 3) · Groq API · FAISS · Whisper · Tesseract  
> **LLM Option A:** `llama3` running locally via Ollama at `http://localhost:11434`  
> **LLM Option B:** Groq API — blazing fast cloud inference (free tier available)  
> **Switch between Local and Groq at any time from the UI — no restart needed.**

---

## TABLE OF CONTENTS
1. Project Overview & Must-Have Features
2. Final Folder Structure
3. Environment Setup
4. Dependencies (requirements.txt)
5. Module-by-Module Implementation
   - 5.1 Content Ingestion (All File Types)
   - 5.2 Text Chunking & Embedding
   - 5.3 Vector Store (FAISS)
   - 5.4 RAG Pipeline + Ollama LLaMA 3
   - 5.5 Study Mode Engine
   - 5.6 Exam Prep Pack Generator
   - 5.7 Topic-Wise Notebook Builder
   - 5.8 Source Citation Tracker
   - 5.9 Confidence Indicator
   - 5.10 Follow-Up Question Suggester
6. FastAPI Backend (main.py)
7. Streamlit Frontend (app.py)
8. Prompt Templates
9. Team Responsibilities
10. Running the App
11. Demo Flow (for Viva)

---

## 1. PROJECT OVERVIEW & MUST-HAVE FEATURES

### Core Concept
OpenStudyLM lets students upload ALL their study materials (PDFs, slides, audio, video, YouTube links, images, docs) and ask questions that are answered using content from ALL sources combined — with citations, confidence scores, and exam-ready output.

### Must-Have Features (Implement These First)
| # | Feature | Wow Factor |
|---|---------|-----------|
| 1 | Multi-format ingestion (PDF, DOCX, PPTX, TXT, image, audio, video, YouTube) | Foundation |
| 2 | Cross-source RAG Q&A with citations | Core |
| 3 | Study Mode Selector (Beginner / Exam / Revision) | Differentiator |
| 4 | Exam Prep Pack Generator | Killer Feature |
| 5 | Topic-Wise Notebook Builder | Killer Feature |
| 6 | Answer Confidence Indicator | Trust Layer |
| 7 | Follow-Up Question Suggestions | Tutor Feel |

---

## 2. FINAL FOLDER STRUCTURE

```
openstudy-lm/
│
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pdf_loader.py
│   │   ├── docx_loader.py
│   │   ├── pptx_loader.py
│   │   ├── txt_loader.py
│   │   ├── image_loader.py      # OCR via Tesseract
│   │   ├── audio_loader.py      # Whisper STT
│   │   ├── video_loader.py      # ffmpeg + Whisper
│   │   └── youtube_loader.py    # yt-dlp + transcript
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   └── vector_store.py      # FAISS wrapper
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   ├── llm_client.py        # ⭐ Unified LLM client (Ollama + Groq)
│   │   └── prompt_templates.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── study_modes.py
│   │   ├── exam_pack.py
│   │   ├── notebook_builder.py
│   │   └── followup.py
│   └── utils/
│       ├── __init__.py
│       └── metadata.py
│
├── frontend/
│   └── app.py                   # Streamlit UI
│
├── uploads/                     # Temp uploaded files
├── vector_store/                # Persisted FAISS index
├── outputs/                     # Generated notes, packs
├── .env                         # ⭐ Store GROQ_API_KEY here
├── requirements.txt
└── README.md
```

---

## 3. ENVIRONMENT SETUP

### Step 1: Install Ollama & Pull LLaMA 3
```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull LLaMA 3
ollama pull llama3

# Verify it runs
ollama run llama3 "hello"
```

### Step 2: Install Tesseract (OCR)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

### Step 3: Install ffmpeg (Video Processing)
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Step 4: Create Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### Step 5: Set Up Groq API Key (for Groq mode)
```bash
# Get your FREE API key from https://console.groq.com
# Create a .env file in the project root:

echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```
> **Note:** Groq offers a **free tier** with generous rate limits. Sign up at https://console.groq.com — no credit card needed.

---

## 4. REQUIREMENTS.TXT

```txt
# Backend
fastapi==0.111.0
uvicorn==0.30.1
python-multipart==0.0.9

# Document Parsing
pymupdf==1.24.5
python-docx==1.1.2
python-pptx==0.6.23

# OCR
pytesseract==0.3.10
Pillow==10.3.0

# Audio / Video
openai-whisper==20231117
yt-dlp==2024.5.27

# Embeddings
sentence-transformers==3.0.1

# Vector Store
faiss-cpu==1.8.0
numpy==1.26.4

# LLM Clients
ollama==0.2.1          # Local LLaMA 3 via Ollama
groq==0.9.0            # ⭐ Groq cloud API

# Frontend
streamlit==1.35.0

# Utils
python-dotenv==1.0.1
pydantic==2.7.3
httpx==0.27.0
reportlab==4.2.2       # PDF export
python-docx==1.1.2     # DOCX export
```

---

## 5. MODULE-BY-MODULE IMPLEMENTATION

---

### 5.1 Content Ingestion

#### `backend/ingestion/pdf_loader.py`
```python
import fitz  # PyMuPDF

def load_pdf(file_path: str) -> list[dict]:
    """Returns list of {text, page, source}"""
    doc = fitz.open(file_path)
    chunks = []
    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            chunks.append({
                "text": text,
                "page": page_num + 1,
                "source": file_path,
                "source_type": "pdf"
            })
    return chunks
```

#### `backend/ingestion/docx_loader.py`
```python
from docx import Document

def load_docx(file_path: str) -> list[dict]:
    doc = Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return [{
        "text": full_text,
        "page": 1,
        "source": file_path,
        "source_type": "docx"
    }]
```

#### `backend/ingestion/pptx_loader.py`
```python
from pptx import Presentation

def load_pptx(file_path: str) -> list[dict]:
    prs = Presentation(file_path)
    chunks = []
    for i, slide in enumerate(prs.slides):
        text = " ".join([
            shape.text for shape in slide.shapes
            if hasattr(shape, "text") and shape.text.strip()
        ])
        if text:
            chunks.append({
                "text": text,
                "page": i + 1,
                "source": file_path,
                "source_type": "pptx"
            })
    return chunks
```

#### `backend/ingestion/txt_loader.py`
```python
def load_txt(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return [{"text": text, "page": 1, "source": file_path, "source_type": "txt"}]
```

#### `backend/ingestion/image_loader.py`
```python
import pytesseract
from PIL import Image

def load_image(file_path: str) -> list[dict]:
    img = Image.open(file_path)
    text = pytesseract.image_to_string(img).strip()
    if not text:
        return []
    return [{"text": text, "page": 1, "source": file_path, "source_type": "image"}]
```

#### `backend/ingestion/audio_loader.py`
```python
import whisper

_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")  # use "small" for better accuracy
    return _model

def load_audio(file_path: str) -> list[dict]:
    model = get_whisper_model()
    result = model.transcribe(file_path)
    segments = []
    for seg in result["segments"]:
        segments.append({
            "text": seg["text"].strip(),
            "page": None,
            "timestamp": f"{seg['start']:.1f}s - {seg['end']:.1f}s",
            "source": file_path,
            "source_type": "audio"
        })
    return segments
```

#### `backend/ingestion/video_loader.py`
```python
import subprocess
import os
from .audio_loader import load_audio

def load_video(file_path: str) -> list[dict]:
    # Extract audio from video using ffmpeg
    audio_path = file_path.rsplit(".", 1)[0] + "_audio.wav"
    subprocess.run([
        "ffmpeg", "-i", file_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path, "-y"
    ], check=True, capture_output=True)
    
    chunks = load_audio(audio_path)
    # Update source_type
    for c in chunks:
        c["source_type"] = "video"
        c["source"] = file_path
    
    os.remove(audio_path)  # cleanup
    return chunks
```

#### `backend/ingestion/youtube_loader.py`
```python
import subprocess
import os
from .audio_loader import load_audio

def load_youtube(url: str, download_dir: str = "uploads") -> list[dict]:
    audio_path = os.path.join(download_dir, "yt_audio.wav")
    
    # Download audio only using yt-dlp
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "wav",
        "--audio-quality", "0",
        "-o", audio_path,
        url
    ], check=True)
    
    chunks = load_audio(audio_path)
    for c in chunks:
        c["source_type"] = "youtube"
        c["source"] = url
    
    os.remove(audio_path)
    return chunks
```

#### `backend/ingestion/__init__.py` — Master Dispatcher
```python
import os
from .pdf_loader import load_pdf
from .docx_loader import load_docx
from .pptx_loader import load_pptx
from .txt_loader import load_txt
from .image_loader import load_image
from .audio_loader import load_audio
from .video_loader import load_video
from .youtube_loader import load_youtube

EXTENSION_MAP = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".pptx": load_pptx,
    ".txt": load_txt,
    ".png": load_image,
    ".jpg": load_image,
    ".jpeg": load_image,
    ".mp3": load_audio,
    ".wav": load_audio,
    ".mp4": load_video,
    ".mov": load_video,
}

def ingest_file(file_path: str) -> list[dict]:
    ext = os.path.splitext(file_path)[1].lower()
    loader = EXTENSION_MAP.get(ext)
    if loader is None:
        raise ValueError(f"Unsupported file type: {ext}")
    return loader(file_path)

def ingest_youtube(url: str) -> list[dict]:
    return load_youtube(url)
```

---

### 5.2 Text Chunking & Embedding

#### `backend/processing/chunker.py`
```python
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
```

#### `backend/processing/embedder.py`
```python
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
```

---

### 5.3 Vector Store

#### `backend/processing/vector_store.py`
```python
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
```

---

### 5.4 RAG Pipeline — Unified LLM Client (Ollama + Groq)

#### `backend/rag/llm_client.py`
```python
import os
import ollama
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─── GROQ MODEL OPTIONS ─────────────────────────────────────────────────────────
# These are the best free Groq models as of 2024:
# "llama3-8b-8192"         — LLaMA 3 8B  (fast, same as local)
# "llama3-70b-8192"        — LLaMA 3 70B (much smarter, still free)
# "mixtral-8x7b-32768"     — Mixtral 8x7B (great for long context)
# "gemma2-9b-it"           — Google Gemma 2 9B (lightweight)

GROQ_DEFAULT_MODEL = "llama3-70b-8192"
OLLAMA_DEFAULT_MODEL = "llama3"

# ─── LLM PROVIDER REGISTRY ──────────────────────────────────────────────────────
# This is the single place the active provider is stored.
# It is updated via set_provider() called from the FastAPI endpoint.
_provider_state = {
    "provider": "ollama",          # "ollama" | "groq"
    "groq_model": GROQ_DEFAULT_MODEL,
    "ollama_model": OLLAMA_DEFAULT_MODEL,
}

def set_provider(provider: str, groq_model: str = None, ollama_model: str = None):
    """Called by API to switch provider at runtime."""
    _provider_state["provider"] = provider
    if groq_model:
        _provider_state["groq_model"] = groq_model
    if ollama_model:
        _provider_state["ollama_model"] = ollama_model

def get_provider_info() -> dict:
    """Returns current provider state — used by /status endpoint."""
    return {
        "provider": _provider_state["provider"],
        "groq_model": _provider_state["groq_model"],
        "ollama_model": _provider_state["ollama_model"],
        "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
    }

# ─── OLLAMA BACKEND ─────────────────────────────────────────────────────────────
def _ask_ollama(prompt: str, system: str, model: str) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model=model,
        messages=messages,
        options={"temperature": 0.3, "num_predict": 1024}
    )
    return response["message"]["content"]

# ─── GROQ BACKEND ───────────────────────────────────────────────────────────────
def _ask_groq(prompt: str, system: str, model: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in .env file. "
            "Get your free key at https://console.groq.com"
        )

    client = Groq(api_key=api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content

# ─── UNIFIED PUBLIC FUNCTION ────────────────────────────────────────────────────
def ask_llama(prompt: str, system: str = None) -> str:
    """
    Unified LLM call. Routes to Ollama or Groq based on current provider state.
    All features (study modes, exam pack, notebook, follow-up) call this function.
    """
    provider = _provider_state["provider"]

    if provider == "groq":
        return _ask_groq(
            prompt=prompt,
            system=system,
            model=_provider_state["groq_model"]
        )
    else:  # default: ollama
        return _ask_ollama(
            prompt=prompt,
            system=system,
            model=_provider_state["ollama_model"]
        )
```

> **How it works:** Every feature (`study_modes`, `exam_pack`, `notebook_builder`, `followup`) calls `ask_llama()`. The provider switch is handled entirely inside `llm_client.py` — **no other files need to change.**

#### `backend/rag/retriever.py`
```python
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
```

#### `backend/rag/prompt_templates.py`
```python
SYSTEM_PROMPT = """You are OpenStudyLM, an intelligent AI study assistant.
You help students understand their study materials, answer questions clearly,
and generate exam-ready content. Always base your answers on the provided context.
Be clear, accurate, and cite sources when possible."""

def build_qa_prompt(question: str, context: str, mode: str = "exam") -> str:
    mode_instructions = {
        "beginner": "Explain in very simple terms. Use analogies. Avoid jargon.",
        "exam": "Give a structured answer with key points, definitions, and examples. Be exam-ready.",
        "revision": "Give a very short bullet-point summary. Maximum 5 bullets."
    }
    instruction = mode_instructions.get(mode, mode_instructions["exam"])
    
    return f"""CONTEXT FROM STUDY MATERIALS:
{context}

STUDENT QUESTION:
{question}

INSTRUCTION: {instruction}

Answer the question using only the context above. At the end, cite which sources you used."""

def build_exam_pack_prompt(topics: str, context: str) -> str:
    return f"""You are creating an exam preparation pack for a student.

STUDY MATERIAL CONTEXT:
{context}

TOPICS TO COVER: {topics}

Generate a complete exam preparation pack with:
1. KEY CONCEPTS (5-8 bullet points)
2. IMPORTANT DEFINITIONS (5+ terms)
3. SHORT ANSWER QUESTIONS (5 questions with answers)
4. MCQs (5 questions with 4 options each, mark correct answer)
5. LONG ANSWER QUESTIONS (2-3 essay-style questions with outline answers)

Be thorough and exam-focused."""

def build_notebook_prompt(context: str) -> str:
    return f"""Analyze the following study material and create a structured topic-wise notebook.

STUDY MATERIAL:
{context}

Create a notebook with this structure:
## TOPIC 1: [Name]
### Subtopic 1.1
[explanation]
### Subtopic 1.2
[explanation]

## TOPIC 2: [Name]
...

Cover all major topics found in the material. Be comprehensive."""

def build_followup_prompt(question: str, answer: str) -> str:
    return f"""A student asked: "{question}"
The answer given was: "{answer[:500]}..."

Suggest 3 natural follow-up questions the student should ask next to deepen their understanding.
Return ONLY the 3 questions as a numbered list, nothing else."""
```

---

### 5.5 Study Mode Engine

#### `backend/features/study_modes.py`
```python
from rag.retriever import retrieve, format_context
from rag.llm_client import ask_llama
from rag.prompt_templates import SYSTEM_PROMPT, build_qa_prompt
from processing.vector_store import get_store

def answer_question(question: str, mode: str = "exam") -> dict:
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
    answer = ask_llama(prompt, system=SYSTEM_PROMPT)
    
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
```

---

### 5.6 Exam Prep Pack Generator

#### `backend/features/exam_pack.py`
```python
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
```

---

### 5.7 Topic-Wise Notebook Builder

#### `backend/features/notebook_builder.py`
```python
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
```

---

### 5.8 Follow-Up Suggestions

#### `backend/features/followup.py`
```python
from rag.llm_client import ask_llama
from rag.prompt_templates import build_followup_prompt

def get_followup_questions(question: str, answer: str) -> list[str]:
    prompt = build_followup_prompt(question, answer)
    response = ask_llama(prompt)
    
    # Parse numbered list
    lines = [l.strip() for l in response.split("\n") if l.strip()]
    questions = []
    for line in lines:
        # Remove numbering like "1." "1)" etc.
        if line and line[0].isdigit():
            cleaned = line.split(".", 1)[-1].strip()
            cleaned = cleaned.split(")", 1)[-1].strip()
            if cleaned:
                questions.append(cleaned)
    
    return questions[:3]  # max 3
```

---

## 6. FASTAPI BACKEND (main.py)

```python
# backend/main.py
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

app = FastAPI(title="OpenStudyLM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("vector_store", exist_ok=True)


# ─── MODELS ────────────────────────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    mode: str = "exam"  # beginner | exam | revision

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
        result = answer_question(req.question, req.mode)
        
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
        ollama_model=req.ollama_model
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
    store = get_store()
    store.clear()
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 7. STREAMLIT FRONTEND (frontend/app.py)

```python
# frontend/app.py
import streamlit as st
import requests
import os

API_URL = "http://localhost:8000"

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OpenStudyLM",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-header {font-size: 2.5rem; font-weight: bold; color: #4F46E5;}
.sub-header {color: #6B7280; font-size: 1rem; margin-top: -10px;}
.confidence-high {color: #10B981; font-weight: bold;}
.confidence-medium {color: #F59E0B; font-weight: bold;}
.confidence-low {color: #EF4444; font-weight: bold;}
.source-tag {background: #EEF2FF; padding: 3px 8px; border-radius: 4px; 
             font-size: 0.8rem; color: #4F46E5; margin-right: 5px;}
</style>
""", unsafe_allow_html=True)


# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 OpenStudyLM")
    st.caption("Your AI-powered study assistant")
    
    # ─── STATUS ──────────────────────────────────────────────────────────────────
    try:
        status = requests.get(f"{API_URL}/status").json()
        chunks = status.get("total_chunks", 0)
        provider = status.get("provider", "ollama")
        if chunks > 0:
            st.success(f"✅ {chunks} chunks indexed")
        else:
            st.warning("⚠️ No content uploaded yet")
        
        # Show active LLM badge
        if provider == "groq":
            active_model = status.get("groq_model", "llama3-70b-8192")
            st.info(f"⚡ Groq: `{active_model}`")
        else:
            active_model = status.get("ollama_model", "llama3")
            st.info(f"🖥️ Local Ollama: `{active_model}`")
    except:
        st.error("❌ Backend not running")
        status = {}
        provider = "ollama"
    
    st.divider()
    
    # ─── LLM PROVIDER SWITCHER ───────────────────────────────────────────────────
    st.markdown("### 🤖 LLM Provider")
    
    selected_provider = st.radio(
        "Choose inference backend:",
        options=["ollama", "groq"],
        format_func=lambda x: {
            "ollama": "🖥️ Local (Ollama) — Private & offline",
            "groq":   "⚡ Groq API — Fast cloud inference"
        }[x],
        index=0 if status.get("provider", "ollama") == "ollama" else 1,
        key="provider_radio"
    )
    
    groq_model_choice = None
    ollama_model_choice = None
    
    if selected_provider == "groq":
        groq_model_choice = st.selectbox(
            "Groq model:",
            options=[
                "llama3-70b-8192",
                "llama3-8b-8192",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ],
            format_func=lambda x: {
                "llama3-70b-8192":    "LLaMA 3 70B — Best quality ⭐",
                "llama3-8b-8192":     "LLaMA 3 8B  — Fastest",
                "mixtral-8x7b-32768": "Mixtral 8x7B — Long context",
                "gemma2-9b-it":       "Gemma 2 9B  — Lightweight",
            }[x],
            key="groq_model_select"
        )
        
        # Check API key
        if not status.get("groq_api_key_set"):
            st.error("⚠️ GROQ_API_KEY not set in .env!")
            st.caption("Get your free key at [console.groq.com](https://console.groq.com)")
    else:
        ollama_model_choice = st.selectbox(
            "Ollama model:",
            options=["llama3", "mistral", "phi3", "llama3:8b", "llama3:70b"],
            key="ollama_model_select"
        )
    
    if st.button("🔄 Apply Provider", type="primary", use_container_width=True):
        payload = {"provider": selected_provider}
        if groq_model_choice:
            payload["groq_model"] = groq_model_choice
        if ollama_model_choice:
            payload["ollama_model"] = ollama_model_choice
        
        resp = requests.post(f"{API_URL}/set-provider", json=payload)
        if resp.status_code == 200:
            st.success(f"✅ Switched to {selected_provider.upper()}!")
            st.rerun()
        else:
            st.error(f"❌ Switch failed: {resp.text}")
    
    st.divider()
    
    # ─── STUDY MODE ──────────────────────────────────────────────────────────────
    st.markdown("### 🎯 Study Mode")
    study_mode = st.radio(
        "Choose how you want to learn:",
        options=["beginner", "exam", "revision"],
        format_func=lambda x: {
            "beginner": "🧒 Beginner — Simple explanations",
            "exam": "🎓 Exam — Detailed & structured",
            "revision": "⚡ Revision — Quick bullet points"
        }[x],
        index=1
    )
    
    st.divider()
    
    # Upload Section
    st.markdown("### 📁 Upload Materials")
    
    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf", "docx", "pptx", "txt", "png", "jpg", "jpeg", "mp3", "wav", "mp4"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        for uf in uploaded_files:
            if st.button(f"📤 Process: {uf.name}", key=f"up_{uf.name}"):
                with st.spinner(f"Processing {uf.name}..."):
                    files = {"file": (uf.name, uf.getvalue(), uf.type)}
                    resp = requests.post(f"{API_URL}/upload", files=files)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"✅ {data['chunks_added']} chunks added!")
                    else:
                        st.error(f"❌ Error: {resp.text}")
    
    st.divider()
    
    # YouTube
    st.markdown("### 🎥 YouTube Link")
    yt_url = st.text_input("Paste YouTube URL", placeholder="https://youtube.com/watch?v=...")
    if st.button("📥 Process YouTube") and yt_url:
        with st.spinner("Downloading & transcribing..."):
            resp = requests.post(f"{API_URL}/upload-youtube", json={"url": yt_url})
            if resp.status_code == 200:
                st.success(f"✅ YouTube content indexed!")
            else:
                st.error("❌ Failed to process YouTube")
    
    st.divider()
    
    if st.button("🗑️ Clear All Content", type="secondary"):
        requests.delete(f"{API_URL}/clear")
        st.success("Cleared!")
        st.rerun()


# ─── MAIN TABS ──────────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">📚 OpenStudyLM</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your AI-powered multi-source study assistant</p>', unsafe_allow_html=True)
st.divider()

tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📝 Exam Prep Pack", "📒 Build Notebook"])


# ─── TAB 1: Q&A ─────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("### Ask anything from your study materials")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📎 Sources Used"):
                    for s in msg["sources"]:
                        src_name = os.path.basename(s.get("file", "Unknown"))
                        stype = s.get("type", "")
                        page = s.get("page")
                        ts = s.get("timestamp")
                        label = f"**{src_name}** ({stype})"
                        if page:
                            label += f" · Page {page}"
                        if ts:
                            label += f" · {ts}"
                        st.markdown(f"- {label}")
            if msg.get("confidence"):
                conf = msg["confidence"]
                color = {"high": "green", "medium": "orange", "low": "red"}[conf]
                st.markdown(f"Confidence: :{color}[**{conf.upper()}**] | Sources: {msg.get('chunks_used', 0)} chunks")
            if msg.get("followups"):
                st.markdown("**💡 You might also ask:**")
                for fq in msg["followups"]:
                    if st.button(f"→ {fq}", key=f"fq_{fq[:30]}"):
                        st.session_state.pending_question = fq
    
    # Handle click on follow-up
    if "pending_question" in st.session_state:
        question = st.session_state.pop("pending_question")
    else:
        question = st.chat_input("Ask a question about your study materials...")
    
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        
        with st.chat_message("user"):
            st.markdown(question)
        
        with st.chat_message("assistant"):
            with st.spinner("Searching through your materials..."):
                resp = requests.post(f"{API_URL}/ask", json={
                    "question": question,
                    "mode": study_mode
                })
                
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data["answer"]
                    sources = data.get("sources", [])
                    confidence = data.get("confidence", "medium")
                    chunks_used = data.get("chunks_used", 0)
                    followups = data.get("followup_questions", [])
                    
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander("📎 Sources Used"):
                            for s in sources:
                                src_name = os.path.basename(s.get("file", "Unknown"))
                                stype = s.get("type", "")
                                page = s.get("page")
                                ts = s.get("timestamp")
                                label = f"**{src_name}** ({stype})"
                                if page:
                                    label += f" · Page {page}"
                                if ts:
                                    label += f" · {ts}"
                                st.markdown(f"- {label}")
                    
                    conf_color = {"high": "green", "medium": "orange", "low": "red"}[confidence]
                    st.markdown(f"Confidence: :{conf_color}[**{confidence.upper()}**] | Sources: {chunks_used} chunks")
                    
                    if followups:
                        st.markdown("**💡 Follow-up questions:**")
                        for fq in followups:
                            st.markdown(f"→ _{fq}_")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "confidence": confidence,
                        "chunks_used": chunks_used,
                        "followups": followups
                    })
                else:
                    st.error("Failed to get answer. Make sure backend is running.")


# ─── TAB 2: EXAM PACK ───────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🎓 Generate Exam Preparation Pack")
    st.caption("Enter topics and get a complete study pack with MCQs, definitions, and long answers.")
    
    topics_input = st.text_area(
        "Topics to cover (comma-separated)",
        placeholder="e.g., Neural Networks, Backpropagation, Convolutional Neural Networks",
        height=80
    )
    
    if st.button("🚀 Generate Exam Pack", type="primary", disabled=not topics_input):
        with st.spinner("Generating exam preparation content... (this may take 1-2 minutes)"):
            resp = requests.post(f"{API_URL}/exam-pack", json={"topics": topics_input})
            
            if resp.status_code == 200:
                data = resp.json()
                st.success(f"✅ Exam pack generated! ({data.get('sources_used', 0)} source chunks used)")
                st.markdown("---")
                st.markdown(data["content"])
                
                # Download button
                dl_resp = requests.get(f"{API_URL}/download/exam-pack")
                if dl_resp.status_code == 200:
                    st.download_button(
                        "📥 Download Exam Pack",
                        data=dl_resp.content,
                        file_name="exam_pack.txt",
                        mime="text/plain"
                    )
            else:
                st.error("Failed to generate exam pack.")


# ─── TAB 3: NOTEBOOK ────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📒 Build Topic-Wise Notebook")
    st.caption("Automatically organizes all your uploaded content into a structured notebook.")
    
    if st.button("📓 Build My Notebook", type="primary"):
        with st.spinner("Building notebook from all your materials... (may take 2-3 minutes)"):
            resp = requests.post(f"{API_URL}/build-notebook")
            
            if resp.status_code == 200:
                data = resp.json()
                
                if data["total_chunks"] == 0:
                    st.warning("No content uploaded yet! Please upload study materials first.")
                else:
                    st.success(f"✅ Notebook built from {data['total_chunks']} content chunks!")
                    st.markdown("---")
                    st.markdown(data["content"])
                    
                    # Download
                    dl_resp = requests.get(f"{API_URL}/download/notebook")
                    if dl_resp.status_code == 200:
                        st.download_button(
                            "📥 Download Notebook (.md)",
                            data=dl_resp.content,
                            file_name="study_notebook.md",
                            mime="text/markdown"
                        )
            else:
                st.error("Failed to build notebook.")
```

---

## 8. COMPLETE PROMPT TEMPLATES (Reference)

All prompts are in `backend/rag/prompt_templates.py` (defined in Section 5.4).  
Here is a quick summary of the **mode-based prompting strategy**:

| Mode | Prompt Instruction |
|------|--------------------|
| `beginner` | "Explain simply, use analogies, avoid jargon" |
| `exam` | "Structured answer with definitions and examples, exam-ready" |
| `revision` | "Maximum 5 bullet points, ultra-short" |

The **system prompt** establishes OpenStudyLM's identity and forces grounding in provided context.

---

## 9. TEAM RESPONSIBILITIES

### 👩‍💻 Member 1 — Backend & AI Pipeline
**Files to own:**
- `backend/rag/` (all files)
- `backend/processing/` (all files)
- `backend/main.py`
- `backend/features/study_modes.py`

**Tasks:**
- Set up Ollama + LLaMA 3 integration
- Build and test RAG pipeline
- Implement FAISS vector store
- Write and tune all prompt templates
- Test cross-source retrieval accuracy

---

### 👨‍💻 Member 2 — Data Ingestion & Processing
**Files to own:**
- `backend/ingestion/` (all loaders)
- `backend/processing/chunker.py`
- `backend/features/exam_pack.py`
- `backend/features/notebook_builder.py`

**Tasks:**
- Implement all file format parsers
- Set up Whisper for audio/video
- Integrate Tesseract OCR for images
- Implement YouTube download pipeline
- Test all ingestion types end-to-end
- Build exam pack and notebook generation

---

### 👩‍🎨 Member 3 — Frontend & Features
**Files to own:**
- `frontend/app.py`
- `backend/features/followup.py`

**Tasks:**
- Build entire Streamlit UI
- Implement study mode selector
- Display citations and confidence scores
- Implement download buttons
- Build follow-up question display
- Do end-to-end UX testing
- Prepare demo flow for viva

---

## 10. RUNNING THE APP

### Terminal 1 — Start Ollama
```bash
ollama serve
# In another terminal:
ollama run llama3
```

### Terminal 2 — Start Backend
```bash
cd openstudy-lm/backend
source ../venv/bin/activate
python main.py
# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Terminal 3 — Start Frontend
```bash
cd openstudy-lm/frontend
source ../venv/bin/activate
streamlit run app.py
# Opens at http://localhost:8501
```

---

## 11. DEMO FLOW (For Viva)

### Recommended Demo Sequence (5 minutes)

**Step 1** — Upload 2-3 materials
- Upload a PDF (lecture notes)
- Upload a PPTX (slides)
- Paste a YouTube link

**Step 2** — Show Q&A with Study Modes
- Ask: *"Explain [topic] in simple terms"* → switch to Beginner mode
- Ask same question in Exam mode → show the difference
- Point out: **citations with page numbers**, **confidence score**

**Step 3** — Generate Exam Pack
- Type 2-3 topics
- Click Generate
- Show MCQs + long answers + definitions
- Download the file

**Step 4** — Build Notebook
- Click Build Notebook
- Show structured topic organization
- Download as Markdown

**Step 5** — Viva One-liner**
> *"OpenStudyLM is a fully open-source, locally-running AI study assistant that uses Retrieval-Augmented Generation with LLaMA 3 to unify multiple study formats into one searchable knowledge base, answering questions with source citations and generating exam-ready content — completely offline, with no paid APIs."*

---

## APPENDIX A: COMMON ERRORS & FIXES

| Error | Fix |
|-------|-----|
| `ollama: connection refused` | Run `ollama serve` first |
| `tesseract not found` | Install via apt/brew, add to PATH |
| `ffmpeg not found` | Install via apt/brew |
| `faiss import error` | Install `faiss-cpu` not `faiss-gpu` |
| `whisper out of memory` | Use `model="tiny"` instead of `base` |
| Upload fails silently | Check `uploads/` folder exists |
| Empty answers | Check vector store has content: `GET /status` |
| `GROQ_API_KEY not found` | Add `GROQ_API_KEY=...` to `.env` file |
| `groq.AuthenticationError` | Wrong API key — check console.groq.com |
| Groq rate limit hit | Switch to Ollama or wait 60 seconds |

---

## APPENDIX B: OLLAMA vs GROQ — WHEN TO USE WHICH

| Factor | 🖥️ Ollama (Local) | ⚡ Groq (Cloud) |
|--------|------------------|----------------|
| Speed | Moderate (GPU-dependent) | Very fast (~500 tok/sec) |
| Privacy | 100% private | Data sent to Groq |
| Internet needed | No | Yes |
| Cost | Free forever | Free tier (generous limits) |
| Model quality | LLaMA 3 8B | LLaMA 3 70B (much smarter) |
| Best for | Privacy, offline use, demos | Better answers, low-end laptops |
| Requires setup | Ollama install + model pull | Just an API key |

### Recommended Strategy
- **Development & testing** → Use Groq (faster iteration)
- **Viva / college demo** → Use Ollama (no internet dependency)
- **Exam pack generation** → Use Groq LLaMA 3 70B (better output quality)
- **Quick Q&A in class** → Either works

---

*Built for college AI course project · LLaMA 3 + Ollama + Groq + FAISS + Whisper*
