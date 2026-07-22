"""Week-1 risk engine: HHI concentration at raw materials, propagated downstream.

This is intentionally store-agnostic — it operates on plain node/edge dicts and
uses NetworkX only for the DAG traversal. Weeks 2+ extend this with geopolitical
event boosts, dependency-weighted edges, inventory buffers and lead-time.
"""
import networkx as nx

# Provisional bands (recalibrated in W2 once the composite score adds
# geopolitical/quality/compliance). HHI > ~25 already means "highly concentrated",
# so concentration-only scores in the 50s warrant a red flag.
LOW_THRESHOLD = 35.0
MED_THRESHOLD = 55.0

# weakest-link emphasis: a node inherits mostly its worst input, partly the spread
MAX_WEIGHT = 0.6
AVG_WEIGHT = 0.4


def band(score: float) -> str:
    if score >= MED_THRESHOLD:
        return "high"
    if score >= LOW_THRESHOLD:
        return "medium"
    return "low"


def hhi(shares: dict[str, float]) -> float:
    """Herfindahl-Hirschman Index over supply shares; range (1/n, 1]."""
    if not shares:
        return 0.0
    total = sum(shares.values()) or 1.0
    return sum((v / total) ** 2 for v in shares.values())


def compute_risk(nodes: list[dict], edges: list[dict]) -> tuple[list[dict], list[dict]]:
    by_id = {n["id"]: dict(n) for n in nodes}

    graph = nx.DiGraph()
    graph.add_nodes_from(by_id)
    for e in edges:
        if e["source"] in by_id and e["target"] in by_id:
            graph.add_edge(e["source"], e["target"], weight=float(e.get("weight", 1.0)))

    # 1) base risk: concentration on raw materials
    base: dict[str, float] = {}
    for nid, n in by_id.items():
        n.setdefault("risk_breakdown", {})
        if n.get("type") == "raw_material" and n.get("country_shares"):
            conc = round(hhi(n["country_shares"]) * 100, 1)
            base[nid] = conc
            n["risk_breakdown"]["concentration"] = conc
        else:
            base[nid] = 0.0

    # 2) propagate upstream -> downstream in topological order
    order = (
        list(nx.topological_sort(graph))
        if nx.is_directed_acyclic_graph(graph)
        else list(by_id)
    )
    risk: dict[str, float] = {}
    for nid in order:
        preds = list(graph.predecessors(nid))
        if not preds:
            risk[nid] = base.get(nid, 0.0)
            continue
        weights = [graph[p][nid].get("weight", 1.0) for p in preds]
        pred_risks = [risk.get(p, 0.0) for p in preds]
        wavg = sum(r * w for r, w in zip(pred_risks, weights)) / (sum(weights) or 1.0)
        propagated = MAX_WEIGHT * max(pred_risks) + AVG_WEIGHT * wavg
        score = round(max(base.get(nid, 0.0), propagated), 1)
        risk[nid] = score
        if propagated > 0:
            by_id[nid]["risk_breakdown"]["propagated"] = round(propagated, 1)

    out_nodes = []
    for nid, n in by_id.items():
        n["risk"] = risk.get(nid, 0.0)
        n["risk_band"] = band(n["risk"])
        out_nodes.append(n)
    return out_nodes, edges
