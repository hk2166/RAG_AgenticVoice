"""
Anthropic REST client — thin wrapper around the Anthropic API.

Kept for backwards compatibility; the main pipeline uses the anthropic SDK
(see app/llm/generate.py, app/improved_query/query_rewrite.py, etc.).
"""

import anthropic
from app.config import ANTHROPIC_API_KEY, LLM_MODEL
from app.embeddings import embed_text

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Embeddings ──────────────────────────────────────

def embed_content(text: str, model: str = None) -> list:
    """
    Return a list[float] embedding for *text*.

    Uses sentence-transformers locally (no API key required).
    The `model` argument is ignored — kept for API compatibility.
    """
    return embed_text(text)


# ── Text generation ─────────────────────────────────

def generate_content(prompt: str, model: str = None, temperature: float = 0.3) -> str:
    """
    Send *prompt* to Claude and return the generated text.
    """
    response = _client.messages.create(
        model=model or LLM_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
