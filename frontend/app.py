
import streamlit as st
import requests
import os
import time

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="OpenStudyLM",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #1E293B;
        font-weight: 700;
    }
    
    /* Custom Cards */
    .stCard {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4F46E5;
    }
    
    .metric-label {
        color: #64748B;
        font-size: 0.875rem;
    }

    /* Chat Messages */
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar Cleanup */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: #DEF7EC;
        color: #03543F;
    }
    
    .status-badge.error {
        background-color: #FDE8E8;
        color: #9B1C1C;
    }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE INITIALIZATION ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
from concurrent.futures import ThreadPoolExecutor

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
@st.cache_data(ttl=5, show_spinner=False)
def get_status():
    """Cached status check to prevent UI blocking."""
    try:
        return requests.get(f"{API_URL}/status", timeout=2).json()
    except:
        return {}

def stream_text(text):
    """Generator to simulate streaming for st.write_stream"""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.01) # Faster typing effect (was 0.02)

def upload_single_file(file_obj):
    files = {"file": (file_obj.name, file_obj.getvalue(), file_obj.type)}
    try:
        requests.post(f"{API_URL}/upload", files=files)
        return True
    except:
        return False

def render_sidebar():
    with st.sidebar:
        st.markdown("## 📚 OpenStudyLM")
        st.caption("AI-powered study assistant")
        
        # 🟢 TOP STATUS INDICATOR 🟢
        status = get_status()
        if status:
            provider = status.get("provider", "ollama")
            model = status.get("groq_model" if provider == "groq" else "ollama_model", "unknown")
            st.success(f"🟢 **Online** ({status.get('total_chunks', 0)} chunks)")
            st.caption(f"Running on **{provider.title()}**")
        else:
            st.error("🔴 **Backend Offline**")
            st.warning("Ensure `backend/main.py` is running.")
        
        st.markdown("---")
        
        # Navigation
        selected_page = st.radio(
            "Navigation",
            options=["chat", "library", "exam", "notebook"],
            format_func=lambda x: {
                "chat": "💬 Study Chat",
                "library": "📁 Content Library",
                "exam": "📝 Exam Prep",
                "notebook": "📒 Notebook"
            }[x],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # LLM Provider Selection
        st.subheader("🤖 Model Selection")
        
        current_provider = status.get("provider", "ollama") if status else "ollama"
        
        new_provider = st.selectbox(
            "Provider",
            ["ollama", "groq"],
            index=0 if current_provider == "ollama" else 1,
            label_visibility="collapsed"
        )
        
        selected_model = None
        api_key = None
        
        if new_provider == "groq":
            groq_models = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "meta-llama/llama-4-scout-17b-16e-instruct",
                "openai/gpt-oss-20b",
                "qwen/qwen3-32b"
            ]
            
            # Format model names for display
            def format_model(m):
                if "llama-3.3" in m: return "🚀 Llama 3.3 70B (Versatile)"
                if "llama-3.1" in m: return "⚡ Llama 3.1 8B (Instant)"
                if "llama-4" in m: return "🧠 Llama 4 Scout (17B)"
                if "gpt-oss" in m: return "🤖 GPT-OSS (20B)"
                if "qwen3" in m: return "🐉 Qwen 3 (32B)"
                return m

            current_groq_model = status.get("groq_model", groq_models[0]) if status else groq_models[0]
            # Ensure current model is in list, else default to first
            if current_groq_model not in groq_models:
                current_groq_model = groq_models[0]
                
            selected_model = st.selectbox(
                "Model", 
                groq_models, 
                index=groq_models.index(current_groq_model),
                format_func=format_model
            )
            
            # Always allow updating API key
            api_key_set = status.get("groq_api_key_set", False) if status else False
            
            if not api_key_set:
                st.warning("⚠️ API Key required for Groq")
                api_key = st.text_input("Enter Groq API Key", type="password", placeholder="gsk_...")
            else:
                # Key exists, but allow update
                with st.expander("🔄 Update API Key"):
                    api_key = st.text_input("New API Key", type="password", placeholder="gsk_...")
                 
        else:
             selected_model = st.text_input("Model Tag", value=status.get("ollama_model", "llama3") if status else "llama3", placeholder="llama3")

        # Apply Button
        if st.button("Apply Model", type="primary", use_container_width=True):
             payload = {
                "provider": new_provider,
                "groq_model" if new_provider == "groq" else "ollama_model": selected_model
            }
             if api_key:
                payload["api_key"] = api_key
            
             try:
                 resp = requests.post(f"{API_URL}/set-provider", json=payload, timeout=5)
                 if resp.status_code == 200:
                     st.success(f"Switched to {selected_model}")
                     get_status.clear()
                     time.sleep(0.5)
                     st.rerun()
                 else:
                     st.error(f"Failed to switch: {resp.text}")
             except requests.exceptions.ConnectionError:
                 st.error("❌ Cannot connect to Backend. Is the server running?")
             except Exception as e:
                 st.error(f"An error occurred: {str(e)}")
        
        st.markdown("---")
        with st.expander("ℹ️ About"):
            st.info("OpenStudyLM turns your documents into an interactive study partner using local or cloud LLMs.")

        return selected_page

# ─── PAGE: CHAT ────────────────────────────────────────────────────────────────
def render_chat_page():
    st.title("💬 Study Chat")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("Ask questions, get explanations, and explore your study materials.")
    with col2:
         # Study Mode
         study_mode = st.selectbox(
            "Mode",
            options=["beginner", "exam", "revision"],
            format_func=lambda x: x.capitalize(),
            label_visibility="collapsed"
        )
         
         # New Session Button
         if st.button("✨ New Session", type="secondary", use_container_width=True):
             try:
                 requests.delete(f"{API_URL}/clear")
                 st.session_state.clear()
                 st.rerun()
             except Exception as e:
                 st.error(f"Failed to reset: {e}")
    
    # Chat Container
    chat_container = st.container()
    
    # Render History
    with chat_container:
        for msg_idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Sources
                if msg.get("sources"):
                    with st.expander("📚 Sources & References"):
                        for s in msg["sources"]:
                            st.markdown(f"- **{os.path.basename(s.get('file', 'Doc'))}** (Page {s.get('page', '?')})")
                
                # Follow-ups (Now clickable)
                if msg.get("followups"):
                    cols = st.columns(len(msg["followups"]))
                    for idx, fq in enumerate(msg["followups"]):
                         with cols[idx]:
                             # Use use_container_width to allow full text visibility (approximate)
                             # Use unique key based on message index and follow-up index
                             if st.button(fq, key=f"fq_{msg_idx}_{idx}", use_container_width=True):
                                  # Set as input and rerun
                                  st.session_state["pending_prompt"] = fq
                                  st.rerun()

    # Determine prompt: either from input or pending follow-up click
    prompt = st.chat_input("Ask a question about your documents...")
    
    if "pending_prompt" in st.session_state and st.session_state["pending_prompt"]:
        prompt = st.session_state["pending_prompt"]
        del st.session_state["pending_prompt"]

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Prepare history (last 10 messages for context)
                    history = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages[-6:-1] 
                        if m["role"] in ["user", "assistant"]
                    ]

                    resp = requests.post(f"{API_URL}/ask", json={
                        "question": prompt,
                        "mode": study_mode,
                        "history": history
                    })
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        answer_text = data["answer"]
                        sources = data.get("sources", [])
                        followups = data.get("followup_questions", [])

                        # Simulate streaming
                        response_stream = stream_text(answer_text)
                        st.write_stream(response_stream)
                        
                        if sources:
                            with st.expander("📚 Sources & References"):
                                for s in sources:
                                    st.markdown(f"- **{os.path.basename(s.get('file', 'Doc'))}** (Page {s.get('page', '?')})")
                        
                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": answer_text,
                            "sources": sources,
                            "followups": followups
                        })
                        
                        # Rerun to show new follow-ups
                        st.rerun() 
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")


# ─── PAGE: LIBRARY ─────────────────────────────────────────────────────────────
def render_library_page():
    st.title("📁 Content Library")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Drag & drop PDF, DOCX, or Images",
            type=["pdf", "docx", "pptx", "txt", "png", "jpg", "jpeg", "mp3", "wav", "mp4"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("🚀 Process Files", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Parallel Uploads
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {
                        executor.submit(upload_single_file, uf): uf 
                        for uf in uploaded_files
                    }
                    
                    completed = 0
                    for future in futures:
                        future.result() # Wait for completion
                        completed += 1
                        progress_bar.progress(completed / len(uploaded_files))
                        status_text.text(f"Processed {completed}/{len(uploaded_files)} files...")
                
                st.success("Files processed successfully!")
                # Clear cache to reflect new status
                get_status.clear()
                time.sleep(1)
                st.rerun()

    with col2:
        st.subheader("Add YouTube Video")
        yt_url = st.text_input("YouTube URL", placeholder="https://youtube.com/...")
        if st.button("📥 Import Video") and yt_url:
            with st.spinner("Transcribing..."):
                requests.post(f"{API_URL}/upload-youtube", json={"url": yt_url})
                st.success("Video added!")
                get_status.clear()
                st.rerun()
                
    st.markdown("---")
    st.subheader("System Status")
    
    status = get_status()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{status.get('total_chunks', 0)}</div>
            <div class="metric-label">Total Chunks</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{status.get('provider', 'Unknown').title()}</div>
            <div class="metric-label">Active Provider</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        if st.button("🗑️ Clear All Data", type="primary"):
            requests.delete(f"{API_URL}/clear")
            get_status.clear()
            st.rerun()

# ─── PAGE: EXAM PREP ───────────────────────────────────────────────────────────
def render_exam_page():
    st.title("📝 Exam Preparation")
    st.markdown("Generate comprehensive study packs including MCQs, definitions, and essay questions.")
    
    topics = st.text_area("Enter topics to cover", height=150, placeholder="e.g. Photosynthesis, Cellular Respiration, Krebs Cycle")
    
    if st.button("Generate Exam Pack", type="primary", disabled=not topics):
        with st.spinner("Generating content..."):
            resp = requests.post(f"{API_URL}/exam-pack", json={"topics": topics})
            if resp.status_code == 200:
                data = resp.json()
                st.success("Exam pack generated!")
                with st.expander("View Content", expanded=True):
                    st.write_stream(stream_text(data["content"])) 
                
                # Download
                dl_resp = requests.get(f"{API_URL}/download/exam-pack")
                if dl_resp.status_code == 200:
                    st.download_button("📥 Download PDF/Text", dl_resp.content, "exam_pack.txt")
            else:
                st.error("Failed to generate exam pack")

# ─── PAGE: NOTEBOOK ────────────────────────────────────────────────────────────
def render_notebook_page():
    st.title("📒 Interactive Notebook")
    st.markdown("Compile all your knowledge capabilities into a single structured notebook.")
    
    if st.button("Generate Notebook", type="primary"):
        with st.spinner("Compiling notebook..."):
            resp = requests.post(f"{API_URL}/build-notebook")
            if resp.status_code == 200:
                data = resp.json()
                st.write_stream(stream_text(data["content"]))
                 # Download
                dl_resp = requests.get(f"{API_URL}/download/notebook")
                if dl_resp.status_code == 200:
                    st.download_button("📥 Download Markdown", dl_resp.content, "notebook.md")
            else:
                st.error("Failed to build notebook")


# ─── MAIN APP ROUTER ───────────────────────────────────────────────────────────
def main():
    page = render_sidebar()
    
    if page == "chat":
        render_chat_page()
    elif page == "library":
        render_library_page()
    elif page == "exam":
        render_exam_page()
    elif page == "notebook":
        render_notebook_page()

if __name__ == "__main__":
    main()
