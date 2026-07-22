"""Depot charging infrastructure — the other half of the Maintenance Operations
Optimiser.

PS3 build-area #6 asks for an agent that integrates "EV fleet maintenance
schedules, **charging infrastructure uptime data**, and workshop capacity ...
ensuring charging infrastructure availability aligns with operational shift
patterns".

`ops/schedule.py` already covers workshop capacity (bays) and parts lead time.
This module covers the charging side and, crucially, the interaction between
them: a depot can be perfectly healthy on paper and still strand vehicles,
because chargers go down and shifts do not wait.

The model
---------
Each depot has a bank of chargers with a rated power and an observed **uptime**
(the fraction of the window they are actually available — India depot DC chargers
realistically run 0.8-0.95 once grid trips, connector faults and queueing are
counted). Effective capacity is therefore:

    delivered_kWh = sum(chargers) power_kw * uptime * charge_window_h

The fleet's nightly demand is the energy every depot-returning asset must take
back before its next shift. If demand exceeds delivered energy, some vehicles
start the day short — and we report *which*, not just a red number.
"""
from __future__ import annotations

from ..data import fleet as fleet_data

# Depot charger banks. Uptime is observed availability, not nameplate.
DEPOTS: list[dict] = [
    {
        "id": "dep-blr",
        "name": "Bengaluru Depot",
        "chargers": 1,
        "power_kw": 60.0,
        "uptime": 0.86,   # frequent trips on this feeder
        "window_h": 8.0,  # overnight window between shifts
    },
    {
        "id": "dep-del",
        "name": "Delhi Depot",
        "chargers": 1,
        "power_kw": 60.0,
        "uptime": 0.93,
        "window_h": 8.0,
    },
    {
        "id": "dep-mum",
        "name": "Mumbai Depot",
        "chargers": 1,
        "power_kw": 30.0,
        "uptime": 0.79,   # worst bank: ageing units, one connector down
        "window_h": 7.0,
    },
    {
        "id": "dep-che",
        "name": "Chennai Depot",
        "chargers": 1,
        "power_kw": 30.0,
        "uptime": 0.91,
        "window_h": 8.0,
    },
    {
        "id": "dep-hyd",
        "name": "Hyderabad Depot",
        "chargers": 1,
        "power_kw": 60.0,
        "uptime": 0.90,
        "window_h": 7.0,
    },
]

# Every fleet region maps to the depot that actually serves it.
REGION_DEPOT = {
    "Bengaluru": "dep-blr",
    "Lucknow": "dep-del",
    "Delhi": "dep-del",
    "Jaipur": "dep-del",
    "Mumbai": "dep-mum",
    "Pune": "dep-mum",
    "Ahmedabad": "dep-mum",
    "Chennai": "dep-che",
    "Kolkata": "dep-che",
    "Hyderabad": "dep-hyd",
}
_BY_ID = {d["id"]: d for d in DEPOTS}


def _depot_for(region: str) -> dict:
    return _BY_ID[REGION_DEPOT.get(region, "dep-blr")]


def _daily_kwh(spec: dict) -> float:
    """Energy an asset must put back each night to run tomorrow's duty."""
    return spec["km_per_day"] * spec["kwh_per_km"]


def build_charging(maintenance: dict | None = None, day: int = 0) -> dict:
    """Charging headroom per depot, and where it collides with the shift pattern.

    An asset in the workshop *on the modelled day* is not drawing charge, which
    frees capacity — that coupling is why charging and maintenance belong in one
    optimiser. Note a work order is a short service window on a future day, not a
    permanent absence: only orders whose window actually covers `day` count.
    """
    in_workshop: set[str] = set()
    if maintenance:
        in_workshop = {
            w["asset_id"]
            for w in maintenance.get("work_orders", [])
            if w["recommended_start_day"] <= day < w["completion_day"]
        }

    by_depot: dict[str, dict] = {}
    for d in DEPOTS:
        by_depot[d["id"]] = {
            **{k: d[k] for k in ("id", "name", "chargers", "power_kw", "uptime", "window_h")},
            "nameplate_kwh": round(d["chargers"] * d["power_kw"] * d["window_h"], 1),
            "delivered_kwh": round(d["chargers"] * d["power_kw"] * d["uptime"] * d["window_h"], 1),
            "demand_kwh": 0.0,
            "assets": [],
            "at_risk": [],
        }

    for spec in fleet_data.ASSET_SPECS:
        dep = _depot_for(spec["region"])
        row = by_depot[dep["id"]]
        need = _daily_kwh(spec)
        row["assets"].append(
            {
                "id": spec["id"],
                "name": spec["name"],
                "region": spec["region"],
                "kwh_needed": round(need, 1),
                "in_workshop": spec["id"] in in_workshop,
            }
        )
        if spec["id"] not in in_workshop:
            row["demand_kwh"] += need

    depots = []
    total_short = 0.0
    stranded: list[dict] = []
    for row in by_depot.values():
        row["demand_kwh"] = round(row["demand_kwh"], 1)
        delivered = row["delivered_kwh"]
        headroom = round(delivered - row["demand_kwh"], 1)
        row["headroom_kwh"] = headroom
        row["utilisation_pct"] = (
            round(row["demand_kwh"] / delivered * 100, 1) if delivered > 0 else 0.0
        )
        # Energy lost purely to chargers being down, vs their nameplate.
        row["lost_to_downtime_kwh"] = round(row["nameplate_kwh"] - delivered, 1)
        row["status"] = (
            "short" if headroom < 0 else "tight" if row["utilisation_pct"] > 85 else "ok"
        )

        # N-1 contingency: standard infrastructure practice. If one charger in
        # this bank fails tonight, can the depot still put the fleet back on the
        # road tomorrow? A depot can look comfortable and still have no
        # redundancy at all.
        n1_delivered = round(
            max(row["chargers"] - 1, 0) * row["power_kw"] * row["uptime"] * row["window_h"], 1
        )
        row["n1_delivered_kwh"] = n1_delivered
        row["n1_survives"] = n1_delivered >= row["demand_kwh"]

        if headroom < 0:
            total_short += -headroom
            # Charge the shortest-duty assets first (most trips recovered per
            # kWh); whatever cannot be served is what actually strands.
            queue = sorted(
                (a for a in row["assets"] if not a["in_workshop"]),
                key=lambda a: a["kwh_needed"],
            )
            budget = delivered
            for a in queue:
                if budget >= a["kwh_needed"]:
                    budget -= a["kwh_needed"]
                else:
                    row["at_risk"].append(a["id"])
                    stranded.append(
                        {
                            "asset_id": a["id"],
                            "name": a["name"],
                            "depot": row["name"],
                            "kwh_needed": a["kwh_needed"],
                            "kwh_available": round(max(budget, 0.0), 1),
                        }
                    )
                    budget = 0.0
        depots.append(row)

    depots.sort(key=lambda r: r["headroom_kwh"])
    worst = depots[0] if depots else None

    # What restoring the weakest bank to a healthy 95% would buy back.
    uplift = None
    if worst and worst["uptime"] < 0.95:
        regained = round(
            worst["chargers"] * worst["power_kw"] * (0.95 - worst["uptime"]) * worst["window_h"],
            1,
        )
        uplift = {
            "depot": worst["name"],
            "from_uptime": worst["uptime"],
            "to_uptime": 0.95,
            "kwh_regained": regained,
            "closes_gap": regained >= -worst["headroom_kwh"] if worst["headroom_kwh"] < 0 else True,
        }

    return {
        "depots": depots,
        "stranded": stranded,
        "meta": {
            "depot_count": len(depots),
            "chargers_total": sum(d["chargers"] for d in DEPOTS),
            "fleet_demand_kwh": round(sum(d["demand_kwh"] for d in depots), 1),
            "delivered_kwh": round(sum(d["delivered_kwh"] for d in depots), 1),
            "nameplate_kwh": round(sum(d["nameplate_kwh"] for d in depots), 1),
            "lost_to_downtime_kwh": round(
                sum(d["lost_to_downtime_kwh"] for d in depots), 1
            ),
            "avg_uptime_pct": round(
                sum(d["uptime"] for d in DEPOTS) / len(DEPOTS) * 100, 1
            ),
            "depots_short": sum(1 for d in depots if d["status"] == "short"),
            "assets_at_risk": len(stranded),
            "shortfall_kwh": round(total_short, 1),
            "worst_depot": worst["name"] if worst else None,
            "no_redundancy": [d["name"] for d in depots if not d["n1_survives"]],
            "uplift": uplift,
        },
    }
