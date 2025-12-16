from typing import Dict, Any
from datetime import datetime
from ..mock_data.loader import load_mock


def exim_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    exim = data.get("exim", {})
    return {
        "exim": exim,
        "_meta": {"source": "mock", "fetched_at": datetime.utcnow().isoformat() + "Z"},
    }
