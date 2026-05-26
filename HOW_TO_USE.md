# 🎓 OpenStudyLM: How to Use

Welcome to **OpenStudyLM**! This is your personal AI-powered study assistant. Think of it as a smart tutor that reads your textbooks, lecture slides, and notes, and then helps you study by answering questions, creating exam packs, and organizing your knowledge.

This guide is designed for **students and faculty** to understand how the project is structured and how to run it.

---

## 🚀 How to Run the App

### Prerequisites

1.  **Install Python**: Make sure you have Python installed on your computer.
2.  **Ollama (Optional but Recommended)**: If you want to run completely offline, install [Ollama](https://ollama.com/) and run `ollama run llama3`.
3.  **Groq API Key (Optional)**: If you want faster, cloud-based results, get a free API key from [Groq](https://console.groq.com/).

### Step 1: Install Dependencies

Open your terminal (Command Prompt or PowerShell) and run:

```bash
pip install -r requirements.txt
```

### Step 2: Start the Backend (The Brain 🧠)

This is the engine that processes your files and talks to the AI.
Open a terminal and run:

```bash
python backend/main.py
```

_You should see a message saying "Application startup complete"._

### Step 3: Start the Frontend (The Interface 💻)

This is the beautiful website you interact with.
Open a **new** terminal window and run:

```bash
streamlit run frontend/app.py
```

_Your browser will automatically open to the app._

---

## 📂 Project Structure: What's Inside?

Here is a breakdown of the files and folders so you know exactly what is happening under the hood.

### **1. `frontend/` (The User Interface)**

This folder contains the code for the website you see.

- **`app.py`**: The main file for the website. It handles:
  - **Chat Page**: Where you talk to the AI.
  - **Library**: Where you upload your files.
  - **Exam Prep**: Where generated tests are shown.
  - **Style**: All the colors, buttons, and animations are defined here.

### **2. `backend/` (The Logic)**

This is where the magic happens. It's split into specialized folders:

#### 🟢 `backend/main.py` (The Commander)

- The main control center. It receives requests from the frontend (like "upload this file" or "answer this question") and tells the other parts of the system what to do.
- It handles **automatic cleanup**, ensuring your data is fresh every time you restart.

#### 🟢 `backend/ingestion/` (The Readers)

These scripts teach the AI how to read different file types:

- `pdf_loader.py`: Reads PDF textbooks.
- `docx_loader.py`: Reads Word documents.
- `pptx_loader.py`: Reads PowerPoint slides.
- `youtube_loader.py`: Transcribes YouTube videos so you can "chat" with a video!
- `audio/video/image_loader.py`: Handles other media formats.

#### 🟢 `backend/processing/` (The Organizers)

Once read, the text needs to be organized.

- `chunker.py`: Breaks long books into small, manageable "chunks" (paragraphs).
- `embedder.py`: Converts text into numbers (vectors) so the AI can understand compatibility/similarity.
- `vector_store.py`: A mini-database (ChromaDB) that stores these chunks so we can find them later.

#### 🟢 `backend/rag/` (The Thinking Engine)

RAG stands for **Retrieval-Augmented Generation**. This means "Find the info, then generate an answer."

- `retriever.py`: When you ask a question, this finds the most relevant pages from your uploaded books.
- `llm_client.py`: Connects to the AI models (Ollama or Groq) to generate the final answer.
- `prompt_templates.py`: Contains the "instructions" we give the AI (e.g., "You are a helpful tutor...").

#### 🟢 `backend/features/` (The Study Tools)

Special features for students:

- `exam_pack.py`: Generates Study Packs with MCQs, definitions, and essay questions.
- `notebook_builder.py`: Compiles all your meaningful interactions into a revision notebook.
- `study_modes.py`: Logic for different modes like "Beginner" (simple explanations) or "Exam" (technical answers).

### **3. Root Files**

- `requirements.txt`: A list of all the software libraries needed to run this project.
- `uploads/`: A temporary folder where your uploaded files sit before being processed.
- `outputs/`: Where generated Exam Packs and Notebooks are saved for you to download.

---

## 🛠️ Troubleshooting

**"Backened Offline" Error?**

- Make sure you are running `python backend/main.py` in a separate terminal window.

**"Duplicate Key" Error?**

- Click the **"✨ New Session"** button in the top right. This clears old memory and fixes most glitches.

**Slow Answers?**

- If running locally with Ollama, it depends on your computer's speed.
- Switch to **Groq** in the sidebar (using a free API key) for lightning-fast speeds.

---

_Built with ❤️ for better learning._
