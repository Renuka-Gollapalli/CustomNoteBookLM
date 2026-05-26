# OpenStudyLM — Task Tracker
> **Project:** Smart Multi-Source Study Assistant  
> **Team:** 3 Members | **Timeline:** 4 Weeks  
> **Stack:** Python · FastAPI · Streamlit · Ollama (LLaMA 3) · FAISS · Whisper

---

## TEAM MEMBERS

| Member | Role | Owns |
|--------|------|------|
| Member 1 | Backend & AI Pipeline | RAG, LLM, Vector Store, FastAPI |
| Member 2 | Data Ingestion & Processing | All file loaders, Chunker, Exam Pack, Notebook |
| Member 3 | Frontend & Features | Streamlit UI, Follow-up, UX, Demo |

---

## WEEK 1 — Foundation & Setup

### Member 1 — Backend & AI
- [ ] Install Ollama and pull LLaMA 3 (`ollama pull llama3`)
- [ ] Verify Ollama runs at `http://localhost:11434`
- [ ] Sign up at https://console.groq.com and get a free API key
- [ ] Create `.env` file in project root with `GROQ_API_KEY=your_key_here`
- [ ] Set up Python virtual environment
- [ ] Install all dependencies from `requirements.txt` (includes `groq==0.9.0`)
- [ ] Create project folder structure as per build guide
- [ ] Write `backend/rag/llm_client.py` (unified Ollama + Groq client)
- [ ] Test Ollama call works from Python (`_ask_ollama`)
- [ ] Test Groq call works from Python (`_ask_groq`)
- [ ] Test `set_provider()` switching works at runtime
- [ ] Write `backend/processing/embedder.py` (sentence-transformers)
- [ ] Write `backend/processing/vector_store.py` (FAISS wrapper)
- [ ] Test embed + store + search pipeline with dummy text

### Member 2 — Ingestion
- [ ] Install Tesseract OCR and verify with `tesseract --version`
- [ ] Install ffmpeg and verify with `ffmpeg -version`
- [ ] Write `backend/ingestion/pdf_loader.py` and test on a sample PDF
- [ ] Write `backend/ingestion/docx_loader.py` and test
- [ ] Write `backend/ingestion/pptx_loader.py` and test
- [ ] Write `backend/ingestion/txt_loader.py` and test
- [ ] Write `backend/ingestion/image_loader.py` (Tesseract OCR) and test
- [ ] Write `backend/ingestion/__init__.py` dispatcher

### Member 3 — Frontend Setup
- [ ] Install Streamlit and verify with `streamlit hello`
- [ ] Create `frontend/app.py` with basic page layout (title, sidebar, tabs)
- [ ] Build sidebar: file uploader widget (no logic yet, just UI)
- [ ] Build sidebar: study mode radio selector
- [ ] Build Tab 1: basic chat input and message display
- [ ] Build Tab 2: topics text area and generate button placeholder
- [ ] Build Tab 3: build notebook button placeholder
- [ ] Test UI renders without errors

---

## WEEK 2 — Core Features

### Member 1 — RAG Pipeline
- [ ] Tune chunking parameters (test chunk_size 300 vs 500)
- [ ] Write `backend/processing/chunker.py` (text chunking with overlap)
- [ ] Write `backend/rag/retriever.py` (embed query → FAISS search → return chunks)
- [ ] Write `backend/rag/prompt_templates.py` (all prompt templates)
- [ ] Write `backend/features/study_modes.py` (full RAG Q&A with mode support)
- [ ] Test: upload a PDF → ask a question → get answer from Ollama (LLaMA 3)
- [ ] Test: switch to Groq → ask same question → compare output quality
- [ ] Verify source citations appear in response metadata
- [ ] Implement confidence indicator logic (based on chunk count)
- [ ] Write `backend/main.py` — `/upload`, `/ask`, `/set-provider` endpoints
- [ ] Add `POST /set-provider` endpoint (switches Ollama ↔ Groq at runtime)
- [ ] Update `GET /status` endpoint to return provider info
- [ ] Test all API endpoints with Postman or curl

### Member 2 — Advanced Ingestion
- [ ] Write `backend/ingestion/audio_loader.py` (Whisper STT) and test on MP3
- [ ] Write `backend/ingestion/video_loader.py` (ffmpeg extract + Whisper) and test
- [ ] Write `backend/ingestion/youtube_loader.py` (yt-dlp + Whisper) and test
- [ ] Add metadata (page number, timestamp, source type) to all loaders
- [ ] Integrate all loaders with `chunk_document()` from chunker
- [ ] Test end-to-end: audio file → chunks → into FAISS → answer retrieved
- [ ] Add `/upload-youtube` endpoint to `main.py`

### Member 3 — Connect UI to Backend
- [ ] Connect file uploader in sidebar to `POST /upload` API
- [ ] Show upload success/failure messages
- [ ] Connect YouTube URL input to `POST /upload-youtube` API
- [ ] Connect chat input to `POST /ask` API
- [ ] Display AI answers in chat bubbles
- [ ] Show source citations in an expandable section below each answer
- [ ] Show confidence badge (High / Medium / Low) with color coding
- [ ] Add status indicator in sidebar (chunk count + active provider from `GET /status`)
- [ ] Build LLM Provider switcher in sidebar (radio: Ollama / Groq)
- [ ] Add Groq model dropdown (appears only when Groq is selected)
- [ ] Add Ollama model dropdown (appears only when Ollama is selected)
- [ ] Wire "Apply Provider" button to `POST /set-provider`
- [ ] Show ⚠️ warning if Groq is selected but API key is not set
- [ ] Show active provider badge (🖥️ Local / ⚡ Groq) in sidebar header

---

## WEEK 3 — Stand-Out Features

### Member 1 — Polish RAG & Endpoints
- [ ] Tune chunking parameters (test chunk_size 300 vs 500)
- [ ] Improve prompt templates based on test outputs
- [ ] Add `/exam-pack` endpoint to `main.py`
- [ ] Add `/build-notebook` endpoint to `main.py`
- [ ] Add `/download/exam-pack` and `/download/notebook` endpoints
- [ ] Add `GET /status` and `DELETE /clear` endpoints
- [ ] Add error handling and proper HTTP status codes throughout
- [ ] Test full API with all endpoints using Postman

### Member 2 — Exam Pack & Notebook
- [ ] Write `backend/features/exam_pack.py` (multi-topic retrieval + LLM generation)
- [ ] Write `backend/features/notebook_builder.py` (broad sampling + structured output)
- [ ] Test exam pack generation with 2-3 topics from uploaded content
- [ ] Test notebook builder — verify it produces structured topic headers
- [ ] Implement `save_exam_pack_as_txt()` and `save_notebook()` to `outputs/` folder
- [ ] Handle edge case: no content uploaded → return clear error message

### Member 3 — Exam Pack & Notebook UI + Follow-Ups
- [ ] Write `backend/features/followup.py` (LLM-based follow-up suggestions)
- [ ] Display follow-up questions as clickable buttons below each answer
- [ ] Wire Tab 2 (Exam Pack): connect to `/exam-pack` API, display results
- [ ] Add download button for exam pack in Tab 2
- [ ] Wire Tab 3 (Notebook): connect to `/build-notebook` API, display results
- [ ] Add download button for notebook in Tab 3
- [ ] Add loading spinners with descriptive messages for all long operations
- [ ] Test full flow: upload → ask → exam pack → notebook

---

## WEEK 4 — Testing, Polish & Viva Prep

### Member 1 — Testing & Integration
- [ ] End-to-end test with PDF + PPTX + audio sources combined
- [ ] Verify cross-source answers cite multiple files
- [ ] Stress test: upload 5+ files and ask 10+ questions
- [ ] Fix any LLM response quality issues (adjust temperature, prompt wording)
- [ ] Verify vector store persists correctly across app restarts
- [ ] Write `README.md` with setup and run instructions
- [ ] Prepare architecture explanation for viva (3-4 sentences per component)

### Member 2 — Edge Cases & Demo Content
- [ ] Test with corrupted/empty files — verify graceful error messages
- [ ] Test YouTube with a real educational video
- [ ] Test image OCR with a photo of handwritten notes
- [ ] Prepare 3 demo files: one PDF, one PPTX, one YouTube link (same subject)
- [ ] Run full demo sequence and note any bugs
- [ ] Prepare explanation of ingestion pipeline for viva

### Member 3 — UI Polish & Viva Demo
- [ ] Add "Clear All Content" button with confirmation
- [ ] Test UI on different screen sizes
- [ ] Fix any UI bugs or layout issues
- [ ] Add app description / how-to-use text for first-time users
- [ ] Prepare and rehearse 5-minute demo flow (see build guide Section 11)
- [ ] Prepare viva answers for: "What is RAG?", "Why LLaMA 3?", "Why FAISS?", "How is this different from ChatGPT?"

---

## MUST-HAVE FEATURES CHECKLIST (Final Sign-Off)

| Feature | Owner | Status |
|---------|-------|--------|
| PDF ingestion | M2 | ⬜ |
| DOCX ingestion | M2 | ⬜ |
| PPTX ingestion | M2 | ⬜ |
| Image OCR ingestion | M2 | ⬜ |
| Audio (Whisper) ingestion | M2 | ⬜ |
| Video ingestion | M2 | ⬜ |
| YouTube ingestion | M2 | ⬜ |
| Text chunking + embedding | M1 | ⬜ |
| FAISS vector store | M1 | ⬜ |
| LLaMA 3 via Ollama (local) | M1 | ⬜ |
| Groq API integration | M1 | ⬜ |
| Runtime provider switch (Ollama ↔ Groq) | M1 | ⬜ |
| RAG Q&A pipeline | M1 | ⬜ |
| Beginner study mode | M1 | ⬜ |
| Exam study mode | M1 | ⬜ |
| Revision study mode | M1 | ⬜ |
| Source citations | M1 | ⬜ |
| Confidence indicator | M1 | ⬜ |
| Exam prep pack generator | M2 | ⬜ |
| Topic-wise notebook builder | M2 | ⬜ |
| Follow-up question suggestions | M3 | ⬜ |
| Streamlit UI (all 3 tabs) | M3 | ⬜ |
| LLM Provider switcher UI (sidebar) | M3 | ⬜ |
| Groq model selector UI | M3 | ⬜ |
| File download (exam pack, notebook) | M3 | ⬜ |

---

## VIVA QUICK-REFERENCE

**One-line project pitch:**
> *"OpenStudyLM is an open-source, locally-running AI study assistant that uses Retrieval-Augmented Generation with LLaMA 3 to unify multiple study formats into one searchable knowledge base, answering questions with source citations and generating exam-ready content — completely offline."*

**Key questions to prepare:**
1. What is RAG and why did you use it?
2. Why LLaMA 3 / Ollama instead of ChatGPT?
3. How does FAISS work?
4. How do you handle audio and video files?
5. What is the study mode feature and how is it implemented?
6. How is this different from basic "Chat with PDF" projects?
7. Why did you add Groq support? What is Groq?
8. How does the provider switching work at runtime without restarting the server?
9. What are the limitations of your system?
10. What would you add with more time?
