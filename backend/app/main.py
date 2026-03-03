from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes.voice import router as voice_router
from app.routes.ingest import router as ingest_router

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
    expose_headers=["X-Transcription", "X-Response-Text"],
)

app.include_router(voice_router, tags=["Voice"])
app.include_router(ingest_router, tags=["Ingest"])


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Voice RAG Agent is running"}


app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")