"""
Local embedding utility using sentence-transformers.
No API key required — the model is downloaded once and cached locally (~90 MB).
"""

from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_text(text: str) -> list[float]:
    """Return a normalized 384-dim embedding for a single text string."""
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()
