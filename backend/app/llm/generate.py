import asyncio
import anthropic

from app.config import ANTHROPIC_API_KEY, LLM_MODEL
from app.retrieval.retrieve import retrieve

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_SYSTEM_PROMPT = """You are a helpful voice assistant. Make use of the provided document context to answer questions.
If the provided context does not contain the answer or is not sufficient to answer the question, clearly state before answering: "That information is outside the provided document, but here is what I know:" and answer from your training knowledge.
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
      3. Call Claude and return the answer text
    """
    global _conversation_history

    # Retrieval is blocking (FAISS + local embeddings) — run in a thread
    docs = await run_in_thread(retrieve, question)

    context = "\n\n".join(d["chunk"] for d in docs)

    # Format recent history (last 3 turns / 6 messages)
    history_text = ""
    if _conversation_history:
        history_text = "Recent Conversation History:\n"
        for role, text in _conversation_history:
            history_text += f"{role.capitalize()}: {text}\n"
        history_text += "\n"

    prompt = f"""Context from document:
{context}

{history_text}User question: {question}

Answer:"""

    def _call():
        return client.messages.create(
            model=LLM_MODEL,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

    response = await run_in_thread(_call)

    answer = response.content[0].text.strip() if response.content else "I couldn't find an answer to that."

    # Save to history and truncate to the last 3 turns (6 interactions)
    _conversation_history.append(("user", question))
    _conversation_history.append(("assistant", answer))
    _conversation_history = _conversation_history[-6:]

    return answer
