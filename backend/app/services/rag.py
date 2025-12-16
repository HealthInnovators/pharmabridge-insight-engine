import os
import re
from typing import Any, Dict, List, Tuple


_INTERNAL_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "internal_docs")


def _tokenize(text: str) -> List[str]:
    return [t for t in re.split(r"[^a-zA-Z0-9]+", text.lower()) if t]


def _score(query_tokens: List[str], doc_tokens: List[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    q = set(query_tokens)
    d = set(doc_tokens)
    inter = q.intersection(d)
    if not inter:
        return 0.0
    return len(inter) / max(1, len(q))


def _read_doc(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def retrieve_internal_docs(query: str, k: int = 3) -> List[Dict[str, Any]]:
    os.makedirs(_INTERNAL_DIR, exist_ok=True)

    query_tokens = _tokenize(query)
    candidates: List[Tuple[float, str, str]] = []

    for name in os.listdir(_INTERNAL_DIR):
        if not (name.lower().endswith(".txt") or name.lower().endswith(".md")):
            continue
        path = os.path.join(_INTERNAL_DIR, name)
        if not os.path.isfile(path):
            continue
        text = _read_doc(path)
        doc_tokens = _tokenize(text)
        s = _score(query_tokens, doc_tokens)
        if s > 0:
            candidates.append((s, name, text))

    candidates.sort(key=lambda x: x[0], reverse=True)
    out: List[Dict[str, Any]] = []

    for s, name, text in candidates[:k]:
        snippet = re.sub(r"\s+", " ", text).strip()
        if len(snippet) > 400:
            snippet = snippet[:400] + "..."
        out.append({"title": name, "summary": snippet, "score": round(s, 3)})

    return out
