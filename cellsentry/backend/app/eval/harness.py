"""Evaluation harness — produces the headline metrics for the deck.

  * lead_time    : detection-to-impact lead time over the event corpus
  * attribution  : are the right products flagged for each event? (precision/recall)
  * quality      : SPC defect detection vs ground truth (precision/recall/F1)

All deterministic and runnable headless (no API key needed).
"""
from __future__ import annotations

import networkx as nx

from ..agents.pipeline import run_scenario
from ..data.events import EVENTS
from ..graph.store import get_store
from ..quality.inspection import generate_lots
from ..quality.spc import flag_lots
from ..risk import engine

DERISK = {"price_down", "supply_up"}


def _risk_event_ids() -> list[str]:
    return [e["id"] for e in EVENTS if e["extracted"]["direction"] not in DERISK]


def _expected_products(material_labels: list[str], by_id: dict, edges: list[dict]) -> set:
    graph = nx.DiGraph()
    graph.add_nodes_from(by_id)
    for e in edges:
        if e["source"] in by_id and e["target"] in by_id:
            graph.add_edge(e["source"], e["target"])
    products = [nid for nid, n in by_id.items() if n.get("type") == "product"]
    rm = {nid: n["label"].lower() for nid, n in by_id.items() if n.get("type") == "raw_material"}
    expected: set = set()
    for ml in material_labels:
        m = ml.lower()
        rid = next((nid for nid, lbl in rm.items() if m in lbl or lbl in m), None)
        if not rid:
            continue
        for p in products:
            if nx.has_path(graph, rid, p):
                expected.add(p)
    return expected


def evaluate_lead_time() -> dict:
    risk_events = _risk_event_ids()
    leads: list[float] = []
    events_with_alerts = 0
    total_alerts = 0
    for eid in risk_events:
        res = run_scenario([eid], generate_briefs=False)
        if res.alerts:
            events_with_alerts += 1
            total_alerts += len(res.alerts)
            leads += [a.lead_time_days for a in res.alerts if a.lead_time_days is not None]
    leads.sort()
    median = leads[len(leads) // 2] if leads else None
    return {
        "risk_events": len(risk_events),
        "events_with_alerts": events_with_alerts,
        "total_alerts": total_alerts,
        "median_lead_days": median,
        "mean_lead_days": round(sum(leads) / len(leads), 1) if leads else None,
        "min_lead_days": min(leads) if leads else None,
        "max_lead_days": max(leads) if leads else None,
        "reactive_baseline_days": 0,
    }


def evaluate_attribution() -> dict:
    nodes, edges = get_store().get_graph()
    nodes, _, by_id = engine.compute_node_risk(nodes, edges, None)
    tp = fp = fn = 0
    for e in EVENTS:
        x = e["extracted"]
        if x["direction"] in DERISK:
            continue
        expected = _expected_products(x["materials"], by_id, edges)
        if not expected:
            continue
        actual = {a.product_id for a in run_scenario([e["id"]], generate_briefs=False).alerts}
        tp += len(expected & actual)
        fp += len(actual - expected)
        fn += len(expected - actual)
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(prec, 3), "recall": round(rec, 3)}


def evaluate_quality() -> dict:
    flags = flag_lots(generate_lots())
    tp = fp = fn = tn = 0
    for l in flags:
        pred, truth = l["flagged"], l["true_defect"]
        if pred and truth:
            tp += 1
        elif pred and not truth:
            fp += 1
        elif not pred and truth:
            fn += 1
        else:
            tn += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "lots": len(flags),
        "defective": tp + fn,
        "flagged": tp + fp,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(prec, 3),
        "recall": round(rec, 3),
        "f1": round(f1, 3),
    }


def run_all() -> dict:
    return {
        "lead_time": evaluate_lead_time(),
        "attribution": evaluate_attribution(),
        "quality": evaluate_quality(),
    }
