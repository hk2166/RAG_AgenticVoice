import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "models/gemini-2.0-flash"

FAISS_INDEX_PATH = "faiss.index"
CHUNKS_PATH = "chunks.pkl"
