from typing import Dict, Any
from datetime import datetime
from ..mock_data.loader import load_mock


def web_intel_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    web = data.get("web_intel", [])
    return {
        "web_intel": web,
        "_meta": {"source": "mock", "fetched_at": datetime.utcnow().isoformat() + "Z"},
    }
