import faiss
import pickle
import numpy as np
from google import genai

from app.config import GEMINI_API_KEY, FAISS_INDEX_PATH, CHUNKS_PATH

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


def retrieve(query: str, k: int = 3) -> list[str]:

    # Load FAISS index
    index = faiss.read_index(FAISS_INDEX_PATH)

    # Load original chunks
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    # Embed query
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=query,
    )
    query_vector = np.array([response.embeddings[0].values]).astype("float32")

    # Search FAISS
    distances, indices = index.search(query_vector, k)

    results = [
        {"chunk": chunks[i], "distance": float(distances[0][j])}
        for j, i in enumerate(indices[0])
    ]

    return results

