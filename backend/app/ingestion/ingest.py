import os
import faiss
import pickle
import numpy as np
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai

from app.config import GEMINI_API_KEY, FAISS_INDEX_PATH, CHUNKS_PATH

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


def ingest_pdf(path: str):

    # 1️⃣ Extract text from PDF
    print(f"[1/5] Loading PDF: {path}")
    reader = PdfReader(path)
    full_text = ""
    for page in reader.pages:
        full_text += (page.extract_text() or "") + "\n"
    print(f"      Extracted {len(full_text)} characters from {len(reader.pages)} pages")

    # 2️⃣ Split text into chunks
    print("[2/5] Chunking text ...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=80,
    )
    chunks = splitter.split_text(full_text)
    print(f"      Created {len(chunks)} chunks")

    # 3️⃣ Create embeddings
    print("[3/5] Generating embeddings ...")
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

    # 4️⃣ Store in FAISS
    print("[4/5] Building FAISS index ...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print(f"      Index contains {index.ntotal} vectors (dim={dimension})")

    # 5️⃣ Save index and chunks
    print("[5/5] Saving to disk ...")
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"\n✅ Ingestion complete!")
    print(f"   -> {FAISS_INDEX_PATH}")
    print(f"   -> {CHUNKS_PATH}")


if __name__ == "__main__":
    # Resolve path to data/cv_dev.pdf relative to this file
    base_dir = os.path.dirname(__file__)
    pdf_path = os.path.normpath(os.path.join(base_dir, "..", "..", "data", "cv_dev.pdf"))
    ingest_pdf(pdf_path)