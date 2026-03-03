from google import genai

from app.config import GEMINI_API_KEY, LLM_MODEL
from app.retrieval.retrieve import retrieve

client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})


async def generate_answer(question: str) -> str:

    #  Retrieve relevant chunks
    docs = retrieve(question, k=3)
    context = "\n\n".join(d["chunk"] for d in docs)

    #  Build grounded prompt
    prompt = f"""You are a document-based assistant.

Answer ONLY using the context below.
If the answer is not in the context, say:
"I cannot find that information in the document."

Context:
{context}

Question:
{question}
"""

    # Generate response
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )


    return response.text


if __name__ == "__main__":
    import asyncio

    test_questions = [
        "Which college is he in??",
        "Is he into robotics?",
        "is he a good coder?",
    ]

    async def main():
        for question in test_questions:
            print(f"\nQ. {question}")
            answer = await generate_answer(question)
            print(f"ANS:- {answer.strip()}")

    asyncio.run(main())