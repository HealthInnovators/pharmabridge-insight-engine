import os
from typing import Any, Dict, List, Optional

import httpx


def _is_configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def llm_provider_name() -> str:
    if _is_configured():
        return "groq"
    return "none"


async def generate_chat_response(
    *,
    query: str,
    history: List[Dict[str, Any]],
    report_data: Dict[str, Any],
    fallback_text: str,
) -> str:
    """Generate assistant markdown.

    - Uses Groq OpenAI-compatible endpoint if GROQ_API_KEY is set.
    - Otherwise returns fallback_text.

    Important: The prompt strictly instructs the model to only use provided report_data.
    """

    if not _is_configured():
        return fallback_text

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    system = (
        "You are PharmaBridge Insight Engine, an analyst assistant for pharmaceutical intelligence. "
        "You MUST only use the provided structured data (report_data) as your source of truth. "
        "If a detail is missing from report_data, explicitly say it is not available. "
        "Do NOT fabricate citations, numbers, trial IDs, PMIDs, or claims. "
        "Always start your response with a 'Data Sources' section derived from report_data.sources. "
        "If report_data.sources indicates a section is 'mock', label it as demo/placeholder data. "
        "If the user's query is about a specific molecule/indication but report_data content appears to be about a different topic, explicitly flag a scope mismatch instead of claiming relevance. "
        "Answer in concise, professional markdown with clear section headings. "
        "When possible, include citations as links using fields already present in report_data (e.g., publication url, trial url)."
    )

    user_payload = {
        "query": query,
        "report_data": report_data,
    }

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                "Using the following JSON as the only source, write the response. "
                "Include: Findings summary, key evidence bullets per section, and clarifications if present.\n\n"
                f"{user_payload}"
            ),
        },
    ]

    timeout_s = float(os.getenv("GROQ_TIMEOUT_S", "30"))

    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            r = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": float(os.getenv("GROQ_TEMPERATURE", "0.2")),
                    "max_tokens": int(os.getenv("GROQ_MAX_TOKENS", "900")),
                },
            )
            r.raise_for_status()
            data = r.json()
            return (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", fallback_text)
            )
    except Exception:
        return fallback_text
