import anthropic
from typing import List, Dict
from app.config import ANTHROPIC_API_KEY, LLM_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def rerank(query: str, results: List[Dict]) -> List[Dict]:
    """
    Rerank retrieved chunks by relevance to the query using the LLM.

    Each item in `results` is {"chunk": str, "score": float}.
    Returns the list sorted from most to least relevant.
    """
    if not results:
        return results

    # Build a single prompt that asks the LLM to rank indices by relevance
    chunks_text = "\n\n".join(
        f"[{i}] {r['chunk']}" for i, r in enumerate(results)
    )

    prompt = f"""You are a relevance ranker. Given a user query and a list of text chunks,
return a comma-separated list of the chunk indices sorted from most to least relevant.
Output ONLY the comma-separated indices — no explanation, no extra text.

Query: {query}

Chunks:
{chunks_text}

Ranked indices (most to least relevant):"""

    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=128,
            messages=[{"role": "user", "content": prompt}]
        )

        ranked_indices = [
            int(idx.strip())
            for idx in response.content[0].text.strip().split(",")
            if idx.strip().isdigit()
        ]
        # Keep only valid indices and append any missing ones at the end
        seen = set()
        ordered = []
        for idx in ranked_indices:
            if 0 <= idx < len(results) and idx not in seen:
                ordered.append(results[idx])
                seen.add(idx)
        for idx in range(len(results)):
            if idx not in seen:
                ordered.append(results[idx])
        return ordered
    except Exception:
        # Fall back to original FAISS score ordering
        return results
