from typing import Dict, Any
from ..mock_data.loader import load_mock


def patent_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    patents = data.get("patents", [])
    return {"patents": patents}
