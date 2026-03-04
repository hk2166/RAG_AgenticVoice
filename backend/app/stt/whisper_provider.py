from faster_whisper import WhisperModel
import tempfile
import os


model = WhisperModel("large-v3", compute_type="int8")


def transcribe_audio(audio_bytes: bytes) -> str:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    segments, info = model.transcribe(
        tmp_path,
        language="en",           # skip language detection
        beam_size=5,             # beam search for better accuracy
        vad_filter=True,         # remove silence / non-speech
        vad_parameters={
            "min_silence_duration_ms": 500,
            "speech_pad_ms": 200,
        },
        temperature=0,           # deterministic, no random sampling
        condition_on_previous_text=True,
        word_timestamps=False,
    )

    text = "".join(segment.text for segment in segments)

    os.remove(tmp_path)

    print(f"[STT] Detected language: {info.language} (confidence: {info.language_probability:.2f})")
    print(f"[STT] Transcript: {text.strip()}")

    return text.strip()