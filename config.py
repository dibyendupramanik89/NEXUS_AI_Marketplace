"""
NEXUS AI Marketplace - LLM Configuration
Supports: Claude (Anthropic) → Gemini → Ollama (Local) → Deterministic Fallback
Automatically detects available LLM and selects best model.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

_ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
_GEMINI_KEY = os.getenv("GEMINI_API_KEY")
_OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "false").lower() == "true"
_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
_OLLAMA_PRIMARY_MODEL = os.getenv("OLLAMA_PRIMARY_MODEL", "gemma4:e4b")  # Google Gemma
_OLLAMA_SECONDARY_MODEL = os.getenv("OLLAMA_SECONDARY_MODEL", "qwen3.5:2b")


def _check_ollama_available() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{_OLLAMA_HOST}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _is_ollama_model_available(model_name: str) -> bool:
    """Check if a specific model is available in Ollama."""
    try:
        response = requests.get(f"{_OLLAMA_HOST}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            available_models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
            return any(model_name in m for m in available_models)
    except Exception:
        pass
    return False


def get_llm(temperature: float = 0.0):
    """
    Returns the best available LLM.
    Priority:
    1. Claude (Anthropic) - cloud API
    2. Gemini (Google) - cloud API
    3. Ollama (Local) - offline, privacy-first
    4. Deterministic Fallback
    """
    
    # Try Cloud APIs first
    if _ANTHROPIC_KEY:
        try:
            from langchain_anthropic import ChatAnthropic
            print("🤖 [CONFIG] Using Claude 3.5 Sonnet (Anthropic)")
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=temperature,
                api_key=_ANTHROPIC_KEY,
            )
        except ImportError:
            print("⚠️  [CONFIG] langchain-anthropic not installed")

    if _GEMINI_KEY:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            print("🤖 [CONFIG] Using Gemini 2.5 Flash (Google)")
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=temperature,
                google_api_key=_GEMINI_KEY,
            )
        except ImportError:
            print("⚠️  [CONFIG] langchain-google-genai not installed")

    # Try Ollama (Local)
    if _OLLAMA_ENABLED and _check_ollama_available():
        try:
            from langchain_ollama import ChatOllama
            
            # Try primary model (Gemma2)
            if _is_ollama_model_available(_OLLAMA_PRIMARY_MODEL):
                print(f"🤖 [CONFIG] Using {_OLLAMA_PRIMARY_MODEL.upper()} (Ollama - Local)")
                return ChatOllama(
                    model=_OLLAMA_PRIMARY_MODEL,
                    base_url=_OLLAMA_HOST,
                    temperature=temperature,
                    keep_alive="5m",
                )
            
            # Fallback to secondary model (Llama2)
            if _is_ollama_model_available(_OLLAMA_SECONDARY_MODEL):
                print(f"🤖 [CONFIG] Using {_OLLAMA_SECONDARY_MODEL.upper()} (Ollama - Local)")
                return ChatOllama(
                    model=_OLLAMA_SECONDARY_MODEL,
                    base_url=_OLLAMA_HOST,
                    temperature=temperature,
                    keep_alive="5m",
                )
            
            print(f"⚠️  [CONFIG] No Ollama models available. Install: ollama pull {_OLLAMA_PRIMARY_MODEL}")
        except ImportError:
            print("⚠️  [CONFIG] langchain-ollama not installed. Run: pip install langchain-ollama")
        except Exception as e:
            print(f"⚠️  [CONFIG] Ollama error: {e}")

    print("⚠️  [CONFIG] No LLM found. Running in deterministic fallback mode.")
    print("   📌 To use Ollama:")
    print("      1. Install: brew install ollama")
    print("      2. Start: ollama serve")
    print("      3. Pull models: ollama pull gemma2 && ollama pull llama2")
    print("      4. Set OLLAMA_ENABLED=true in .env")
    return None


def get_active_llm_name() -> str:
    """Get name of the active LLM."""
    if _ANTHROPIC_KEY:
        return "Claude 3.5 Sonnet (Anthropic)"
    
    if _GEMINI_KEY:
        return "Gemini 2.5 Flash (Google)"
    
    if _OLLAMA_ENABLED and _check_ollama_available():
        if _is_ollama_model_available(_OLLAMA_PRIMARY_MODEL):
            return f"{_OLLAMA_PRIMARY_MODEL.upper()} (Ollama - Local)"
        if _is_ollama_model_available(_OLLAMA_SECONDARY_MODEL):
            return f"{_OLLAMA_SECONDARY_MODEL.upper()} (Ollama - Local)"
    
    return "Deterministic Fallback (Offline)"


def get_ollama_models_available() -> list:
    """Get list of available Ollama models."""
    try:
        response = requests.get(f"{_OLLAMA_HOST}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        pass
    return []
