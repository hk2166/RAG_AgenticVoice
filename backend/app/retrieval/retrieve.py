import faiss
import pickle
import numpy as np
from google import genai

from app.config import GEMINI_API_KEY, FAISS_INDEX_PATH, CHUNKS_PATH
from app.improved_query.query_rewrite import rewrite_query
from app.query_ranker.rerank import rerank

client = genai.Client(api_key=GEMINI_API_KEY)

# Lazy-loaded globals — populated on first call to retrieve()
_index = None
_chunks = None


def _load_index():
    global _index, _chunks
    if _index is None:
        _index = faiss.read_index(FAISS_INDEX_PATH)
        with open(CHUNKS_PATH, "rb") as f:
            _chunks, _ = pickle.load(f)


def retrieve(query: str, k: int = 12):

    _load_index()

    # rewrite vague queries
    query = rewrite_query(query)

    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=query
    )

    query_vector = np.array(
        [response.embeddings[0].values],
        dtype="float32"
    )

    faiss.normalize_L2(query_vector)

    scores, indices = _index.search(query_vector, k)

    results = []

    for j, i in enumerate(indices[0]):

        if i != -1 and i < len(_chunks):

            results.append({
                "chunk": _chunks[i],
                "score": float(scores[0][j])
            })

    # semantic rerank
    results = rerank(query, results)

    return results