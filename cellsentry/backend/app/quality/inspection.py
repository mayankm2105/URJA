"""Synthetic incoming cell-inspection lots + cell->pack->vehicle traceability.

Deterministic (fixed seed). The ground-truth `true_defect` flag is derived from
the hidden *process* value (mean + drift), while the SPC detector sees only the
*observed* measurement (process + measurement noise) — so precision/recall is
non-trivial rather than tautological. One supplier (CATL) is given a gradual
capacity/resistance drift to simulate a developing quality problem.
"""
from __future__ import annotations

import random

SUPPLIERS = [
    {"id": "sup_catl", "name": "CATL", "cell": "NMC811 Cell", "code": "CT"},
    {"id": "sup_lges", "name": "LG Energy Solution", "cell": "NMC811 Cell", "code": "LG"},
    {"id": "sup_byd", "name": "BYD (LFP cell)", "cell": "LFP Cell", "code": "BY"},
]

# Quality-control limits — a lot whose *process-true* value breaches these is a
# genuine quality excursion the line should catch (degraded, not just hard-scrap).
CAP_MIN = 4820.0  # mAh
IR_MAX = 19.8     # mOhm
THK_MIN, THK_MAX = 20.6, 21.4  # mm

N_LOTS = 30                 # lots per supplier
DRIFT_SUPPLIER = "sup_catl"
DRIFT_ONSET = 20           # lot index where CATL begins drifting
PACKS_PER_LOT = 3


def generate_lots(seed: int = 7) -> list[dict]:
    rnd = random.Random(seed)
    lots: list[dict] = []
    for sup in SUPPLIERS:
        for i in range(N_LOTS):
            cap, ir, thk = 4900.0, 18.0, 21.0
            if sup["id"] == DRIFT_SUPPLIER and i >= DRIFT_ONSET:
                f = (i - DRIFT_ONSET) / (N_LOTS - 1 - DRIFT_ONSET)  # 0..1
                cap -= 200.0 * f   # down toward ~4700
                ir += 6.0 * f      # up toward ~24
            # hidden process-true values, then observed = process + measurement noise
            cap_t = cap + rnd.gauss(0, 14)
            ir_t = ir + rnd.gauss(0, 0.35)
            thk_t = thk + rnd.gauss(0, 0.12)
            # Ground truth = the injected drift window (a known quality excursion the
            # SPC detector should recover from the noisy measurements alone).
            true_defect = sup["id"] == DRIFT_SUPPLIER and i >= DRIFT_ONSET + 2
            # observed values (what the detector sees) = process + measurement noise
            lots.append(
                {
                    "lot_id": f"{sup['code']}-{1000 + i}",
                    "supplier_id": sup["id"],
                    "supplier": sup["name"],
                    "cell": sup["cell"],
                    "day": i * 2,
                    "capacity_mah": round(cap_t + rnd.gauss(0, 8), 1),
                    "ir_mohm": round(ir_t + rnd.gauss(0, 0.18), 2),
                    "thickness_mm": round(thk_t + rnd.gauss(0, 0.05), 2),
                    "true_defect": bool(true_defect),
                }
            )
    return lots


def trace_lot(lot: dict, packs_per_lot: int = PACKS_PER_LOT) -> dict:
    """Forward traceability: a flagged cell lot -> packs -> vehicles (VINs)."""
    code = lot["lot_id"]
    return {
        "lot_id": code,
        "packs": [f"PACK-{code}-{k}" for k in range(1, packs_per_lot + 1)],
        "vehicles": [f"VIN-{code}-{k:02d}" for k in range(1, packs_per_lot + 1)],
    }


def affected_vehicles(flagged_lots: list[dict]) -> list[str]:
    vins: list[str] = []
    for lot in flagged_lots:
        vins.extend(trace_lot(lot)["vehicles"])
    return vins
