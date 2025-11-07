from typing import Dict, Any
from ..mock_data.loader import load_mock


def trials_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    trials = data.get("trials", [])
    return {"trials": trials}
