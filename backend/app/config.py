import os

# Workaround for macOS duplicate OpenMP runtime error (libomp.dylib)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Latest Gemini models (google-genai 1.x)
EMBEDDING_MODEL = "gemini-embedding-2"
LLM_MODEL = "gemini-2.5-flash"

# Absolute paths — always resolved relative to this file, regardless of CWD
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(_BASE_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(_BASE_DIR, "chunks.pkl")
