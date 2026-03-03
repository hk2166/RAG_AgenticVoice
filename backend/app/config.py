import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "models/gemini-2.0-flash"

# Absolute paths — always resolved relative to this file, regardless of CWD
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(_BASE_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(_BASE_DIR, "chunks.pkl")
