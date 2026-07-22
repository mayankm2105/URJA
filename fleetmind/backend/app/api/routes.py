"""API routes."""
from fastapi import APIRouter, HTTPException

from ..agents.maintenance import generate_plan
from ..agents.procurement import generate_brief
from ..config import get_settings
from ..data import nasa
from ..electrification import readiness
from ..eval.harness import run_all
from ..eval.nasa_eval import evaluate as nasa_evaluate
from ..eval.readiness_eval import evaluate as readiness_evaluate
from ..models.schema import AssetDetail, AssetSummary, FleetResponse
from ..ops.charging import build_charging
from ..ops.schedule import build_schedule
from ..soh import pooled, service

router = APIRouter()


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "llm_enabled": bool(settings.anthropic_api_key),
        "eol_soh": settings.eol_soh,
    }


@router.get("/fleet", response_model=FleetResponse)
def get_fleet() -> FleetResponse:
    """Fleet health board: every asset's current SoH, RUL and dominant driver,
    worst-first."""
    data = service.build_fleet()
    return FleetResponse(
        assets=[AssetSummary(**a) for a in data["assets"]],
        meta=data["meta"],
    )


@router.get("/asset/{asset_id}", response_model=AssetDetail)
def get_asset(asset_id: str, brief: bool = False) -> AssetDetail:
    """Full per-asset detail: observed history, fitted curve, RUL projection,
    recommendations and (optionally) an LLM-written health brief."""
    detail = service.build_detail(asset_id, generate_llm_brief=brief)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"unknown asset '{asset_id}'")
    return AssetDetail(**detail)


@router.get("/maintenance")
def maintenance(
    bays: int = 1, parts_lead_days: int = 30, plan: bool = False
) -> dict:
    """Predictive-maintenance service queue: RUL-driven, downtime-aware work
    orders worst-first. Pass plan=true for an LLM-written ops narrative."""
    schedule = build_schedule(max_concurrent=bays, parts_lead_days=parts_lead_days)
    schedule["plan"] = generate_plan(schedule) if plan else ""
    return schedule


@router.get("/electrification/eval")
def electrification_eval() -> dict:
    """Readiness scoring vs the expert baseline (PS3 evaluation metric #4)."""
    return readiness_evaluate()


@router.get("/charging")
def charging(bays: int = 1, parts_lead_days: int = 30) -> dict:
    """Depot charging-infrastructure headroom, coupled to the maintenance plan
    (assets in the workshop aren't charging). PS3 build-area #6."""
    sched = build_schedule(max_concurrent=bays, parts_lead_days=parts_lead_days)
    return build_charging(sched)


@router.get("/model")
def model() -> dict:
    """Fleet-pooled degradation coefficients (data-derived cycle vs calendar
    fade rates per chemistry)."""
    return {"pooled": pooled.get_pooled_model()}


@router.get("/electrification")
def electrification() -> dict:
    """Fleet electrification readiness & procurement plan: every ICE/CNG candidate
    mapped to its optimal India-market EV replacement, with a confidence-scored
    transition readiness index, OEM/lead-time procurement recommendation, and a
    phased rollout rolled up to fleet CapEx and annual fuel-cost saving."""
    return readiness.build_fleet()


@router.get("/electrification/{candidate_id}")
def electrification_candidate(candidate_id: str, brief: bool = False) -> dict:
    """Single candidate's full electrification assessment. Pass brief=true for an
    LLM-written procurement recommendation."""
    c = readiness.evaluate_candidate(candidate_id)
    if c is None:
        raise HTTPException(status_code=404, detail=f"unknown candidate '{candidate_id}'")
    c["brief"] = generate_brief(c) if brief else ""
    return c


@router.get("/eval")
def evaluation() -> dict:
    """Degradation-prediction accuracy: SoH MAE/RMSE, RUL error, and pooled
    coefficient recovery vs the ground-truth trajectories."""
    return run_all()


@router.get("/validation")
def validation() -> dict:
    """Real-data validation of the model against the NASA battery aging dataset:
    model adequacy (in-sample fit) + knee-onset SoH/RUL forecast accuracy."""
    return nasa_evaluate()


@router.get("/validation/cells")
def validation_cells() -> dict:
    """Per-cell real NASA capacity-fade series (for charting the validation)."""
    return {
        "cells": [
            {**nasa.summary(cid), "series": nasa.observed_series(cid)}
            for cid in nasa.cell_ids()
        ]
    }
