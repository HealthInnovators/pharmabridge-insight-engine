from typing import Dict, Any
from ..mock_data.loader import load_mock


def web_intel_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    web = data.get("web_intel", [])
    return {"web_intel": web}
