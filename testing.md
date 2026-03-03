# Testing Guide — Voice RAG Agent

---

## 0. Start the Server

```bash
cd /Users/hemant/Desktop/personal/Project/GPU/backend
/Users/hemant/Desktop/personal/Project/GPU/venv/bin/uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000

---

## 2. Rebuild FAISS Index (run after changing the PDF)

```bash
cd /Users/hemant/Desktop/personal/Project/GPU/backend && \
/Users/hemant/Desktop/personal/Project/GPU/venv/bin/python -m app.ingestion.ingest 2>&1
```

---

## 3. Test Ingestion + Retrieval Only (no server needed)

```bash
cd /Users/hemant/Desktop/personal/Project/GPU/backend && \
/Users/hemant/Desktop/personal/Project/GPU/venv/bin/python -c "
from app.retrieval.retrieve import retrieve
results = retrieve('What programming languages does he know and what is his name and which college is he from?', k=3)
for i, r in enumerate(results):
    print(f'[{i+1}] score={r[\"distance\"]:.4f}  {r[\"chunk\"][:300]}')
"
```

---

## 4. Test LLM Generation (RAG — no server needed)

```bash
cd /Users/hemant/Desktop/personal/Project/GPU/backend && \
/Users/hemant/Desktop/personal/Project/GPU/venv/bin/python -m app.llm.generate
```

---

## 5. Test TTS Only (no server needed)

```bash
cd /Users/hemant/Desktop/personal/Project/GPU/backend && \
/Users/hemant/Desktop/personal/Project/GPU/venv/bin/python -c "
import asyncio
from app.tts.edge_tts_provider import text_to_speech
async def test():
    audio = await text_to_speech('Hello, this is a TTS test.')
    with open('/tmp/tts_test.mp3', 'wb') as f:
        f.write(audio)
    print(f'TTS OK — {len(audio)} bytes saved to /tmp/tts_test.mp3')
asyncio.run(test())
"
open /tmp/tts_test.mp3
```

---

## 6. Test Full Pipeline via API — returns JSON (server must be running)

```bash
curl -X POST "http://localhost:8000/voice/text" \
  -F "audio=@backend/data/TEST.wav"
```

Expected:

```json
{ "question": "...", "answer": "..." }
```

---

## 7. Test Full Pipeline via API — returns MP3 audio (server must be running)

```bash
curl -X POST "http://localhost:8000/voice" \
  -F "audio=@backend/data/TEST.wav" \
  --output /tmp/response.mp3

open /tmp/response.mp3
```

---

## 8. Swagger UI (visual, no curl needed)

Open in browser: http://localhost:8000/docs

- Click `POST /voice/text` → Try it out → Upload a `.wav` → Execute
- Click `POST /voice` → Try it out → Upload a `.wav` → Execute → Download audio

---

## 9. Record a Test Audio on macOS

```bash
# Using ffmpeg (5 seconds from mic)
ffmpeg -f avfoundation -i ":0" -t 5 backend/data/TEST.wav

# Using sox
sox -d -r 16000 -c 1 backend/data/TEST.wav trim 0 5
```
