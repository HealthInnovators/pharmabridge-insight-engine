import json
import os
from typing import Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "samples")

KNOWN_KEYS = {
    "semaglutide": ["semaglutide", "ozempic", "wegovy"],
    "tirzepatide": ["tirzepatide", "mounjaro", "zepbound"],
    "donanemab": ["donanemab"],
    "sildenafil": ["sildenafil", "viagra", "revatio"],
}


def detect_key(query: str) -> str:
    q = query.lower()
    for key, aliases in KNOWN_KEYS.items():
        for alias in aliases:
            if alias in q:
                return key
    return "generic"


def load_mock(query: str) -> Dict[str, Any]:
    key = detect_key(query)
    path = os.path.join(DATA_DIR, f"{key}.json")
    if not os.path.exists(path):
        return {
            "publications": [],
            "trials": [],
            "patents": [],
            "iqvia": {},
            "exim": {},
            "internal_docs": [],
            "web_intel": [],
        }
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
