import asyncio
from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, LLM_MODEL
from app.retrieval.retrieve import retrieve

client = genai.Client(api_key=GEMINI_API_KEY)

_SYSTEM_PROMPT = """You are a helpful voice assistant. Make use of the provided document context to answer questions. 
If the provided context does not contain the answer or is not sufficient to answer the question, clearly state before answering: "That information is outside the provided document, but here is what I found:" and use your Google Search tool to find the most up-to-date information online to complete the answer. 
Keep answers concise and conversational since they will be read aloud."""


# Python 3.8 compatibility: asyncio.to_thread was added in 3.9
async def run_in_thread(func, *args, **kwargs):
    """Run a blocking function in a thread pool executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


_conversation_history = []

async def generate_answer(question: str) -> str:
    """
    Full RAG step:
      1. Retrieve relevant chunks for `question`
      2. Compose a prompt with the retrieved context
      3. Call Gemini (with Google Search enabled) and return the answer text
    """
    global _conversation_history

    # Retrieval is blocking (FAISS + HTTP) — run in a thread
    docs = await run_in_thread(retrieve, question)

    context = "\n\n".join(d["chunk"] for d in docs)

    # Format recent history (last 3 turns / 6 messages)
    history_text = ""
    if _conversation_history:
        history_text = "Recent Conversation History:\n"
        for role, text in _conversation_history:
            history_text += f"{role.capitalize()}: {text}\n"
        history_text += "\n"

    # Note: Using `types.GenerateContentConfig` handles system instructions cleanly.
    prompt = f"""Context from document:
{context}

{history_text}User question: {question}

Answer:"""
    
    response = await run_in_thread(
        client.models.generate_content,
        model=LLM_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            tools=[{"google_search": {}}],
            temperature=0.3
        )
    )

    answer = response.text.strip() if response.text else "I couldn't find an answer to that."
    
    # Save to history and truncate to the last 3 turns (6 interactions)
    _conversation_history.append(("user", question))
    _conversation_history.append(("assistant", answer))
    _conversation_history = _conversation_history[-6:]

    return answer