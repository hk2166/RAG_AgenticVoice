import faiss
import pickle
import numpy as np
from google import genai

from app.config import GEMINI_API_KEY, FAISS_INDEX_PATH, CHUNKS_PATH

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


def expand_query(query: str) -> str:
    if len(query.split()) < 5:
        return f"In the document, {query}"
    return query


def retrieve(query: str, k: int = 3) -> list[dict]:

    query = expand_query(query)

    index = faiss.read_index(FAISS_INDEX_PATH)

    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    # Embed and normalize query vector (required for IndexFlatIP cosine similarity)
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=query,
    )
    query_vector = np.array([response.embeddings[0].values], dtype="float32")
    faiss.normalize_L2(query_vector)

    # Search — IndexFlatIP scores are cosine similarities (higher = better)
    scores, indices = index.search(query_vector, k)

    return [
        {"chunk": chunks[i], "distance": float(scores[0][j])}
        for j, i in enumerate(indices[0])
    ]