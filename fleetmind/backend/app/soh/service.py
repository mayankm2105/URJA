"""Assembly layer — turns a fleet spec into estimator + RUL views.

Keeps the API routes thin: they call into here, which wires together the data
generator, the least-squares fit, the RUL projection and the briefing agent.
"""
from __future__ import annotations

from ..agents.health_brief import generate_brief, recommendations
from ..data import fleet
from . import degradation as deg
from . import estimator, pooled, rul


def _summary_ctx(spec: dict) -> dict:
    """Fit the asset's observed series and project RUL. Returns a context dict
    shared by both the summary and the detail builders."""
    series = fleet.observed_series(spec)
    fit = estimator.fit(series)
    state = fleet.current_state(spec)
    pred = rul.predict_rul(
        fit, state["efc_total"], state["day"], state["efc_per_day"]
    )
    driver = deg.dominant_driver(spec, state["efc_total"], state["day"])
    band = rul.health_band(pred["soh_now"])
    return {
        "spec": spec,
        "series": series,
        "fit": fit,
        "state": state,
        "pred": pred,
        "driver": driver,
        "band": band,
    }


def build_summary(spec: dict) -> dict:
    c = _summary_ctx(spec)
    return _summary_from_ctx(c)


def _summary_from_ctx(c: dict) -> dict:
    spec, pred = c["spec"], c["pred"]
    return {
        "id": spec["id"],
        "name": spec["name"],
        "vehicle_type": spec["vehicle_type"],
        "region": spec["region"],
        "chemistry": spec["chemistry"],
        "soh": pred["soh_now"],
        "soh_band": c["band"],
        "rul_days": pred["rul_days"],
        "rul_efc": pred["rul_efc"],
        "efc_total": c["state"]["efc_total"],
        "age_days": spec["in_service_days"],
        "dominant_driver": c["driver"],
        "horizon_capped": pred["horizon_capped"],
    }


def build_fleet() -> dict:
    summaries = [build_summary(s) for s in fleet.ASSET_SPECS]
    # Worst (lowest SoH) first — the health board leads with what needs action.
    summaries.sort(key=lambda a: a["soh"])
    avg = sum(a["soh"] for a in summaries) / len(summaries) if summaries else 0.0
    at_risk = [a for a in summaries if a["soh_band"] in ("aging", "end_of_life")]
    return {
        "assets": summaries,
        "meta": {
            "fleet_size": len(summaries),
            "fleet_soh_avg": round(avg, 4),
            "at_risk_count": len(at_risk),
            "end_of_life_count": len([a for a in summaries if a["soh_band"] == "end_of_life"]),
        },
    }


def build_detail(asset_id: str, generate_llm_brief: bool = False) -> dict | None:
    spec = fleet.get_spec(asset_id)
    if spec is None:
        return None
    c = _summary_ctx(spec)
    summary = _summary_from_ctx(c)
    fit, state, pred = c["fit"], c["state"], c["pred"]

    # Data-derived cycle/calendar split from the fleet-pooled fit (not the
    # ground-truth physics) — what a real deployment would actually report.
    breakdown = pooled.fitted_attribution(spec, state["efc_total"], state["day"])
    history = [
        {
            "day": p["day"],
            "efc": p["efc"],
            "soh_observed": p["soh_observed"],
            "soh_true": p["soh_true"],
        }
        for p in c["series"]
    ]
    projection = rul.projection_series(
        fit, state["efc_total"], state["day"], state["efc_per_day"], pred["rul_days"]
    )

    brief_ctx = {
        **summary,
        "soh_now": pred["soh_now"],
        "rul_days": None if pred["horizon_capped"] else pred["rul_days"],
        "eol_soh": pred["eol_soh"],
        "health_band": c["band"],
    }
    recs = recommendations(brief_ctx)
    brief_ctx["recommendations"] = recs
    brief = generate_brief(brief_ctx) if generate_llm_brief else ""

    return {
        "summary": summary,
        "fit": {"a": fit.a, "c": fit.c, "n": fit.n, "rmse": round(fit.rmse, 5)},
        "fade_breakdown": {
            k: (round(v, 5) if isinstance(v, (int, float)) else v)
            for k, v in breakdown.items()
        },
        "history": history,
        "projection": projection,
        "recommendations": recs,
        "brief": brief,
    }
