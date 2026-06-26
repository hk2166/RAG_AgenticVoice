import os

# Workaround for macOS duplicate OpenMP runtime error (libomp.dylib)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # used by STT (Gemini audio transcription)
LLM_MODEL = "claude-opus-4-8"

# Absolute paths — always resolved relative to this file, regardless of CWD
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(_BASE_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(_BASE_DIR, "chunks.pkl")
