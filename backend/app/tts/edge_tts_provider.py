import edge_tts
import uuid
import os


async def text_to_speech(text: str, voice="en-IN-NeerjaNeural"):

    filename = f"temp_{uuid.uuid4()}.mp3"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

    with open(filename, "rb") as f:
        audio = f.read()

    os.remove(filename)

    return audio