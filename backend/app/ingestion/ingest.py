import io
import os
import faiss
import pickle
import numpy as np
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai

from app.config import GEMINI_API_KEY, FAISS_INDEX_PATH, CHUNKS_PATH

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


# ── Shared helpers ────────────────────────────────────────────────────────────

def _extract_text(reader: PdfReader) -> str:
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text


def _build_index(text: str) -> tuple:
    """Chunk → embed → normalize → FAISS index. Returns (chunks, embeddings, index)."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)
    chunks = splitter.split_text(text)
    print(f"      Created {len(chunks)} chunks")

    embeddings = []
    for i, chunk in enumerate(chunks):
        response = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=chunk,
        )
        embeddings.append(response.embeddings[0].values)
        print(f"      Embedded chunk {i + 1}/{len(chunks)}", end="\r")
    print()

    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    print(f"      Index: {index.ntotal} vectors (dim={embeddings.shape[1]})")
    return chunks, embeddings, index


def _save(chunks, embeddings, index):
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump((chunks, embeddings), f)


# ── Public API ────────────────────────────────────────────────────────────────

def ingest_pdf(path: str) -> dict:
    """Ingest a PDF from a file path (used by CLI / __main__)."""
    print(f"[1/4] Loading PDF: {path}")
    reader = PdfReader(path)
    text = _extract_text(reader)
    print(f"      Extracted {len(text)} characters from {len(reader.pages)} pages")

    print("[2/4] Chunking & embedding ...")
    chunks, embeddings, index = _build_index(text)

    print("[3/4] Saving to disk ...")
    _save(chunks, embeddings, index)

    print(f"\n✅ Ingestion complete! -> {FAISS_INDEX_PATH}")
    return {"pages": len(reader.pages), "chunks": len(chunks)}


def ingest_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> dict:
    """Ingest a PDF from raw bytes (used by the /ingest API endpoint)."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = _extract_text(reader)
    chunks, embeddings, index = _build_index(text)
    _save(chunks, embeddings, index)
    return {
        "filename": filename,
        "pages": len(reader.pages),
        "chunks": len(chunks),
        "dim": int(embeddings.shape[1]),
    }


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    pdf_path = os.path.normpath(os.path.join(base_dir, "..", "..", "data", "data.pdf"))
    ingest_pdf(pdf_path)