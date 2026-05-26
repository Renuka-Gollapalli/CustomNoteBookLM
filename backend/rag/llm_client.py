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

GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"
# Fallback/alternative models available on Groq:
# - "llama-3.1-70b-versatile"
# - "llama-3.1-8b-instant"
# - "mixtral-8x7b-32768"

OLLAMA_DEFAULT_MODEL = "llama3"

# ─── LLM PROVIDER REGISTRY ──────────────────────────────────────────────────────
# This is the single place the active provider is stored.
# It is updated via set_provider() called from the FastAPI endpoint.
_provider_state = {
    "provider": "ollama",          # "ollama" | "groq"
    "groq_model": GROQ_DEFAULT_MODEL,
    "ollama_model": OLLAMA_DEFAULT_MODEL,
    "api_key": None
}

def set_provider(provider: str, groq_model: str = None, ollama_model: str = None, api_key: str = None):
    """Called by API to switch provider at runtime."""
    _provider_state["provider"] = provider
    if groq_model:
        _provider_state["groq_model"] = groq_model
    if ollama_model:
        _provider_state["ollama_model"] = ollama_model
    if api_key:
        _provider_state["api_key"] = api_key

def get_provider_info() -> dict:
    """Returns current provider state — used by /status endpoint."""
    return {
        "provider": _provider_state["provider"],
        "groq_model": _provider_state["groq_model"],
        "ollama_model": _provider_state["ollama_model"],
        "groq_api_key_set": bool(_provider_state["api_key"] or os.getenv("GROQ_API_KEY")),
    }

# ─── OLLAMA BACKEND ─────────────────────────────────────────────────────────────
def _ask_ollama(prompt: str, system: str, model: str, history: list = []) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    
    # Append history
    if history:
        messages.extend(history)
        
    messages.append({"role": "user", "content": prompt})

    response = ollama.chat(
        model=model,
        messages=messages,
        options={"temperature": 0.3, "num_predict": 1024}
    )
    return response["message"]["content"]

# ─── GROQ BACKEND ───────────────────────────────────────────────────────────────
def _ask_groq(prompt: str, system: str, model: str, history: list = []) -> str:
    api_key = _provider_state.get("api_key") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please set it in Settings or .env file."
        )

    client = Groq(api_key=api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
        
    # Append history
    if history:
        messages.extend(history)
        
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content

# ─── UNIFIED PUBLIC FUNCTION ────────────────────────────────────────────────────
def ask_llama(prompt: str, system: str = None, history: list = []) -> str:
    """
    Unified LLM call. Routes to Ollama or Groq based on current provider state.
    """
    provider = _provider_state["provider"]

    if provider == "groq":
        return _ask_groq(
            prompt=prompt,
            system=system,
            model=_provider_state["groq_model"],
            history=history
        )
    else:  # default: ollama
        return _ask_ollama(
            prompt=prompt,
            system=system,
            model=_provider_state["ollama_model"],
            history=history
        )
