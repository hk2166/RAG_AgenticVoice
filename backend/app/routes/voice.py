from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response
from urllib.parse import quote

from app.stt.whisper_provider import transcribe_audio
from app.llm.generate import generate_answer
from app.tts.edge_tts_provider import text_to_speech

router = APIRouter()


def _safe_header(value: str) -> str:
    """Encode a string so it is safe to use as an HTTP header value.

    HTTP/1.1 headers must be Latin-1 (ISO-8859-1). Characters outside that
    range trigger a ValueError in uvicorn/h11. We URL-encode any non-ASCII
    characters so the value is always ASCII-clean.
    """
    # Collapse newlines first (multi-line headers are forbidden)
    value = value.strip().replace("\n", " ").replace("\r", " ")
    # URL-encode non-ASCII bytes so the header stays ASCII-safe
    return quote(value, safe=" .,!?-_()'\"")


@router.post("/voice")
async def voice_query(audio: UploadFile = File(...)):
    """
    Full voice RAG pipeline:
      1. Transcribe audio (STT)
      2. Retrieve relevant chunks + generate answer (RAG)
      3. Convert answer to speech (TTS)
      4. Return audio bytes + transcription/answer as response headers
    """
    audio_bytes = await audio.read()

    # STT
    question = transcribe_audio(audio_bytes)

    # RAG
    answer = await generate_answer(question)

    # TTS
    audio_response = await text_to_speech(answer)

    return Response(
        content=audio_response,
        media_type="audio/mpeg",
        headers={
            "X-Transcription": _safe_header(question),
            "X-Response-Text": _safe_header(answer),
        },
    )


@router.post("/voice/text")
async def voice_query_text(audio: UploadFile = File(...)):
    """Debug endpoint — returns JSON with transcript and answer instead of audio."""
    audio_bytes = await audio.read()
    question = transcribe_audio(audio_bytes)
    answer = await generate_answer(question)
    return {"question": question, "answer": answer}

