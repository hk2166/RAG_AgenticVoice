# Real-Time Voice RAG Agent

A **Real-Time Voice RAG Agent** that listens to a spoken question, retrieves relevant context from an uploaded PDF, generates a grounded answer with Gemini, and responds in voice.

Pipeline: **STT (Faster-Whisper) → FAISS RAG → Gemini LLM → Edge-TTS**

---

## Tech Stack

| Layer          | Technology                                        |
| -------------- | ------------------------------------------------- |
| Backend API    | FastAPI + Uvicorn                                 |
| Speech-to-Text | Faster-Whisper `large-v3 or medium` (local, int8) |
| LLM            | Gemini `models/gemini-2.0-flash`                  |
| Embeddings     | Gemini `models/gemini-embedding-001` (dim 3072)   |
| Vector Store   | FAISS `IndexFlatIP` with L2 normalisation         |
| Text-to-Speech | Edge-TTS `en-IN-NeerjaNeural`                     |
| Frontend       | Vanilla HTML / CSS / JS (dark theme)              |

---

## Features

| Status | Feature                                        |
| ------ | ---------------------------------------------- |
| ✅     | Local Speech-to-Text (Faster-Whisper large-v3) |
| ✅     | Gemini 2.0 Flash LLM reasoning                 |
| ✅     | Gemini embeddings (dim 3072)                   |
| ✅     | FAISS cosine-similarity vector index           |
| ✅     | Edge-TTS voice output                          |
| ✅     | Dynamic PDF upload via `/ingest`               |
| ✅     | Modular architecture                           |
| ✅     | Low-latency pipeline                           |

---

## Architecture

```
Microphone Input (browser)
        ↓
Faster-Whisper large-v3  (STT — local, int8)
        ↓
    Text Query
        ↓
Gemini gemini-embedding-001  →  FAISS IndexFlatIP
        ↓
Top-12 Context Chunks
        ↓
Gemini models/gemini-2.0-flash  (LLM)
        ↓
Edge-TTS en-IN-NeerjaNeural  (TTS)
        ↓
Spoken Audio Response (browser)
```

---

## Project Structure

```
GPU/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router registration
│   │   ├── config.py          # API keys, model names, index paths
│   │   ├── ingestion/
│   │   │   └── ingest.py      # PDF → chunks → FAISS index pipeline
│   │   ├── improved_query/
│   │   │   └── query_rewrite.py  # LLM-powered query rewriter
│   │   ├── query_ranker/
│   │   │   └── rerank.py      # LLM-powered semantic reranker
│   │   ├── retrieval/
│   │   │   └── retrieve.py    # Query expansion + cosine similarity search
│   │   ├── llm/
│   │   │   └── generate.py    # Grounded Gemini prompt + generation
│   │   ├── stt/
│   │   │   └── whisper_provider.py   # Faster-Whisper transcription
│   │   ├── tts/
│   │   │   └── edge_tts_provider.py  # Edge-TTS synthesis
│   │   └── routes/
│   │       ├── voice.py       # POST /voice, POST /voice/text
│   │       └── ingest.py      # POST /ingest, GET /api/document
│   ├── data/                  # gitignored — place PDFs here
│   └── .env                   # gitignored — create locally
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── venv/                      # gitignored — create locally
└── README.md
```

---

## Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd GPU
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

> **Note:** The `venv/` folder is gitignored and must be created locally — never commit it.

### 3️⃣ Install Dependencies

```bash
cd backend
pip install fastapi uvicorn faster-whisper faiss-cpu edge-tts google-genai\
            langchain-text-splitters pypdf python-dotenv python-multipart numpy
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> **Warning:** `.env` is gitignored and must **never** be committed. Keep your API key private.

### 5️⃣ Ingest Your PDF

Place your PDF in `backend/data/` and run the ingestion script once:

```bash
cd backend
python -m app.ingestion.ingest
```

This builds `faiss.index` and `chunks.pkl` inside `backend/app/`.

Alternatively, upload a PDF directly through the web UI after starting the server.

### 6️⃣ Run the Server

```bash
cd backend
uvicorn app.main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## API Reference

### POST `/voice`

Upload audio and receive a spoken answer (full end-to-end pipeline).

**Form field:** `audio` — audio recording (.webm / .wav)

**Response headers:**

| Header            | Description                     |
| ----------------- | ------------------------------- |
| `X-Transcription` | Whisper transcript of the query |
| `X-Response-Text` | LLM answer text                 |

**Response body:** `audio/mpeg` — synthesised speech

```bash
curl -X POST http://localhost:8000/voice \
     -F "audio=@query.webm" \
     --output response.mp3
```

---

### POST `/voice/text`

Debug endpoint — same as `/voice` but returns JSON instead of audio.

**Form field:** `audio` — audio recording (.webm / .wav)

```bash
curl -X POST http://localhost:8000/voice/text \
     -F "audio=@query.webm"
```

**Response:** `{ "question": "...", "answer": "..." }`

---

### POST `/ingest`

Upload a PDF to rebuild the FAISS index at runtime (no server restart needed).

```bash
curl -X POST http://localhost:8000/ingest \
     -F "file=@resume.pdf"
```

**Response:**

```json
{
  "status": "success",
  "filename": "resume.pdf",
  "pages": 2,
  "chunks": 47,
  "dim": 3072
}
```

---

### GET `/api/document`

Check whether a FAISS index is currently loaded on disk.

```bash
curl http://localhost:8000/api/document
```

**Response:** `{ "loaded": true }`

---

### GET `/api/health`

Health-check endpoint.

```bash
curl http://localhost:8000/api/health
```

**Response:** `{ "status": "ok", "message": "Voice RAG Agent is running" }`

---

## Frontend

Served automatically by FastAPI from the `frontend/` directory at `http://localhost:8000`.

| Panel       | Description                                                                    |
| ----------- | ------------------------------------------------------------------------------ |
| Upload zone | Drag-and-drop or click to upload a PDF; shows real chunk count after ingestion |
| Chat area   | Conversation bubbles — your question on the right, agent answer on the left    |
| Mic footer  | Press the microphone button to record; release to send                         |

---

## Environment Variables

| Variable         | Required | Description              |
| ---------------- | -------- | ------------------------ |
| `GEMINI_API_KEY` | Yes      | Google AI Studio API key |

Create `backend/.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

> `.env` is gitignored and must never be committed.

---

## Notes

- The FAISS index is stored at `backend/app/faiss.index` and `backend/app/chunks.pkl`.
- Uploading a new PDF via `/ingest` or the UI replaces the existing index immediately.
- Whisper runs locally in `int8` mode — no external STT API is required.
- Edge-TTS requires an outbound internet connection for synthesis.
