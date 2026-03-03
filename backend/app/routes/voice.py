from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response

from app.stt.whisper_provider import transcribe_audio
from app.llm.generate import generate_answer
from app.tts.edge_tts_provider import text_to_speech

router = APIRouter()


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
            "X-Transcription": question.strip().replace("\n", " "),
            "X-Response-Text": answer.strip().replace("\n", " "),
        },
    )


@router.post("/voice/text")
async def voice_query_text(audio: UploadFile = File(...)):
    """Debug endpoint — returns JSON with transcript and answer instead of audio."""
    audio_bytes = await audio.read()
    question = transcribe_audio(audio_bytes)
    answer = await generate_answer(question)
    return {"question": question, "answer": answer}
