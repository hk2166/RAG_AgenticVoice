# 🎙 Real-Time Voice RAG Agent

A functional **Real-Time Voice Retrieval-Augmented Generation (RAG) Agent** built to:

- Listen to a spoken question
- Retrieve relevant context from a knowledge base (PDF)
- Generate a grounded answer using Gemini
- Respond back in voice

This project fulfills the assignment requirements for:

- STT (Speech-to-Text)
- RAG Engine
- Orchestration Logic
- TTS (Text-to-Speech)
- Low latency interaction

---

##  Tech Stack

- **FastAPI** – Backend API
- **Faster-Whisper** – Local Speech-to-Text
- **Gemini 1.5 Flash** – LLM Reasoning
- **Gemini Embeddings (`gemini-embedding-001`)** – Vector embeddings
- **FAISS** – Vector similarity search
- **Edge-TTS** – Text-to-Speech

---

##  Features

| Status | Feature                               |
| ------ | ------------------------------------- |
| ✅     | Local Speech-to-Text (Faster-Whisper) |
| ✅     | Gemini reasoning (1.5 Flash)          |
| ✅     | Gemini embeddings                     |
| ✅     | FAISS vector index                    |
| ✅     | Edge-TTS voice output                 |
| ✅     | Modular architecture                  |
| ✅     | Low-latency backend                   |
| ❌     | Voice cloning (not implemented)       |
| ❌     | Streaming WebSocket (not implemented) |

---

##  Architecture

```
Microphone Input
       ↓
Faster-Whisper (STT)
       ↓
   Text Query
       ↓
FAISS Retrieval (Gemini Embeddings)
       ↓
Gemini 1.5 Flash (Grounded Response)
       ↓
    Edge-TTS
       ↓
Spoken Audio Response
```

This matches the required pipeline:

**STT → RAG → Orchestration → TTS**

---

## 📂 Project Structure

```
GPU/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── ingestion/
│   │   │   └── ingest.py
│   │   ├── retrieval/
│   │   │   └── retrieve.py
│   │   ├── llm/
│   │   │   └── generate.py
│   │   ├── stt/
│   │   │   └── whisper_provider.py
│   │   ├── tts/
│   │   │   └── edge_tts_provider.py
│   │   └── routes/
│   │       └── voice.py
│   ├── data/           ← gitignored, add your PDFs here
│   └── .env            ← gitignored, create this locally
├── frontend/
├── venv/               ← gitignored, created by you locally
└── README.md
```

---

##  Setup Instructions

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
pip install fastapi uvicorn faster-whisper faiss-cpu edge-tts google-generativeai pypdf python-dotenv python-multipart
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

> **Warning:** `.env` is gitignored and must **never** be committed. Keep your API key private.

### 5️⃣ Ingest PDF (Required Before Running)

Place your PDF file in `backend/data/` and run:

```python
from app.ingestion.ingest import ingest_pdf
ingest_pdf("data/your_document.pdf")
```

This generates:

- `faiss.index`
- `chunks.pkl`

### 6️⃣ Run the Server

```bash
cd backend
uvicorn app.main:app --reload
```

---

##  API Usage

### Voice Query Endpoint

**POST** `/voice`

Upload an audio file to get a spoken response:

```bash
curl -X POST "http://localhost:8000/voice" \
  -F "audio=@your_audio.wav"
```

