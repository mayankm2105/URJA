"""Composite supply-chain risk engine.

Per-node risk fuses three dimensions:
  - concentration : HHI over a raw material's global country shares
  - geopolitical  : country-risk baseline (share-weighted for raw materials)
  - event         : transient boosts from active disruption signals
Risk then propagates downstream along the BOM DAG (dependency-weighted,
weakest-link emphasis). Lead-time-to-impact for each product is the minimum
buffer-day path from any shocked upstream node to that product.

Deterministic and store-agnostic — operates on plain node/edge dicts.
"""
from __future__ import annotations

import networkx as nx

from .concentration import band, hhi  # noqa: F401  (band/hhi reused)
from .country_risk import country_risk, geo_from_shares

CONCENTRATION_WEIGHT = 0.55
GEOPOLITICAL_WEIGHT = 0.45
SUPPLIER_GEO_SCALE = 0.7

MAX_PROP_WEIGHT = 0.6  # weakest-link emphasis
AVG_PROP_WEIGHT = 0.4

ALERT_DELTA = 1.0  # min risk increase for a product to raise an alert


def static_risk(node: dict) -> float:
    """Event-independent base risk for a node."""
    node.setdefault("risk_breakdown", {})
    t = node.get("type")
    if t == "raw_material":
        conc = round(hhi(node.get("country_shares") or {}) * 100, 1)
        geo = round(geo_from_shares(node.get("country_shares")), 1)
        node["risk_breakdown"]["concentration"] = conc
        node["risk_breakdown"]["geopolitical"] = geo
        return round(CONCENTRATION_WEIGHT * conc + GEOPOLITICAL_WEIGHT * geo, 1)
    if t == "supplier":
        geo = round(country_risk(node.get("country")) * SUPPLIER_GEO_SCALE, 1)
        node["risk_breakdown"]["geopolitical"] = geo
        return geo
    if t == "country":
        geo = round(country_risk(node.get("label")), 1)
        node["risk_breakdown"]["geopolitical"] = geo
        return geo
    return 0.0


def _build_graph(by_id: dict, edges: list[dict]) -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_nodes_from(by_id)
    for e in edges:
        if e["source"] in by_id and e["target"] in by_id:
            graph.add_edge(
                e["source"],
                e["target"],
                dep=float(e.get("dependency", 1.0)),
                buf=float(e.get("buffer_days", 0.0)),
            )
    return graph


def compute_node_risk(
    nodes: list[dict], edges: list[dict], event_boosts: dict[str, float] | None = None
) -> tuple[list[dict], nx.DiGraph, dict]:
    event_boosts = event_boosts or {}
    by_id = {n["id"]: dict(n) for n in nodes}
    graph = _build_graph(by_id, edges)

    base: dict[str, float] = {}
    for nid, n in by_id.items():
        n.setdefault("risk_breakdown", {})
        s = static_risk(n)
        boost = float(event_boosts.get(nid, 0.0))
        if boost:
            n["risk_breakdown"]["event"] = round(boost, 1)
        base[nid] = min(100.0, s + boost)

    order = (
        list(nx.topological_sort(graph))
        if nx.is_directed_acyclic_graph(graph)
        else list(by_id)
    )
    risk: dict[str, float] = {}
    for nid in order:
        preds = list(graph.predecessors(nid))
        if not preds:
            risk[nid] = round(base.get(nid, 0.0), 1)
            continue
        deps = [graph[p][nid].get("dep", 1.0) for p in preds]
        pred_risks = [risk.get(p, 0.0) for p in preds]
        wavg = sum(r * d for r, d in zip(pred_risks, deps)) / (sum(deps) or 1.0)
        propagated = MAX_PROP_WEIGHT * max(pred_risks) + AVG_PROP_WEIGHT * wavg
        risk[nid] = round(max(base.get(nid, 0.0), propagated), 1)

    out_nodes = []
    for nid, n in by_id.items():
        n["risk"] = risk.get(nid, 0.0)
        n["risk_band"] = band(n["risk"])
        out_nodes.append(n)
    return out_nodes, graph, by_id


def product_lead_times(
    graph: nx.DiGraph, by_id: dict, shocked_ids: list[str]
) -> dict[str, dict]:
    """For each product, the minimum buffer-day path from any shocked node."""
    products = [nid for nid, n in by_id.items() if n.get("type") == "product"]
    result: dict[str, dict] = {}
    for product in products:
        best = None
        for shock in shocked_ids:
            if shock == product or not graph.has_node(shock):
                continue
            if nx.has_path(graph, shock, product):
                days = nx.shortest_path_length(graph, shock, product, weight="buf")
                if best is None or days < best[0]:
                    path = nx.shortest_path(graph, shock, product, weight="buf")
                    best = (days, shock, path)
        if best:
            result[product] = {
                "lead_time_days": round(best[0], 1),
                "via": best[1],
                "path": best[2],
            }
    return result
