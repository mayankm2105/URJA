"""Expert baseline for fleet-electrification readiness.

PS3 evaluates "fleet electrification readiness scoring quality **versus expert
baseline**". This module is that baseline: each candidate hand-labelled the way
an India fleet-electrification consultant would call it, reasoning holistically
from first principles rather than from the engine's weighted sub-scores.

The reasoning process is deliberately *different* from the engine's:

  * the engine computes five sub-scores and takes a weighted average, so a
    strong score on one axis can compensate for a weak one;
  * the expert applies **hard gates first** (can the vehicle physically do the
    route on one charge? is there a depot to charge at?) and only then weighs
    economics and technology maturity.

That difference is the point — where the two disagree, it exposes a real
property of the engine rather than restating it.

HONEST LIMITATION: this is one practitioner's judgement encoded once, not a
panel of independent consultants scoring blind. It is a credible proxy, not a
substitute for real expert elicitation, and should be replaced by a panel
before any accuracy claim is made externally.

Verdict vocabulary matches the engine: "Electrify now" | "Pilot deployment" |
"Defer / monitor".
"""
from __future__ import annotations

# Real-world range is ~85% of the manufacturer-claimed figure (the derate the
# engine also uses); the expert applies it as a hard gate, not a score.
EXPERT_LABELS: dict[str, dict] = {
    "del-3w-ahm": {
        "rank": 1,
        "action": "Electrify now",
        "rationale": (
            "Easiest case in the fleet. 60 km/day against ~106 km real range on a "
            "Treo Zor is a 75% margin, 12 h depot dwell is far more than the ~3 h "
            "needed, and cargo 3W EVs are the most mature EV segment in India."
        ),
    },
    "del-3w-blr": {
        "rank": 2,
        "action": "Electrify now",
        "rationale": (
            "75 km/day, 11 h depot dwell, fixed route, proven 3W EV segment. "
            "Diesel at Rs 3.4/km makes the payback acceptable despite the low "
            "annual mileage."
        ),
    },
    "lcv-pun": {
        "rank": 3,
        "action": "Electrify now",
        "rationale": (
            "90 km/day against ~131 km real range on an Ace EV, 650 kg inside the "
            "1000 kg rating, 10 h depot dwell, fixed route. Diesel at Rs 7.1/km "
            "over 28k km/yr is the strongest running-cost case among the light "
            "vehicles."
        ),
    },
    "del-3w-del": {
        "rank": 4,
        "action": "Electrify now",
        "rationale": (
            "95 km/day leaves only ~11% headroom on a Treo Zor, but the route is "
            "fixed and known, so the margin is manageable. CNG at Rs 2.9/km "
            "weakens the payback — worth doing, but it is the marginal call of "
            "the four."
        ),
    },
    "bus-hyd": {
        "rank": 5,
        "action": "Pilot deployment",
        "rationale": (
            "Economically the biggest prize: diesel at Rs 24/km over 62k km/yr. "
            "190 km/day fits a Switch EiV12 (~212 km real) with ~10% margin and "
            "charging needs only ~2 h of the 7 h dwell. But Rs 1.8 cr capex and a "
            "32-week lead mean standard practice is to pilot one or two buses "
            "before committing the depot."
        ),
    },
    "lcv-mum": {
        "rank": 6,
        "action": "Pilot deployment",
        "rationale": (
            "135 km/day exceeds the Ace EV's ~131 km real range, and the route is "
            "variable so the distance is not guaranteed. Electrifiable only if the "
            "round is restructured or a mid-day top-up is added — pilot it, don't "
            "roll it out."
        ),
    },
    "auto-jai": {
        "rank": 7,
        "action": "Pilot deployment",
        "rationale": (
            "110 km/day sits exactly on the Treo's ~110 km real range with zero "
            "margin, on an on-demand route where daily distance varies. CNG at "
            "Rs 2.6/km also blunts the saving. Pilot to learn the true duty "
            "distribution first."
        ),
    },
    "taxi-kol": {
        "rank": 8,
        "action": "Pilot deployment",
        "rationale": (
            "175 km/day against ~181 km real range on an Xpres-T is a ~3% margin "
            "— unacceptable for a revenue taxi on variable routes, where a missed "
            "charge means lost shifts. Viable only with fast-charge access; pilot "
            "with a charging plan."
        ),
    },
    "bus-blr": {
        "rank": 9,
        "action": "Defer / monitor",
        "rationale": (
            "HARD GATE FAILURE: 245 km/day exceeds every available e-bus on one "
            "charge — the longest-range option (Switch EiV12) manages ~212 km "
            "real. No amount of good economics fixes a bus that cannot finish its "
            "day. Defer until opportunity charging is installed or the schedule is "
            "split; revisit as 300 km+ buses reach the India market."
        ),
    },
    "truck-che": {
        "rank": 10,
        "action": "Defer / monitor",
        "rationale": (
            "380 km/day intercity against ~170 km real range on an Eicher Pro X, "
            "and the truck never returns to a depot overnight. Two independent "
            "hard gates fail. Not electrifiable with today's products."
        ),
    },
}


def expert_action(candidate_id: str) -> str | None:
    row = EXPERT_LABELS.get(candidate_id)
    return row["action"] if row else None


def expert_rank(candidate_id: str) -> int | None:
    row = EXPERT_LABELS.get(candidate_id)
    return row["rank"] if row else None
