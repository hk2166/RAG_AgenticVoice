import whisper
import tempfile
import os

_whisper_model = whisper.load_model("small")

def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio directly with the open-source Whisper model."""
    fd, tmp_path = tempfile.mkstemp(suffix=".webm")
    os.close(fd)
    
    try:
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)
        return _whisper_model.transcribe(tmp_path)["text"].strip()
    finally:
        try: os.remove(tmp_path)
        except OSError: pass