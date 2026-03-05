import asyncio
from google import genai

from app.config import GEMINI_API_KEY, LLM_MODEL
from app.retrieval.retrieve import retrieve

client = genai.Client(api_key=GEMINI_API_KEY)

_SYSTEM_PROMPT = """You are a helpful voice assistant that answers questions strictly based
on the provided document context. Keep answers concise and conversational since they will be
read aloud. If the answer is not in the context, say so honestly."""


async def generate_answer(question: str) -> str:
    """
    Full RAG step:
      1. Retrieve relevant chunks for `question`
      2. Compose a prompt with the retrieved context
      3. Call Gemini and return the answer text
    """
    # Retrieval is blocking (FAISS + HTTP) — run in a thread
    docs = await asyncio.to_thread(retrieve, question)

    context = "\n\n".join(d["chunk"] for d in docs)

    prompt = f"""{_SYSTEM_PROMPT}

Context from document:
{context}

User question: {question}

Answer:"""

    response = await asyncio.to_thread(
        client.models.generate_content,
        model=LLM_MODEL,
        contents=prompt,
    )

    return response.text.strip()