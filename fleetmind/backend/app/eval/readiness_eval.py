"""Readiness scoring vs the expert baseline — PS3 evaluation metric #4.

Three complementary measures, because "agrees with the expert" means two
different things:

  * **Verdict agreement** — does the engine reach the same Electrify/Pilot/Defer
    call? Reported raw and as Cohen's kappa (chance-corrected: with only three
    classes and an unbalanced split, raw agreement flatters).
  * **Rank correlation** — does it *prioritise* the fleet in the same order?
    Spearman's rho over the full ranking.
  * **Disagreements** — listed individually with both rationales, because one
    explained disagreement is more informative than an aggregate.
"""
from __future__ import annotations

from ..electrification.expert_baseline import EXPERT_LABELS
from ..electrification.readiness import build_fleet

ACTIONS = ["Electrify now", "Pilot deployment", "Defer / monitor"]


def _cohen_kappa(a: list[str], b: list[str]) -> float:
    """Chance-corrected agreement between two labellers."""
    n = len(a)
    if n == 0:
        return 0.0
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pe = 0.0
    for cls in ACTIONS:
        pa = sum(1 for x in a if x == cls) / n
        pb = sum(1 for y in b if y == cls) / n
        pe += pa * pb
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def _spearman(rank_a: list[int], rank_b: list[int]) -> float:
    """Rho over two complete rankings (no ties by construction)."""
    n = len(rank_a)
    if n < 2:
        return 0.0
    d2 = sum((x - y) ** 2 for x, y in zip(rank_a, rank_b))
    return 1 - (6 * d2) / (n * (n * n - 1))


def evaluate() -> dict:
    fleet = build_fleet()
    rows = [c for c in fleet["candidates"] if c["id"] in EXPERT_LABELS]

    # Engine ranking: readiness index descending -> rank 1..n
    by_index = sorted(rows, key=lambda c: c["readiness_index"], reverse=True)
    engine_rank = {c["id"]: i + 1 for i, c in enumerate(by_index)}

    per_candidate = []
    engine_actions: list[str] = []
    expert_actions: list[str] = []
    er: list[int] = []
    xr: list[int] = []

    for c in sorted(rows, key=lambda c: EXPERT_LABELS[c["id"]]["rank"]):
        exp = EXPERT_LABELS[c["id"]]
        agree = c["action"] == exp["action"]
        engine_actions.append(c["action"])
        expert_actions.append(exp["action"])
        er.append(engine_rank[c["id"]])
        xr.append(exp["rank"])
        per_candidate.append(
            {
                "id": c["id"],
                "name": c["name"],
                "engine_action": c["action"],
                "expert_action": exp["action"],
                "agree": agree,
                "engine_rank": engine_rank[c["id"]],
                "expert_rank": exp["rank"],
                "readiness_index": c["readiness_index"],
                "engine_reason": c["binding_constraint"],
                "expert_reason": exp["rationale"],
            }
        )

    n = len(per_candidate)
    exact = sum(1 for r in per_candidate if r["agree"])
    disagreements = [r for r in per_candidate if not r["agree"]]

    return {
        "baseline": "Hand-labelled by India fleet-electrification domain reasoning "
        "(hard gates first, then economics) — a proxy for a consultant panel, "
        "not blind multi-expert elicitation.",
        "candidates_scored": n,
        "verdict_agreement_pct": round(exact / n * 100, 1) if n else 0.0,
        "cohen_kappa": round(_cohen_kappa(engine_actions, expert_actions), 3),
        "spearman_rho": round(_spearman(er, xr), 3),
        "rank_within_1": round(
            sum(1 for r in per_candidate if abs(r["engine_rank"] - r["expert_rank"]) <= 1)
            / n
            * 100,
            1,
        )
        if n
        else 0.0,
        "disagreement_count": len(disagreements),
        "disagreements": disagreements,
        "per_candidate": per_candidate,
    }
