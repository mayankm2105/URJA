"""Electrification readiness & procurement engine.

For each ICE/CNG candidate vehicle we evaluate every class-compatible EV in the
India catalog and compute a transition readiness index from five operational
sub-scores, then recommend the best-fit model with a procurement action.

Sub-scores (0-100)
-------------------
range     : does the EV's real-world range comfortably cover the daily route?
charging  : does the depot dwell window fit the daily recharge?
payload   : can the EV carry the required payload?
duty      : is the duty cycle EV-friendly (depot-returning, fixed route)?
tco       : how fast does fuel-cost saving pay back the EV price?

The readiness index is their weighted sum. A confidence score reflects how
*decisive* the sub-scores are — marginal scores near the pass/fail boundary
lower confidence in the recommendation.
"""
from __future__ import annotations

from . import catalog
from .candidates import CANDIDATES, get_candidate

ELEC_TARIFF_INR_PER_KWH = 8.0     # commercial depot charging tariff
REALWORLD_RANGE_DERATE = 0.85     # claimed -> real-world range
RANGE_TARGET_MARGIN = 0.30        # want >=30% range headroom for full score
CHARGE_TARGET_MARGIN = 0.50       # want dwell >=1.5x required charge time

# CO2 accounting (kg CO2e/km) — tailpipe factors by vehicle class for diesel;
# CNG burns ~20% cleaner per km. EVs charge from the India grid at the CEA
# average factor (~0.71 kg CO2/kWh), so EV emissions = kwh_per_km * grid EF.
DIESEL_EF_KG_PER_KM = {
    "city_bus": 1.05,
    "mcv_truck": 0.75,
    "lcv": 0.30,
    "sedan_taxi": 0.18,
    "cargo_3w": 0.10,
    "passenger_3w": 0.09,
}
CNG_MULTIPLIER = 0.80
GRID_EF_KG_PER_KWH = 0.71


def _carbon(c: dict, m: dict) -> dict:
    """Annual CO2: current ICE tailpipe vs the recommended EV on grid power."""
    base = DIESEL_EF_KG_PER_KM.get(c["vehicle_class"], 0.2)
    ice_ef = base * (CNG_MULTIPLIER if c["powertrain"] == "cng" else 1.0)
    ice_t = ice_ef * c["annual_km"] / 1000.0
    ev_t = m["kwh_per_km"] * GRID_EF_KG_PER_KWH * c["annual_km"] / 1000.0
    return {
        "ice_tco2_yr": round(ice_t, 2),
        "ev_tco2_yr": round(ev_t, 2),
        "saving_tco2_yr": round(max(ice_t - ev_t, 0.0), 2),
    }

WEIGHTS = {"range": 0.25, "charging": 0.25, "payload": 0.20, "duty": 0.15, "tco": 0.15}


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _score_pair(c: dict, m: dict) -> dict:
    usable_range = m["range_km"] * REALWORLD_RANGE_DERATE
    range_margin = usable_range / c["daily_km"] if c["daily_km"] else 99
    range_score = _clamp01((range_margin - 1.0) / RANGE_TARGET_MARGIN) * 100

    daily_energy = c["daily_km"] * m["kwh_per_km"]
    required_h = daily_energy / max(m["charge_power_kw"], 0.1)
    dwell = c["dwell_hours"]
    charge_ratio = dwell / required_h if required_h else 99
    charging_score = _clamp01((charge_ratio - 1.0) / CHARGE_TARGET_MARGIN) * 100
    if not c["returns_to_depot"]:
        charging_score *= 0.4  # no depot = no reliable overnight charging

    if c["payload_kg"] <= 0:
        payload_score = 100.0
    elif m["payload_kg"] <= 0:
        payload_score = 0.0
    else:
        payload_score = _clamp01(m["payload_kg"] / c["payload_kg"]) * 100

    duty_score = 30.0 + 40.0 * c["returns_to_depot"] + 30.0 * c["route_fixed"]

    ev_cost_per_km = m["kwh_per_km"] * ELEC_TARIFF_INR_PER_KWH
    saving_per_km = max(c["fuel_cost_per_km"] - ev_cost_per_km, 0.0)
    annual_saving = saving_per_km * c["annual_km"]
    payback_years = (m["price_inr"] / annual_saving) if annual_saving > 0 else 99.0
    # 3y or faster -> full score, 8y or slower -> zero
    tco_score = _clamp01((8.0 - payback_years) / (8.0 - 3.0)) * 100

    subscores = {
        "range": round(range_score, 1),
        "charging": round(charging_score, 1),
        "payload": round(payload_score, 1),
        "duty": round(duty_score, 1),
        "tco": round(tco_score, 1),
    }
    index = sum(subscores[k] * WEIGHTS[k] for k in WEIGHTS)
    return {
        "subscores": subscores,
        "index": round(index, 1),
        "ev_cost_per_km": round(ev_cost_per_km, 2),
        "saving_per_km": round(saving_per_km, 2),
        "annual_saving_inr": round(annual_saving),
        "payback_years": round(payback_years, 1) if payback_years < 99 else None,
    }


def _confidence(subscores: dict) -> int:
    """Decisive sub-scores (clearly high or low) -> high confidence; sub-scores
    sitting near the 50 boundary -> lower confidence in the recommendation."""
    marginal = sum(1 for v in subscores.values() if 38 <= v <= 62)
    return int(max(40, 100 - marginal * 14))


def _action(index: float, confidence: int) -> str:
    if index >= 72:
        return "Electrify now"
    if index >= 52:
        return "Pilot deployment"
    return "Defer / monitor"


def _binding_constraint(subscores: dict) -> str:
    worst = min(subscores, key=subscores.get)
    labels = {
        "range": "daily range exceeds EV real-world range",
        "charging": "depot dwell window too short to recharge",
        "payload": "payload exceeds available EV capacity",
        "duty": "irregular / non-depot duty cycle",
        "tco": "weak fuel-cost payback",
    }
    return labels[worst] if subscores[worst] < 60 else "no binding constraint — strong fit"


def evaluate_candidate(candidate_id: str) -> dict | None:
    c = get_candidate(candidate_id)
    if c is None:
        return None
    options = catalog.models_for_class(c["vehicle_class"])
    scored = []
    for m in options:
        s = _score_pair(c, m)
        scored.append({"model": m, "eval": s})
    scored.sort(key=lambda x: x["eval"]["index"], reverse=True)

    best = scored[0] if scored else None
    if best is None:
        return None
    ev, ev_eval = best["model"], best["eval"]

    # Feasibility is a HARD gate, separate from the (compensatory) index: if no
    # class-compatible EV can physically finish the daily route on one charge,
    # say so. Without this the weighted average can still surface a "best" model
    # that is range-infeasible, because good TCO offsets a zero range score.
    feasible = [
        o
        for o in scored
        if o["model"]["range_km"] * REALWORLD_RANGE_DERATE >= c["daily_km"]
    ]
    range_feasible = len(feasible) > 0
    best_range_km = max(
        (o["model"]["range_km"] * REALWORLD_RANGE_DERATE for o in scored), default=0.0
    )
    confidence = _confidence(ev_eval["subscores"])
    index = ev_eval["index"]
    return {
        "id": c["id"],
        "name": c["name"],
        "region": c["region"],
        "vehicle_class": c["vehicle_class"],
        "powertrain": c["powertrain"],
        "daily_km": c["daily_km"],
        "payload_kg": c["payload_kg"],
        "dwell_hours": c["dwell_hours"],
        "returns_to_depot": c["returns_to_depot"],
        "route_fixed": c["route_fixed"],
        "readiness_index": index,
        "confidence": confidence,
        "action": _action(index, confidence),
        "binding_constraint": _binding_constraint(ev_eval["subscores"]),
        "range_feasible": range_feasible,
        "feasibility_note": (
            None
            if range_feasible
            else (
                f"No available EV in this class can cover {c['daily_km']} km on one "
                f"charge — the longest-range option manages about {best_range_km:.0f} km "
                f"real-world. Needs opportunity charging or a route split before any "
                f"model below is viable."
            )
        ),
        "subscores": ev_eval["subscores"],
        "recommended_ev": {
            "id": ev["id"],
            "model": ev["model"],
            "oem": ev["oem"],
            "chemistry": ev.get("chemistry", "LFP"),
            "range_km": ev["range_km"],
            "payload_kg": ev["payload_kg"],
            "price_inr": ev["price_inr"],
            "lead_weeks": ev["lead_weeks"],
            "fast_charge": ev["fast_charge"],
        },
        "economics": {
            "ev_cost_per_km": ev_eval["ev_cost_per_km"],
            "fuel_cost_per_km": c["fuel_cost_per_km"],
            "saving_per_km": ev_eval["saving_per_km"],
            "annual_saving_inr": ev_eval["annual_saving_inr"],
            "payback_years": ev_eval["payback_years"],
        },
        "carbon": _carbon(c, ev),
        "alternatives": [
            {
                "id": o["model"]["id"],
                "model": o["model"]["model"],
                "oem": o["model"]["oem"],
                "chemistry": o["model"].get("chemistry", "LFP"),
                "index": o["eval"]["index"],
                "price_inr": o["model"]["price_inr"],
                "lead_weeks": o["model"]["lead_weeks"],
            }
            for o in scored[1:]
        ],
    }


def build_fleet() -> dict:
    rows = [evaluate_candidate(c["id"]) for c in CANDIDATES]
    rows = [r for r in rows if r]
    rows.sort(key=lambda r: r["readiness_index"], reverse=True)

    now = [r for r in rows if r["action"] == "Electrify now"]
    pilot = [r for r in rows if r["action"] == "Pilot deployment"]
    defer = [r for r in rows if r["action"] == "Defer / monitor"]

    capex_now = sum(r["recommended_ev"]["price_inr"] for r in now)
    annual_saving_total = sum(r["economics"]["annual_saving_inr"] for r in rows)
    max_lead_now = max((r["recommended_ev"]["lead_weeks"] for r in now), default=0)
    co2_now = sum(r["carbon"]["saving_tco2_yr"] for r in now)
    co2_all = sum(r["carbon"]["saving_tco2_yr"] for r in rows)

    return {
        "candidates": rows,
        "meta": {
            "fleet_size": len(rows),
            "electrify_now": len(now),
            "pilot": len(pilot),
            "defer": len(defer),
            "avg_readiness": round(sum(r["readiness_index"] for r in rows) / len(rows), 1) if rows else 0,
            "phase1_capex_inr": capex_now,
            "phase1_max_lead_weeks": max_lead_now,
            "fleet_annual_saving_inr": annual_saving_total,
            "phase1_co2_saving_tons": round(co2_now, 1),
            "fleet_co2_saving_tons": round(co2_all, 1),
        },
    }
