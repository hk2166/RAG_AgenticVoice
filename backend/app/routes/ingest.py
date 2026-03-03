import asyncio
import os

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.ingestion.ingest import ingest_pdf_bytes
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


@router.get("/api/document")
async def document_status():
    """Return whether a document index is currently loaded on disk."""
    loaded = os.path.exists(FAISS_INDEX_PATH) and os.path.exists(CHUNKS_PATH)
    return {"loaded": loaded}
