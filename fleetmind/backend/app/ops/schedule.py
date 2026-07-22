"""Predictive-maintenance scheduler.

Turns the fleet's RUL projections into a concrete, downtime-aware service queue.
The depot is modelled as a small number of parallel service bays
(`max_concurrent`); replacement packs carry a procurement lead time
(`parts_lead_days`); each swap takes `service_days`.

Assets are scheduled worst-first (lowest RUL). Each is placed in the earliest
free bay no sooner than the parts lead. If an asset cannot be serviced before it
crosses the 80% end-of-life knee, it is flagged `overdue` — the cost of having
detected it too late, which is exactly what earlier prediction buys down.

The headline business metric is the contrast between this predictive plan and a
reactive run-to-failure baseline, surfaced in `meta`.
"""
from __future__ import annotations

from ..soh import service

PARTS_LEAD_DAYS = 30        # procurement lead time for a replacement pack
SERVICE_DAYS = 3            # asset out-of-service during a pack swap
MAX_CONCURRENT = 1          # parallel depot service bays
PLAN_HORIZON_DAYS = 540     # only plan for assets reaching EoL within ~18 months


def build_schedule(
    max_concurrent: int = MAX_CONCURRENT,
    parts_lead_days: int = PARTS_LEAD_DAYS,
    service_days: int = SERVICE_DAYS,
    horizon_days: int = PLAN_HORIZON_DAYS,
) -> dict:
    fleet_data = service.build_fleet()
    assets = fleet_data["assets"]

    # Candidates: already end-of-life, or projected to hit the knee within horizon.
    candidates = [
        a
        for a in assets
        if a["soh_band"] == "end_of_life"
        or (not a["horizon_capped"] and a["rul_days"] <= horizon_days)
    ]
    candidates.sort(key=lambda a: a["rul_days"])  # most urgent first

    # Greedy assignment across equal-duration bays; each bay tracks its next
    # free day (cannot start before parts arrive).
    bays = [float(parts_lead_days)] * max(1, max_concurrent)
    work_orders: list[dict] = []
    for a in candidates:
        bay = min(range(len(bays)), key=lambda i: bays[i])
        start = bays[bay]
        completion = start + service_days
        bays[bay] = completion
        # Overdue if the pack swap cannot complete before the asset crosses the
        # 80% knee — including assets already past it (rul_days == 0).
        overdue = completion > a["rul_days"] + 1e-6

        immediate = a["soh_band"] == "end_of_life" or a["rul_days"] <= parts_lead_days
        work_orders.append(
            {
                "asset_id": a["id"],
                "name": a["name"],
                "region": a["region"],
                "chemistry": a["chemistry"],
                "soh": a["soh"],
                "rul_days": a["rul_days"],
                "eol_day": round(a["rul_days"]),
                "action": "Replace pack" if immediate else "Schedule pack replacement",
                "recommended_start_day": round(start),
                "service_days": service_days,
                "completion_day": round(completion),
                "overdue": overdue,
                "priority": len(work_orders) + 1,
                "driver": a["dominant_driver"],
            }
        )

    work_orders.sort(key=lambda w: (w["recommended_start_day"], w["rul_days"]))
    last_completion = max((w["completion_day"] for w in work_orders), default=0)
    overdue_n = sum(1 for w in work_orders if w["overdue"])

    return {
        "work_orders": work_orders,
        "meta": {
            "fleet_size": fleet_data["meta"]["fleet_size"],
            "scheduled": len(work_orders),
            "overdue": overdue_n,
            "service_bays": max_concurrent,
            "parts_lead_days": parts_lead_days,
            "service_days": service_days,
            "queue_clears_day": last_completion,
            # A run-to-failure baseline only acts at EoL (day = rul), then still
            # waits the parts lead before service can even begin.
            "reactive_first_action_day": parts_lead_days,
            "predictive_first_warning_day": 0,
        },
    }
