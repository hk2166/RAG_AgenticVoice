from google import genai

from app.config import GEMINI_API_KEY, LLM_MODEL
from app.retrieval.retrieve import retrieve

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


async def generate_answer(question: str) -> str:

    #  Retrieve relevant chunks
    docs = retrieve(question, k=5)
    context = "\n\n".join(d["chunk"] for d in docs)


    #  Build grounded prompt
    prompt = f"""You are a helpful assistant that answers questions based on a document.

Use the context below to answer the question. You may reason, summarize, and synthesize 
information from the context — do not just quote it verbatim.

Rules:
- Base your answer on the context provided.
- If listing projects, return only project names (no links, no URLs, no "(Github)" or "(Demo)").
- Keep answers concise and clear.
- If the context genuinely does not contain enough information to answer, say:
  "I cannot find that information in the document."

Context:
{context}

Question: {question}

Answer:"""

    # Generate response
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )
    return response.text