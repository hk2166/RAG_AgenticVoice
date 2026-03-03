from faster_whisper import WhisperModel
import tempfile
import os

model = WhisperModel("base", compute_type="int8")


def transcribe_audio(audio_bytes: bytes):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    segments, _ = model.transcribe(tmp_path)

    text = ""
    for segment in segments:
        text += segment.text

    os.remove(tmp_path)

    return text.strip()