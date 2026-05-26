# OpenStudyLM

A Smart Multi-Source Study Assistant (CustomNotebookLM).

## Setup

1.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Outer Tools:**
    - [Ollama](https://ollama.ai/) + `ollama pull llama3`
    - [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH)
    - [ffmpeg](https://ffmpeg.org/download.html) (Add to PATH)

3.  **Setup Environment:**
    - Create `.env` file (already created)
    - Add `GROQ_API_KEY=your_key` if you want to use Groq.

## Running

1.  **Start Backend:**

    ```bash
    cd backend
    python main.py
    ```

2.  **Start Frontend:**
    ```bash
    cd frontend
    streamlit run app.py
    ```
