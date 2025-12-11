from typing import Dict, Any, List
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
from datetime import datetime

from .workers.web_search import web_search_agent
from .workers.trials import trials_agent
from .workers.patents import patent_agent
from .workers.iqvia import iqvia_agent
from .workers.exim import exim_agent
from .workers.internal_knowledge import internal_knowledge_agent
from .workers.web_intel import web_intel_agent


class State(TypedDict, total=False):
    query: str
    tasks: List[str]
    i: int
    results: Dict[str, Any]
    agents_used: List[str]
    next: str
    summary: str
    report_data: Dict[str, Any]
    history: List[Dict[str, Any]]


def plan(state: State) -> State:
    q = state["query"].lower()
    tasks: List[str] = []
    if any(k in q for k in ["trial", "phase", "study", "nct", "pipeline"]):
        tasks.append("trials")
    if any(k in q for k in ["patent", "expiry", "fto", "ip", "biosimilar", "generic", "competition"]):
        tasks.append("patent")
    if any(k in q for k in ["market", "sales", "cagr", "iqvia", "market size", "therapy area"]):
        tasks.append("iqvia")
    if any(k in q for k in ["export", "import", "exim", "trade", "sourcing", "dependency"]):
        tasks.append("exim")
    if any(k in q for k in ["internal", "mins", "deck", "strategy", "upload", "pdf", "briefing"]):
        tasks.append("internal_knowledge")
    if any(k in q for k in ["web", "guideline", "news", "forum", "publication", "real-time", "real time", "web search"]):
        tasks.append("web_intel")
    # Always include web search summary for demo richness
    tasks.insert(0, "web_search")

    state["tasks"] = tasks
    state["i"] = 0
    state["results"] = {}
    state["agents_used"] = []
    state["next"] = tasks[0] if tasks else "aggregate"
    return state


def web_node(state: State) -> State:
    q = state["query"]
    res = web_search_agent(q)
    state["results"]["web_search"] = res
    state["agents_used"].append("web_search")
    state["i"] += 1
    state["next"] = state["tasks"][state["i"]] if state["i"] < len(state["tasks"]) else "aggregate"
    return state


def trials_node(state: State) -> State:
    q = state["query"]
    res = trials_agent(q)
    state["results"]["trials"] = res
    state["agents_used"].append("trials")
    state["i"] += 1
    state["next"] = state["tasks"][state["i"]] if state["i"] < len(state["tasks"]) else "aggregate"
    return state


def patent_node(state: State) -> State:
    q = state["query"]
    res = patent_agent(q)
    state["results"]["patent"] = res
    state["agents_used"].append("patent")
    state["i"] += 1
    state["next"] = state["tasks"][state["i"]] if state["i"] < len(state["tasks"]) else "aggregate"
    return state


def iqvia_node(state: State) -> State:
    q = state["query"]
    res = iqvia_agent(q)
    state["results"]["iqvia"] = res
    state["agents_used"].append("iqvia")
    state["i"] += 1
    state["next"] = state["tasks"][state["i"]] if state["i"] < len(state["tasks"]) else "aggregate"
    return state


def exim_node(state: State) -> State:
    q = state["query"]
    res = exim_agent(q)
    state["results"]["exim"] = res
    state["agents_used"].append("exim")
    state["i"] += 1
    state["next"] = state["tasks"][state["i"]] if state["i"] < len(state["tasks"]) else "aggregate"
    return state


def internal_node(state: State) -> State:
    q = state["query"]
    res = internal_knowledge_agent(q)
    state["results"]["internal_knowledge"] = res
    state["agents_used"].append("internal_knowledge")
    state["i"] += 1
    state["next"] = state["tasks"][state["i"]] if state["i"] < len(state["tasks"]) else "aggregate"
    return state


def web_intel_node(state: State) -> State:
    q = state["query"]
    res = web_intel_agent(q)
    state["results"]["web_intel"] = res
    state["agents_used"].append("web_intel")
    state["i"] += 1
    state["next"] = state["tasks"][state["i"]] if state["i"] < len(state["tasks"]) else "aggregate"
    return state


def aggregate(state: State) -> State:
    q = state["query"]
    results = state["results"]

    publications = results.get("web_search", {}).get("publications", [])
    trials = results.get("trials", {}).get("trials", [])
    patents = results.get("patent", {}).get("patents", [])
    iqvia = results.get("iqvia", {}).get("iqvia", {})
    exim = results.get("exim", {}).get("exim", {})
    internal_docs = results.get("internal_knowledge", {}).get("internal_docs", [])
    web_items = results.get("web_intel", {}).get("web_intel", [])

    lines: List[str] = [f"Query: {q}", "", "Findings:"]

    if publications:
        lines.append("- Publications:")
        for p in publications[:3]:
            lines.append(f"  • {p['title']} — {p['journal']} ({p['year']})")

    if trials:
        lines.append("- Clinical Trials:")
        for t in trials[:3]:
            lines.append(f"  • {t['nct_id']} — {t['title']} [{t['phase']}] ({t['status']})")

    if patents:
        lines.append("- Patents:")
        for p in patents[:3]:
            lines.append(f"  • {p['patent_number']} — {p['title']} (exp: {p['expiry']})")

    if iqvia:
        lines.append("- Market Insights (IQVIA):")
        ta = iqvia.get("therapy_area", "")
        cagr = iqvia.get("cagr")
        lines.append(f"  • Therapy area: {ta}; CAGR: {cagr}%")
        competitors = iqvia.get("competitors", [])
        for c in competitors[:3]:
            lines.append(f"  • {c['name']} — share {int(c.get('market_share',0)*100)}%")

    if exim:
        lines.append("- EXIM Trends:")
        dep = exim.get("import_dependency")
        if dep is not None:
            lines.append(f"  • Import dependency: {int(dep*100)}%")
        exporters = exim.get("top_exporters", [])
        for e in exporters[:3]:
            lines.append(f"  • Top exporter: {e['country']} ({e.get('share','')})")

    if internal_docs:
        lines.append("- Internal Knowledge:")
        for d in internal_docs[:3]:
            lines.append(f"  • {d['title']} — {d.get('summary','')[:80]}")

    if web_items:
        lines.append("- Web Intelligence:")
        for w in web_items[:3]:
            lines.append(f"  • {w['source']} — {w['summary'][:80]} ({w['url']})")

    # Clarification prompts to support conversation flow
    clarifications: List[str] = []
    ql = q.lower()
    if any(k in ql for k in ["unmet need", "opportunity", "whitespace"]) and not any(r in ql for r in ["us", "eu", "europe", "india", "china", "apac", "emea", "region", "global"]):
        clarifications.append("Do you want the assessment by region (US/EU/APAC) or global?")
    if any(k in ql for k in ["competition", "competitor", "biosimilar"]) and not any(k in ql for k in ["moa", "mechanism", "class", "molecule", "drug", "brand"]):
        clarifications.append("Should we scope competition by molecule, class/MoA, or brand?")
    if ("market" in ql or "sales" in ql) and not any(k in ql for k in ["year", "2022", "2023", "2024", "2025"]):
        clarifications.append("Which time horizon should we analyze (last 3y, 5y CAGR, or forecast)?")

    insights: List[str] = []
    try:
        burden = iqvia.get("burden_index", 0)
        if burden and burden > 0.7 and len(trials) < 3:
            insights.append("Whitespace: High disease burden with low trial activity")
    except Exception:
        pass
    try:
        from datetime import date
        now = datetime.utcnow().date()
        for p in patents:
            exp = p.get("expiry")
            if not exp:
                continue
            exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            days = (exp_date - now).days
            if 0 < days <= 730:
                yrs = round(days/365, 1)
                insights.append(f"Biosimilar opportunity: {p['patent_number']} expires in ~{yrs} years")
                break
    except Exception:
        pass
    try:
        dep = exim.get("import_dependency")
        if dep and dep >= 0.6:
            insights.append("Supply risk: High import dependency (>60%)")
    except Exception:
        pass

    if clarifications:
        lines.append("- Clarifications:")
        for c in clarifications:
            lines.append(f"  • {c}")

    if insights:
        lines.append("- Insights and Flags:")
        for it in insights:
            lines.append(f"  • {it}")

    state["summary"] = "\n".join(lines)
    state["report_data"] = {
        "query": q,
        "publications": publications,
        "trials": trials,
        "patents": patents,
        "iqvia": iqvia,
        "exim": exim,
        "internal_docs": internal_docs,
        "web_intel": web_items,
        "clarifications": clarifications,
        "insights": insights,
    }
    return state


async def run_workflow(query: str, history: List[Dict[str, Any]]):
    graph = StateGraph(State)
    graph.add_node("plan", plan)
    graph.add_node("web_search", web_node)
    graph.add_node("trials", trials_node)
    graph.add_node("patent", patent_node)
    graph.add_node("iqvia", iqvia_node)
    graph.add_node("exim", exim_node)
    graph.add_node("internal_knowledge", internal_node)
    graph.add_node("web_intel", web_intel_node)
    graph.add_node("aggregate", aggregate)

    graph.set_entry_point("plan")

    def router(state: State):
        return state.get("next", "aggregate")

    mapping = {
        "web_search": "web_search",
        "trials": "trials",
        "patent": "patent",
        "iqvia": "iqvia",
        "exim": "exim",
        "internal_knowledge": "internal_knowledge",
        "web_intel": "web_intel",
        "aggregate": "aggregate",
    }
    graph.add_conditional_edges("plan", router, mapping)
    graph.add_conditional_edges("web_search", router, mapping)
    graph.add_conditional_edges("trials", router, mapping)
    graph.add_conditional_edges("patent", router, mapping)
    graph.add_conditional_edges("iqvia", router, mapping)
    graph.add_conditional_edges("exim", router, mapping)
    graph.add_conditional_edges("internal_knowledge", router, mapping)
    graph.add_conditional_edges("web_intel", router, mapping)

    app = graph.compile()
    final: State = app.invoke({"query": query, "history": history})
    return final
