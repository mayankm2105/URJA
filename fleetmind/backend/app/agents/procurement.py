"""Electrification procurement agent.

Writes a short transition recommendation over a scored candidate — Claude when a
key is configured, deterministic template otherwise. The narrative leads with the
verdict (electrify / pilot / defer), names the recommended India-market EV with
its OEM and delivery lead time, and states the economic case and the single
binding constraint.
"""
from __future__ import annotations

from ..config import get_settings
from .llm import get_client


def _inr(n: float) -> str:
    """Format rupees in Indian lakh / crore shorthand."""
    if n >= 1_00_00_000:
        return f"₹{n / 1_00_00_000:.2f} Cr"
    if n >= 1_00_000:
        return f"₹{n / 1_00_000:.1f} L"
    return f"₹{n:,.0f}"


def _template_brief(c: dict) -> str:
    ev = c["recommended_ev"]
    econ = c["economics"]
    payback = (
        f"{econ['payback_years']}-year fuel-cost payback"
        if econ["payback_years"] is not None
        else "no positive fuel-cost payback"
    )
    verdict = {
        "Electrify now": "is ready to electrify now",
        "Pilot deployment": "is a pilot-deployment candidate",
        "Defer / monitor": "should be deferred",
    }.get(c["action"], "was assessed")
    return (
        f"{c['name']} ({c['region']}, {c['powertrain'].upper()}) {verdict} with a "
        f"readiness index of {c['readiness_index']} and {c['confidence']}% confidence. "
        f"Best-fit replacement is the {ev['model']} from {ev['oem']} "
        f"(≈{ev['range_km']} km range, {ev['lead_weeks']}-week delivery lead, "
        f"{_inr(ev['price_inr'])} on-road), saving {_inr(econ['annual_saving_inr'])}/yr "
        f"in running cost for a {payback}. Binding constraint: {c['binding_constraint']}."
    )


def generate_brief(candidate: dict) -> str:
    client = get_client()
    if client is None:
        return _template_brief(candidate)
    settings = get_settings()
    ev = candidate["recommended_ev"]
    econ = candidate["economics"]
    sub = candidate["subscores"]
    facts = (
        f"Candidate: {candidate['name']} in {candidate['region']}, currently "
        f"{candidate['powertrain'].upper()}, class {candidate['vehicle_class']}.\n"
        f"Operations: {candidate['daily_km']} km/day, payload {candidate['payload_kg']} kg, "
        f"depot dwell {candidate['dwell_hours']} h, returns-to-depot "
        f"{candidate['returns_to_depot']}, fixed-route {candidate['route_fixed']}.\n"
        f"Readiness index {candidate['readiness_index']}/100, confidence "
        f"{candidate['confidence']}%, action '{candidate['action']}'.\n"
        f"Sub-scores (0-100): range {sub['range']}, charging {sub['charging']}, "
        f"payload {sub['payload']}, duty {sub['duty']}, tco {sub['tco']}.\n"
        f"Binding constraint: {candidate['binding_constraint']}.\n"
        f"Recommended EV: {ev['model']} by {ev['oem']}, {ev['range_km']} km range, "
        f"{ev['payload_kg']} kg payload, price {econ.get('price_inr', ev['price_inr'])} INR, "
        f"delivery lead {ev['lead_weeks']} weeks.\n"
        f"Economics: fuel {econ['fuel_cost_per_km']} INR/km vs EV {econ['ev_cost_per_km']} "
        f"INR/km, annual saving {econ['annual_saving_inr']} INR, payback "
        f"{econ['payback_years']} years."
    )
    try:
        resp = client.messages.create(
            model=settings.briefing_model,
            max_tokens=400,
            system=(
                "You are an EV fleet electrification advisor for an Indian "
                "logistics/transit operator. Given one vehicle's operational data "
                "and its scored best-fit EV replacement, write a tight 3-4 sentence "
                "procurement recommendation: lead with the verdict (electrify now / "
                "pilot / defer) and the readiness index, name the recommended EV with "
                "its OEM and delivery lead time, state the rupee running-cost saving "
                "and payback, and call out the single binding constraint. Use Indian "
                "rupee (lakh/crore) phrasing. No preamble, no bullet lists, no markdown."
            ),
            messages=[{"role": "user", "content": facts}],
        )
        text = "".join(
            getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
        ).strip()
        return text or _template_brief(candidate)
    except Exception:
        return _template_brief(candidate)
