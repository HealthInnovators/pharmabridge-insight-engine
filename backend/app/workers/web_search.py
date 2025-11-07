from typing import Dict, Any
from ..mock_data.loader import load_mock


def web_search_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    pubs = data.get("publications", [])
    return {"publications": pubs}
