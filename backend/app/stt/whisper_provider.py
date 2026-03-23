from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, LLM_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

_TRANSCRIPTION_PROMPT = (
    "Transcribe the following audio exactly as spoken. "
    "Output ONLY the transcription text — no timestamps, no labels, "
    "no extra commentary. If the audio is silent or unintelligible, "
    "return an empty string."
)


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio bytes using Gemini's native audio understanding."""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/webm"),
            _TRANSCRIPTION_PROMPT,
        ],
    )

    text = response.text.strip()

    print(f"[STT] Transcript (Gemini): {text}")

    return text