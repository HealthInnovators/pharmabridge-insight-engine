from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import re

import httpx

from ..mock_data.loader import load_mock
from ..mock_data.loader import detect_key


def _extract_year(text: str) -> Optional[int]:
    if not text:
        return None
    m = re.search(r"(19|20)\d{2}", text)
    if not m:
        return None
    try:
        return int(m.group(0))
    except Exception:
        return None


def _pubmed_fetch(query: str, retmax: int = 5) -> List[Dict[str, Any]]:
    term = query.strip()
    if not term:
        return []

    timeout_s = float(os.getenv("PUBMED_TIMEOUT_S", "8"))

    with httpx.Client(timeout=timeout_s) as client:
        esearch = client.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": term, "retmax": str(retmax), "retmode": "json"},
        )
        esearch.raise_for_status()
        ids = (
            esearch.json()
            .get("esearchresult", {})
            .get("idlist", [])
        )

        if not ids:
            return []

        esummary = client.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
            params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
        )
        esummary.raise_for_status()
        data = esummary.json().get("result", {})

        pubs: List[Dict[str, Any]] = []
        for pmid in ids:
            item = data.get(pmid, {})
            title = (item.get("title") or "").strip().rstrip(".")
            journal = (item.get("fulljournalname") or item.get("source") or "").strip()
            pubdate = (item.get("pubdate") or item.get("sortpubdate") or "").strip()
            year = _extract_year(pubdate)
            if not title:
                continue
            pubs.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "journal": journal or "PubMed",
                    "year": year or "N/A",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                }
            )
        return pubs


def web_search_agent(query: str) -> Dict[str, Any]:
    retmax = int(os.getenv("PUBMED_RETMAX", "5"))
    key = detect_key(query)
    term = key if key != "generic" else query
    try:
        pubs = _pubmed_fetch(term, retmax=retmax)
        if pubs:
            return {
                "publications": pubs,
                "_meta": {
                    "source": "pubmed_api",
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "query_term": term,
                },
            }
    except Exception:
        pass

    data = load_mock(query)
    pubs = data.get("publications", [])
    return {
        "publications": pubs,
        "_meta": {"source": "mock", "fetched_at": datetime.utcnow().isoformat() + "Z", "query_term": term},
    }
