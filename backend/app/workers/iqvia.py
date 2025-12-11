from typing import Dict, Any
from ..mock_data.loader import load_mock


def iqvia_agent(query: str) -> Dict[str, Any]:
    data = load_mock(query)
    iqvia = data.get("iqvia", {})
    return {"iqvia": iqvia}
