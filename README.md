#  RealTime Voice Agent

A modular, deployable Voice-Based Retrieval-Augmented Generation (RAG) system powered by Gemini.

> **Accepts queries → Retrieves context → Generates grounded responses → Responds in custom voice**

---

##  Features

| Status | Feature                                          |
| ------ | ------------------------------------------------ |
| ✅     | Gemini 1.5 Flash for reasoning                   |
| ✅     | Gemini embeddings (`text-embedding-004`)         |
| ✅     | FAISS vector index                               |
| ✅     | ElevenLabs voice synthesis (voice cloning ready) |
| ✅     | Modular architecture (STT, RAG, Agent, TTS)      |
| ✅     | Dockerized & deployment ready                    |
| 🔜     | STT integration (Deepgram / Gemini audio)        |
| 🔜     | Persistent DB (Supabase / pgvector)              |
| 🔜     | Streaming WebSocket support                      |

---

##  Architecture

```
┌─────────────────────────────────────────────────────┐
│                      Client                         │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│                 FastAPI Backend                     │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│              Agent Orchestrator                     │
│  ┌────────────────┬────────────────┬──────────────┐ │
│  │   Retrieval    │   Gemini LLM   │     TTS      │ │
│  │ FAISS + Gemini │   1.5 Flash    │  ElevenLabs  │ │
│  └────────────────┴────────────────┴──────────────┘ │
└─────────────────────┬───────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│                 Audio Response                      │
└─────────────────────────────────────────────────────┘
```

**Future Upgrades:**

- FAISS → pgvector
- ElevenLabs → Local TTS
- WebSocket streaming
- Persistent conversation memory
- Domain fine-tuning

---

##  Project Structure

```
RealTime-Voice-Agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── dependencies.py      # Shared dependencies
│   │   │
│   │   ├── agent/
│   │   │   └── orchestrator.py  # Gemini agent logic
│   │   │
│   │   ├── db/
│   │   │   └── models.py        # Database models
│   │   │
│   │   ├── rag/
│   │   │   ├── embeddings.py    # Gemini embeddings
│   │   │   ├── ingest.py        # Document ingestion
│   │   │   └── retriever.py     # FAISS retrieval
│   │   │
│   │   ├── stt/
│   │   │   └── provider.py      # Speech-to-text provider
│   │   │
│   │   ├── tts/
│   │   │   └── provider.py      # ElevenLabs TTS
│   │   │
│   │   └── routes/
│   │       ├── voice.py         # Voice endpoint
│   │       ├── documents.py     # Document management
│   │       └── users.py         # User management
│   │
│   └── requirement.txt
│
├── frontend/                     # (Coming soon)
├── .gitignore
└── README.md
```

---

##  Setup

### 1. Clone Repository

```bash
git clone https://github.com/hk2166/RealTime-Voice-Agent.git
cd RealTime-Voice-Agent/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirement.txt
```

### 4. Configure Environment

Create `.env` in `backend/`:

```env
GEMINI_API_KEY=your_gemini_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

### 5. Ingest Documents

```python
from app.rag.ingest import ingest_pdf
ingest_pdf("sample.pdf")
```

This generates `faiss_index/` and `metadata.pkl`.

### 6. Run Server

```bash
uvicorn app.main:app --reload
```

Server: `http://127.0.0.1:8000`

---

##  Testing

### Swagger UI

```
http://127.0.0.1:8000/docs
```

**POST `/voice`**

| Field      | Description         |
| ---------- | ------------------- |
| `question` | Your query          |
| `voice_id` | ElevenLabs voice ID |

### cURL

```bash
curl -X POST "http://127.0.0.1:8000/voice" \
  -F "question=What is this document about?" \
  -F "voice_id=YOUR_VOICE_ID" \
  --output response.mp3
```

---

##  Docker

```bash
# Build
docker build -t realtime-voice-agent .

# Run
docker run -p 8000:8000 realtime-voice-agent
```

---

##  Deployment

| Component | Recommendation    |
| --------- | ----------------- |
| Backend   | Railway / Render  |
| Frontend  | Vercel            |
| Vector DB | Supabase pgvector |
| Storage   | Supabase / S3     |

---

##  Performance

| Parameter       | Value              |
| --------------- | ------------------ |
| Chunk size      | 500 tokens         |
| Top-k retrieval | 3                  |
| Model           | gemini-1.5-flash   |
| Embeddings      | text-embedding-004 |

---

## Roadmap

| Phase          | Features                                            |
| -------------- | --------------------------------------------------- |
| **Phase 1** | Voice RAG system, Gemini reasoning, ElevenLabs TTS  |
| **Phase 2** | STT integration, DB persistence, Frontend UI        |
| **Phase 3** | Agentic tools, Memory layer, Fine-tuning, Streaming |

---

