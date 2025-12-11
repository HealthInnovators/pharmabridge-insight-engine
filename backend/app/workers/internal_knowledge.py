from typing import Dict, Any
from ..mock_data.loader import load_mock


def internal_knowledge_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    internal_docs = data.get("internal_docs", [])
    return {"internal_docs": internal_docs}
