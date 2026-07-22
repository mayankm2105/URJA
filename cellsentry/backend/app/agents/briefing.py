"""Mitigation & briefing agent.

Deterministic alternative-supplier recommendations (graph-derived), plus an
executive brief written by Claude — with a template fallback when no API key
is set, so the pipeline always returns something demoable.
"""
from __future__ import annotations

from ..config import get_settings
from .llm import get_client


def alternative_recommendations(
    rm_node_ids: list[str], by_id: dict, lead_days: float | None
) -> list[str]:
    recs: list[str] = []
    for rm in rm_node_ids:
        n = by_id.get(rm, {})
        shares = n.get("country_shares") or {}
        ranked = [c for c in sorted(shares, key=shares.get, reverse=True) if c != "Others"]
        if ranked:
            dominant = ranked[0]
            alts = ranked[1:3]
            alt_txt = ", ".join(alts) if alts else "alternative regions / synthetic"
            recs.append(
                f"Qualify a second {n.get('label', 'material')} source outside "
                f"{dominant} (e.g. {alt_txt}) to cut single-country dependence."
            )
    if lead_days is not None:
        recs.append(
            f"Pre-buy ~{lead_days:.0f} days of affected inventory now, before the buffer depletes."
        )
    recs.append("Stand up dual-sourcing qualification for the affected anode / cell supplier.")
    return recs


def _template_brief(ctx: dict) -> str:
    lt = (
        f"~{ctx['lead_time_days']:.0f} days"
        if ctx.get("lead_time_days") is not None
        else "unknown lead time"
    )
    path = " → ".join(ctx.get("path_labels") or [])
    heads = "; ".join(ctx.get("headlines") or []) or "active supply signals"
    return (
        f"{ctx['product_label']} supply-chain risk rises to {ctx['scenario_risk']:.0f}/100 "
        f"(from a {ctx['baseline_risk']:.0f} baseline) following: {heads}. "
        f"Estimated lead time before production impact is {lt}, propagating along "
        f"{path}. Act within that window: "
        + " ".join(ctx.get("recommendations") or [])
    )


def generate_brief(ctx: dict) -> str:
    client = get_client()
    if client is None:
        return _template_brief(ctx)
    settings = get_settings()
    facts = (
        f"Product: {ctx['product_label']}\n"
        f"Scenario risk: {ctx['scenario_risk']:.0f}/100 (baseline {ctx['baseline_risk']:.0f})\n"
        f"Lead time before impact: "
        f"{('~%.0f days' % ctx['lead_time_days']) if ctx.get('lead_time_days') is not None else 'unknown'}\n"
        f"Risk path: {' -> '.join(ctx.get('path_labels') or [])}\n"
        f"Triggering events: {'; '.join(ctx.get('headlines') or [])}\n"
        f"Candidate mitigations: {' '.join(ctx.get('recommendations') or [])}"
    )
    try:
        resp = client.messages.create(
            model=settings.briefing_model,
            max_tokens=600,
            system=(
                "You are a battery supply-chain risk analyst writing for a procurement and "
                "operations leader. Write a tight 3-4 sentence executive brief. Lead with the "
                "risk level and the lead time before impact, then the single most important "
                "action. No preamble, no bullet lists, no markdown."
            ),
            messages=[{"role": "user", "content": facts}],
        )
        text = "".join(
            getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
        ).strip()
        return text or _template_brief(ctx)
    except Exception:
        return _template_brief(ctx)
