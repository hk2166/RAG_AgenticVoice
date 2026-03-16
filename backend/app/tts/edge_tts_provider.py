import edge_tts
import tempfile
import os


async def text_to_speech(text: str, voice="en-IN-NeerjaNeural") -> bytes:
    # Create temp file in the OS temp directory (not the CWD)
    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)  # close the raw file descriptor; edge_tts will open it by path

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(tmp_path)

        with open(tmp_path, "rb") as f:
            audio = f.read()
    finally:
        # Always clean up, even if synthesis or read fails
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return audio