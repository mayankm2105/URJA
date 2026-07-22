"""Scenario orchestrator: apply events to the graph, recompute risk + lead time,
and emit per-product alerts with briefs."""
from __future__ import annotations

import networkx as nx

from ..data.events import EVENTS_BY_ID
from ..graph.store import get_store
from ..models.schema import Alert, Edge, Node, ScenarioResponse
from ..risk import engine
from ..risk.engine import ALERT_DELTA
from .briefing import alternative_recommendations, generate_brief
from .extraction import resolve_event_mapping
from .llm import get_client

DERISK_DIRECTIONS = {"price_down", "supply_up"}


def _match_node(name: str, by_id: dict, node_type: str) -> str | None:
    nl = name.lower().strip()
    if not nl:
        return None
    first = nl.split()[0]
    for nid, n in by_id.items():
        if n.get("type") != node_type:
            continue
        ln = n["label"].lower()
        if nl in ln or ln in nl or first in ln:
            return nid
    return None


def _boosts_from_mapping(mapping: dict, by_id: dict) -> dict[str, float]:
    severity = float(mapping.get("severity", 0))
    if mapping.get("direction") in DERISK_DIRECTIONS:
        severity = 0.0
    boosts: dict[str, float] = {}
    if severity <= 0:
        return boosts
    for name in mapping.get("materials", []):
        nid = _match_node(name, by_id, "raw_material")
        if nid:
            boosts[nid] = max(boosts.get(nid, 0.0), severity)
    for name in mapping.get("suppliers", []):
        nid = _match_node(name, by_id, "supplier")
        if nid:
            boosts[nid] = max(boosts.get(nid, 0.0), severity)
    return boosts


def run_scenario(event_ids: list[str], generate_briefs: bool = True) -> ScenarioResponse:
    store = get_store()
    nodes, edges = store.get_graph()

    baseline_nodes, _, base_by_id = engine.compute_node_risk(nodes, edges, None)
    baseline_risk = {n["id"]: n["risk"] for n in baseline_nodes}

    boosts: dict[str, float] = {}
    applied: list[str] = []
    node_triggers: dict[str, set] = {}
    for eid in event_ids:
        ev = EVENTS_BY_ID.get(eid)
        if not ev:
            continue
        applied.append(eid)
        mapping = resolve_event_mapping(ev)
        for nid, b in _boosts_from_mapping(mapping, base_by_id).items():
            boosts[nid] = max(boosts.get(nid, 0.0), b)
            node_triggers.setdefault(nid, set()).add(eid)

    scen_nodes, graph, by_id = engine.compute_node_risk(nodes, edges, boosts)
    shocked = [nid for nid, b in boosts.items() if b > 0]
    lead = engine.product_lead_times(graph, by_id, shocked)

    for n in scen_nodes:
        n["baseline_risk"] = baseline_risk.get(n["id"])
        if n["id"] in lead:
            n["lead_time_days"] = lead[n["id"]]["lead_time_days"]

    alerts: list[Alert] = []
    for n in scen_nodes:
        if n["type"] != "product":
            continue
        bl = baseline_risk.get(n["id"], 0.0)
        delta = round(n["risk"] - bl, 1)
        if delta < ALERT_DELTA:
            continue
        info = lead.get(n["id"])
        path_ids = info["path"] if info else []
        path_labels = [by_id[x]["label"] for x in path_ids]
        via = by_id[info["via"]]["label"] if info else None
        lt = info["lead_time_days"] if info else None

        trig: set = set()
        rm_nodes: list[str] = []
        for s in shocked:
            if nx.has_path(graph, s, n["id"]):
                trig |= node_triggers.get(s, set())
                if by_id[s].get("type") == "raw_material":
                    rm_nodes.append(s)
        headlines = [EVENTS_BY_ID[e]["headline"] for e in sorted(trig) if e in EVENTS_BY_ID]
        recs = alternative_recommendations(rm_nodes, by_id, lt)
        ctx = {
            "product_label": n["label"],
            "scenario_risk": n["risk"],
            "baseline_risk": bl,
            "lead_time_days": lt,
            "path_labels": path_labels,
            "headlines": headlines,
            "recommendations": recs,
        }
        brief = generate_brief(ctx) if generate_briefs else ""
        alerts.append(
            Alert(
                product_id=n["id"],
                product_label=n["label"],
                scenario_risk=n["risk"],
                baseline_risk=bl,
                delta=delta,
                risk_band=n["risk_band"],
                lead_time_days=lt,
                path_labels=path_labels,
                via_label=via,
                triggering_event_ids=sorted(trig),
                triggering_headlines=headlines,
                recommendations=recs,
                brief=brief,
            )
        )

    alerts.sort(key=lambda a: -a.delta)
    return ScenarioResponse(
        nodes=[Node(**n) for n in scen_nodes],
        edges=[Edge(**e) for e in edges],
        alerts=alerts,
        events_applied=applied,
        meta={
            "node_count": len(scen_nodes),
            "edge_count": len(edges),
            "alert_count": len(alerts),
            "shocked_nodes": len(shocked),
            "llm_enabled": get_client() is not None,
        },
    )
