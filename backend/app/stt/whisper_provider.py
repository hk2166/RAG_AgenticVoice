import os
from google import genai
from google.genai import types
import requests
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio using Gemini 2.5 Flash, fallback to Groq Whisper."""
    
    # Try Gemini 2.5 Flash first
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/webm'),
                "Transcribe this audio exactly as it is spoken. Output ONLY the transcript without any markdown or extra text. If the audio is completely silent or nothing can be heard, return an empty string."
            ]
        )
        if response.text:
            return response.text.strip()
    except Exception as e:
        print(f"Gemini STT failed: {e}. Falling back to Groq...")

    # Fallback to Groq Whisper if Gemini fails or returns none
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("GROQ_API_KEY not found. Cannot use Groq fallback.")
        return ""

    try:
        files = {'file': ('audio.webm', audio_bytes, 'audio/webm')}
        data = {'model': 'whisper-large-v3'}
        headers = {'Authorization': f'Bearer {groq_api_key}'}
        
        response = requests.post(
            'https://api.groq.com/openai/v1/audio/transcriptions', 
            headers=headers, 
            files=files, 
            data=data
        )
        response.raise_for_status()
        return response.json().get('text', '').strip()
    except Exception as e:
        print(f"Groq STT failed: {e}")
        return ""