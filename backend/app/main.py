from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.voice import router as voice_router

app = FastAPI(
    title="Real-Time Voice RAG Agent",
    description="STT → RAG → TTS pipeline powered by Faster-Whisper, FAISS, Gemini, and Edge-TTS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router, tags=["Voice"])


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Voice RAG Agent is running"}
