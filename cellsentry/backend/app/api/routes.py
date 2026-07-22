"""API routes."""
from fastapi import APIRouter

from ..agents.pipeline import run_scenario
from ..config import get_settings
from ..data.events import EVENTS
from ..graph.store import get_store
from ..models.schema import (
    Edge,
    Event,
    EventSource,
    GraphResponse,
    Node,
    ScenarioRequest,
    ScenarioResponse,
)
from ..risk import engine
from ..quality.inspection import generate_lots, trace_lot
from ..quality.spc import control_limits, flag_lots, supplier_status
from ..eval.harness import run_all

router = APIRouter()


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "graph_backend": "neo4j" if settings.use_neo4j else "memory",
        "llm_enabled": bool(settings.anthropic_api_key),
    }


@router.get("/graph", response_model=GraphResponse)
def get_graph() -> GraphResponse:
    """Baseline supply graph with composite risk (no active events)."""
    store = get_store()
    nodes, edges = store.get_graph()
    out, _, _ = engine.compute_node_risk(nodes, edges, None)
    for n in out:
        n["baseline_risk"] = n["risk"]
    return GraphResponse(
        nodes=[Node(**n) for n in out],
        edges=[Edge(**e) for e in edges],
        meta={"node_count": len(out), "edge_count": len(edges)},
    )


@router.get("/events", response_model=list[Event])
def list_events() -> list[Event]:
    out = []
    for e in EVENTS:
        x = e["extracted"]
        out.append(
            Event(
                id=e["id"],
                date=e["date"],
                headline=e["headline"],
                body=e["body"],
                source=EventSource(**e["source"]),
                event_type=x["event_type"],
                severity=x["severity"],
                direction=x["direction"],
                materials=x["materials"],
                countries=x["countries"],
                suppliers=x["suppliers"],
            )
        )
    return out


@router.post("/scenario", response_model=ScenarioResponse)
def scenario(req: ScenarioRequest) -> ScenarioResponse:
    """Apply the given events, recompute risk + lead time, return alerts + briefs."""
    return run_scenario(req.event_ids, req.generate_briefs)


@router.get("/quality")
def quality() -> dict:
    """Incoming cell-inspection SPC: per-supplier drift status + flagged lots
    with cell->pack->vehicle traceability."""
    raw = generate_lots()
    lots = flag_lots(raw)
    flagged = [l for l in lots if l["flagged"]]
    return {
        "suppliers": supplier_status(lots),
        "limits": control_limits(raw),
        # Full inspection series so the UI can draw the actual control chart,
        # not just the exceptions.
        "lots": [
            {
                "lot_id": l["lot_id"],
                "supplier_id": l["supplier_id"],
                "supplier": l["supplier"],
                "day": l["day"],
                "capacity_mah": l["capacity_mah"],
                "ir_mohm": l["ir_mohm"],
                "flagged": l["flagged"],
                "true_defect": l["true_defect"],
            }
            for l in sorted(lots, key=lambda x: x["day"])
        ],
        "lot_count": len(lots),
        "flagged_count": len(flagged),
        "flagged": [
            {
                "lot_id": l["lot_id"],
                "supplier": l["supplier"],
                "day": l["day"],
                "capacity_mah": l["capacity_mah"],
                "ir_mohm": l["ir_mohm"],
                "reasons": l["reasons"],
                "trace": trace_lot(l),
            }
            for l in flagged
        ],
    }


@router.get("/eval")
def evaluation() -> dict:
    """Evaluation metrics: lead-time, product attribution, quality precision/recall."""
    return run_all()


@router.post("/seed")
def seed() -> dict:
    store = get_store()
    store.load_seed()
    nodes, _ = store.get_graph()
    return {"status": "seeded", "node_count": len(nodes)}
