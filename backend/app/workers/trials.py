from typing import Dict, Any, List, Optional
from datetime import datetime
import os

import httpx

from ..mock_data.loader import load_mock
from ..mock_data.loader import detect_key


def _first_str(v: Any) -> Optional[str]:
    if isinstance(v, str) and v.strip():
        return v.strip()
    if isinstance(v, list) and v:
        for item in v:
            if isinstance(item, str) and item.strip():
                return item.strip()
    return None


def _ctgov_fetch(query: str, page_size: int = 5) -> List[Dict[str, Any]]:
    term = query.strip()
    if not term:
        return []

    timeout_s = float(os.getenv("CTGOV_TIMEOUT_S", "10"))

    with httpx.Client(timeout=timeout_s) as client:
        r = client.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params={
                "query.term": term,
                "pageSize": str(page_size),
                "countTotal": "false",
            },
        )
        r.raise_for_status()
        data = r.json()

    studies = data.get("studies", [])
    if not isinstance(studies, list):
        return []

    out: List[Dict[str, Any]] = []
    for s in studies:
        ps = (s or {}).get("protocolSection", {})
        idmod = (ps or {}).get("identificationModule", {})
        statusmod = (ps or {}).get("statusModule", {})
        designmod = (ps or {}).get("designModule", {})
        sponsmod = (ps or {}).get("sponsorCollaboratorsModule", {})

        nct = _first_str(idmod.get("nctId")) or _first_str(idmod.get("orgStudyId"))
        title = _first_str(idmod.get("briefTitle")) or _first_str(idmod.get("officialTitle"))
        status = _first_str(statusmod.get("overallStatus"))
        phases = designmod.get("phases")
        phase = _first_str(phases)

        sponsor = None
        lead = sponsmod.get("leadSponsor")
        if isinstance(lead, dict):
            sponsor = _first_str(lead.get("name"))

        completion_date = None
        cds = statusmod.get("completionDateStruct")
        if isinstance(cds, dict):
            completion_date = _first_str(cds.get("completionDate"))

        if not nct or not title:
            continue

        out.append(
            {
                "nct_id": nct,
                "title": title,
                "status": status or "N/A",
                "phase": phase or "N/A",
                "completion_date": completion_date or "N/A",
                "sponsor": sponsor or "N/A",
                "url": f"https://clinicaltrials.gov/study/{nct}",
            }
        )

    return out


def trials_agent(query: str) -> Dict[str, Any]:
    page_size = int(os.getenv("CTGOV_PAGE_SIZE", "5"))
    key = detect_key(query)
    term = key if key != "generic" else query
    try:
        trials = _ctgov_fetch(term, page_size=page_size)
        if trials:
            return {
                "trials": trials,
                "_meta": {
                    "source": "clinicaltrials_gov_api",
                    "fetched_at": datetime.utcnow().isoformat() + "Z",
                    "query_term": term,
                },
            }
    except Exception:
        pass

    data = load_mock(query)
    trials = data.get("trials", [])
    return {
        "trials": trials,
        "_meta": {"source": "mock", "fetched_at": datetime.utcnow().isoformat() + "Z", "query_term": term},
    }
