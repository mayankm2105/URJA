"""Statistical process control over incoming cell-inspection lots.

Per supplier: build a baseline from the first N lots (assumed in-control),
derive 3-sigma control limits, and flag lots that breach them or whose EWMA
trend drifts. Detector reads observed measurements only.
"""
from __future__ import annotations

BASELINE_N = 15
K_SIGMA = 3.5
EWMA_LAMBDA = 0.3
EWMA_K = 2.5


def _mean_std(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / max(n - 1, 1)
    return m, var ** 0.5


def _limits_for(group: list[dict]) -> dict:
    """3-sigma control limits derived from the supplier's in-control baseline."""
    base = group[:BASELINE_N]
    cm, cs = _mean_std([b["capacity_mah"] for b in base])
    im, isd = _mean_std([b["ir_mohm"] for b in base])
    return {
        "cap_center": cm,
        "cap_lcl": cm - K_SIGMA * cs,
        "cap_ewma_limit": cm - EWMA_K * cs,
        "ir_center": im,
        "ir_ucl": im + K_SIGMA * isd,
        "ir_ewma_limit": im + EWMA_K * isd,
        "baseline_lots": len(base),
    }


def control_limits(lots: list[dict]) -> dict[str, dict]:
    """Per-supplier control limits, so a UI can draw the actual SPC chart."""
    by_sup: dict[str, list[dict]] = {}
    for l in lots:
        by_sup.setdefault(l["supplier_id"], []).append(l)
    return {
        sid: _limits_for(sorted(g, key=lambda x: x["day"]))
        for sid, g in by_sup.items()
    }


def flag_lots(lots: list[dict]) -> list[dict]:
    by_sup: dict[str, list[dict]] = {}
    for l in lots:
        by_sup.setdefault(l["supplier_id"], []).append(l)

    out: list[dict] = []
    for group in by_sup.values():
        group = sorted(group, key=lambda x: x["day"])
        lim = _limits_for(group)
        cm, lcl_cap, ewma_cap_lim = lim["cap_center"], lim["cap_lcl"], lim["cap_ewma_limit"]
        im, ucl_ir, ewma_ir_lim = lim["ir_center"], lim["ir_ucl"], lim["ir_ewma_limit"]

        ew_cap, ew_ir = cm, im
        for l in group:
            ew_cap = EWMA_LAMBDA * l["capacity_mah"] + (1 - EWMA_LAMBDA) * ew_cap
            ew_ir = EWMA_LAMBDA * l["ir_mohm"] + (1 - EWMA_LAMBDA) * ew_ir
            reasons = []
            if l["capacity_mah"] < lcl_cap:
                reasons.append("capacity below control limit")
            if l["ir_mohm"] > ucl_ir:
                reasons.append("internal resistance above control limit")
            if ew_cap < ewma_cap_lim:
                reasons.append("EWMA capacity drift")
            if ew_ir > ewma_ir_lim:
                reasons.append("EWMA resistance drift")
            out.append({**l, "flagged": len(reasons) > 0, "reasons": reasons})
    return out


def supplier_status(flagged_lots: list[dict]) -> list[dict]:
    by: dict[str, list[dict]] = {}
    for l in flagged_lots:
        by.setdefault(l["supplier_id"], []).append(l)
    res = []
    for group in by.values():
        group = sorted(group, key=lambda x: x["day"])
        last5 = group[-5:]
        drifting = sum(1 for l in last5 if l["flagged"]) >= 3
        res.append(
            {
                "supplier_id": group[0]["supplier_id"],
                "supplier": group[0]["supplier"],
                "status": "drifting" if drifting else "stable",
                "flagged_count": sum(1 for l in group if l["flagged"]),
                "total": len(group),
            }
        )
    return res
