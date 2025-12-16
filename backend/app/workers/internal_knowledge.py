from typing import Dict, Any

from ..mock_data.loader import load_mock
from ..services.rag import retrieve_internal_docs


def internal_knowledge_agent(query: str) -> Dict[str, Any]:
    try:
        docs = retrieve_internal_docs(query, k=3)
        if docs:
            return {"internal_docs": docs}
    except Exception:
        pass

    data = load_mock(query)
    internal_docs = data.get("internal_docs", [])
    return {"internal_docs": internal_docs}
