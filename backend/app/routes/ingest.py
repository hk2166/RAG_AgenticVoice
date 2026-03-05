import asyncio
import os

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.ingestion.ingest import ingest_pdf_bytes, ingest_text
from app.config import FAISS_INDEX_PATH, CHUNKS_PATH

router = APIRouter()


@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Accept a PDF upload, run the full ingestion pipeline, and persist
    faiss.index + chunks.pkl so voice queries can use it immediately.
    """
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only PDF files are supported."},
        )

    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        return JSONResponse(
            status_code=400,
            content={"error": "Uploaded file is empty."},
        )

    # Run blocking pipeline in a thread so the event loop stays free
    result = await asyncio.to_thread(ingest_pdf_bytes, pdf_bytes, file.filename)
    return {"status": "success", **result}


class TextIngestRequest(BaseModel):
    text: str
    title: str = "Pasted Text"


@router.post("/ingest/text")
async def ingest_text_document(body: TextIngestRequest):
    """
    Accept raw plain text, run the full ingestion pipeline, and persist
    faiss.index + chunks.pkl so voice queries can use it immediately.
    """
    if not body.text.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Text content is empty."},
        )

    if len(body.text.strip()) < 50:
        return JSONResponse(
            status_code=400,
            content={"error": "Text is too short to index (minimum 50 characters)."},
        )

    result = await asyncio.to_thread(ingest_text, body.text, body.title)
    return {"status": "success", **result}


@router.get("/api/document")
async def document_status():
    """Return whether a document index is currently loaded on disk."""
    loaded = os.path.exists(FAISS_INDEX_PATH) and os.path.exists(CHUNKS_PATH)
    return {"loaded": loaded}
