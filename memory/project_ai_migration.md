---
name: project-ai-migration
description: Migrated AI backend from Google Gemini to Anthropic Claude (LLM) + sentence-transformers (embeddings)
metadata:
  type: project
---

Replaced Google Gemini with Anthropic Claude for all LLM calls; replaced Gemini embeddings with sentence-transformers (local, free).

**Why:** User requested use of Anthropic API key for AI parts.

**How to apply:** Note that Anthropic has no embeddings API; embeddings use `all-MiniLM-L6-v2` via sentence-transformers (384-dim). Any existing FAISS index built with Gemini (3072-dim) must be rebuilt by re-running document ingestion.

Files changed:
- `requirements.txt` — removed google-generativeai/google-genai, added anthropic + sentence-transformers
- `backend/app/config.py` — GEMINI_API_KEY → ANTHROPIC_API_KEY, LLM_MODEL = claude-opus-4-8
- `backend/app/embeddings.py` — new shared module (sentence-transformers all-MiniLM-L6-v2)
- `backend/app/llm/generate.py` — google.genai → anthropic SDK
- `backend/app/improved_query/query_rewrite.py` — google.genai → anthropic SDK
- `backend/app/query_ranker/rerank.py` — google.genai → anthropic SDK
- `backend/app/ingestion/ingest.py` — Gemini embeddings → embed_text() from embeddings.py
- `backend/app/retrieval/retrieve.py` — Gemini embeddings → embed_text() from embeddings.py
- `backend/app/gemini_client.py` — updated to Anthropic/sentence-transformers
- `backend/.env` — GEMINI_API_KEY → ANTHROPIC_API_KEY placeholder
