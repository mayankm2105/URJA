"""Carbon tracking accuracy vs metered fuel — PS3 evaluation metric #5.

Compares what `carbon_engine` *estimates* a route emits against what the depot's
fuel meter says it actually burned. See `fuel_meter` for why litres — not CO2 —
are the measured quantity, and for the honest limitations of the meter feed.
"""
from __future__ import annotations

from .carbon_engine import diesel_co2_per_km
from .fuel_meter import meter_fleet


def _pct_err(est: float, act: float) -> float:
    return abs(est - act) / act * 100 if act > 0 else 0.0


def validate(routes: list[dict]) -> dict:
    meters = {m["route_id"]: m for m in meter_fleet(routes)}
    per_route = []

    for r in routes:
        m = meters.get(r["id"])
        if not m:
            continue
        payload = float(r.get("payload_tons") or 0.0)
        km = m["km_run"]
        # What the engine claims, from payload tier alone.
        est_tco2 = km * diesel_co2_per_km(payload) / 1000.0
        act_tco2 = m["measured_tco2"]
        per_route.append(
            {
                "route": m["route"],
                "km_run": km,
                "payload_tons": payload,
                "estimated_tco2": round(est_tco2, 3),
                "measured_tco2": act_tco2,
                "abs_err_tco2": round(abs(est_tco2 - act_tco2), 3),
                "pct_err": round(_pct_err(est_tco2, act_tco2), 1),
                "over": est_tco2 > act_tco2,
            }
        )

    if not per_route:
        return {"routes_validated": 0}

    errs = [p["pct_err"] for p in per_route]
    errs_sorted = sorted(errs)
    n = len(errs)
    tot_est = sum(p["estimated_tco2"] for p in per_route)
    tot_act = sum(p["measured_tco2"] for p in per_route)

    return {
        "source": "Simulated depot fuel-meter readings calibrated to published "
        "Indian fleet economy ranges — not a live telematics feed.",
        "measured_quantity": "Litres dispensed x 2.68 kg CO2e/L (published factor). "
        "What is validated is the engine's km/litre assumption, which is the only "
        "part that can actually be wrong.",
        "routes_validated": n,
        "mape_pct": round(sum(errs) / n, 1),
        "median_pct_err": round(errs_sorted[n // 2], 1),
        "worst_pct_err": round(max(errs), 1),
        "within_15_pct": round(sum(1 for e in errs if e <= 15) / n * 100, 1),
        # Fleet-level total matters more than any single route for a Net-Zero
        # report: per-route errors partially cancel.
        "fleet_total_estimated_tco2": round(tot_est, 1),
        "fleet_total_measured_tco2": round(tot_act, 1),
        "fleet_total_pct_err": round(_pct_err(tot_est, tot_act), 1),
        "per_route": sorted(per_route, key=lambda p: -p["pct_err"]),
    }
