"""
Gemini REST API client — bypasses the google-generativeai SDK entirely.

The SDK (v0.1.0rc1) installed on Python 3.8 lacks embed_content() and
GenerativeModel().  This module talks to the Gemini REST API directly
via `requests`, which works on any Python version.
"""

import requests
from app.config import GEMINI_API_KEY, EMBEDDING_MODEL, LLM_MODEL

_BASE = "https://generativelanguage.googleapis.com/v1beta"


# ── Embeddings ──────────────────────────────────────

def embed_content(text: str, model: str = None) -> list:
    """
    Return a list[float] embedding for *text*.

    Uses the REST endpoint:
      POST /v1beta/{model}:embedContent?key=...
    """
    model = model or EMBEDDING_MODEL          # e.g. "models/text-embedding-004"
    url = f"{_BASE}/{model}:embedContent?key={GEMINI_API_KEY}"

    payload = {
        "content": {
            "parts": [{"text": text}]
        }
    }

    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["embedding"]["values"]


# ── Text generation ─────────────────────────────────

def generate_content(prompt: str, model: str = None, temperature: float = 0.3) -> str:
    """
    Send *prompt* to Gemini and return the generated text.

    Uses the REST endpoint:
      POST /v1beta/models/{model}:generateContent?key=...
    """
    model = model or LLM_MODEL                # e.g. "gemini-2.0-flash-exp"
    # Accept both "models/gemini-..." and bare "gemini-..." names
    if not model.startswith("models/"):
        model = f"models/{model}"

    url = f"{_BASE}/{model}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
        },
    }

    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()

    data = resp.json()

    # Extract the text from the first candidate
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Gemini returned no candidates: {data}")

    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts)
