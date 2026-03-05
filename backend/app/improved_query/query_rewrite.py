from google import genai
from app.config import GEMINI_API_KEY, LLM_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)


def rewrite_query(query: str) -> str:
    """
    Rewrite vague user queries into clear document-search queries.
    """

    prompt = f"""
Rewrite the user's question so it becomes a clear search query
for retrieving information from a document.

Rules:
- Keep the meaning identical
- Expand vague references
- Do NOT answer the question

Examples:

User: what about the second one
Search Query: explain the second project mentioned in the document

User: traffic project
Search Query: explain the traffic management project in the document

User Question:
{query}

Search Query:
"""

    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )

    return response.text.strip()