from typing import Dict, Any, List
from langgraph.graph import StateGraph
from typing_extensions import TypedDict

from .workers.web_search import web_search_agent
from .workers.trials import trials_agent
from .workers.patents import patent_agent


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
    if any(k in q for k in ["trial", "phase", "study", "nct"]):
        tasks.append("trials")
    if any(k in q for k in ["patent", "expiry", "fto", "ip"]):
        tasks.append("patent")
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


def aggregate(state: State) -> State:
    q = state["query"]
    results = state["results"]

    publications = results.get("web_search", {}).get("publications", [])
    trials = results.get("trials", {}).get("trials", [])
    patents = results.get("patent", {}).get("patents", [])

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

    state["summary"] = "\n".join(lines)
    state["report_data"] = {
        "query": q,
        "publications": publications,
        "trials": trials,
        "patents": patents,
    }
    return state


async def run_workflow(query: str, history: List[Dict[str, Any]]):
    graph = StateGraph(State)
    graph.add_node("plan", plan)
    graph.add_node("web_search", web_node)
    graph.add_node("trials", trials_node)
    graph.add_node("patent", patent_node)
    graph.add_node("aggregate", aggregate)

    graph.set_entry_point("plan")

    def router(state: State):
        return state.get("next", "aggregate")

    graph.add_conditional_edges("plan", router, {"web_search": "web_search", "trials": "trials", "patent": "patent", "aggregate": "aggregate"})
    graph.add_conditional_edges("web_search", router, {"web_search": "web_search", "trials": "trials", "patent": "patent", "aggregate": "aggregate"})
    graph.add_conditional_edges("trials", router, {"web_search": "web_search", "trials": "trials", "patent": "patent", "aggregate": "aggregate"})
    graph.add_conditional_edges("patent", router, {"web_search": "web_search", "trials": "trials", "patent": "patent", "aggregate": "aggregate"})

    app = graph.compile()
    final: State = app.invoke({"query": query, "history": history})
    return final
