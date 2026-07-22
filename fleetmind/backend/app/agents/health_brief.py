"""Asset-health briefing agent.

Deterministic, physics-derived maintenance recommendations (so the API is
always useful with zero dependencies), plus an executive health brief written
by Claude — with a template fallback when no API key is set.
"""
from __future__ import annotations

from ..config import get_settings
from .llm import get_client


def recommendations(ctx: dict) -> list[str]:
    """Maintenance / ops actions ranked by the asset's dominant fade driver."""
    recs: list[str] = []
    driver = ctx.get("dominant_driver", "")
    rul = ctx.get("rul_days")
    band = ctx.get("health_band")

    if band == "end_of_life":
        recs.append(
            "Battery is at/below the 80% end-of-life knee — schedule pack "
            "replacement or second-life redeployment now and pull the asset "
            "from high-availability routes."
        )
    elif rul is not None and rul <= 180:
        recs.append(
            f"Pre-order a replacement pack and book a service slot — projected "
            f"~{rul:.0f} days of usable life before the 80% knee."
        )

    if driver == "high cell temperature":
        recs.append(
            "Thermal load is the dominant fade driver: inspect pack cooling, "
            "shift charging to cooler hours, and shade/ventilate depot parking."
        )
    elif driver == "high-rate (fast) charging":
        recs.append(
            "Fast-charging is accelerating fade: cap routine charging at a lower "
            "C-rate and reserve DC fast-charge for genuine turnaround pressure."
        )
    elif driver == "deep discharge cycling":
        recs.append(
            "Deep discharge is widening per-cycle loss: raise the lower SoC limit "
            "and rebalance to shorter routes so the pack swings less."
        )
    elif driver == "high cycle throughput":
        recs.append(
            "Throughput is the main driver: rotate this asset onto lighter-duty "
            "routes to flatten its cycle accrual."
        )

    recs.append(
        "Keep logging weekly capacity checks — the RUL projection tightens as "
        "the fitted curve sees more of the fade trajectory."
    )
    return recs


def _template_brief(ctx: dict) -> str:
    rul = (
        f"~{ctx['rul_days']:.0f} days"
        if ctx.get("rul_days") is not None
        else "an indeterminate horizon"
    )
    band = {
        "healthy": "healthy",
        "aging": "ageing but serviceable",
        "end_of_life": "at end-of-life",
    }.get(ctx.get("health_band", ""), "of uncertain health")
    return (
        f"{ctx['name']} ({ctx['chemistry']}, {ctx['region']}) is {band} at "
        f"{ctx['soh_now'] * 100:.1f}% State-of-Health after {ctx['efc_total']:.0f} "
        f"equivalent full cycles. The dominant fade driver is "
        f"{ctx['dominant_driver']}, and the battery is projected to reach the 80% "
        f"end-of-life knee in {rul}. "
        + (ctx.get("recommendations") or [""])[0]
    )


def generate_brief(ctx: dict) -> str:
    client = get_client()
    if client is None:
        return _template_brief(ctx)
    settings = get_settings()
    facts = (
        f"Asset: {ctx['name']} ({ctx['vehicle_type']}, {ctx['region']})\n"
        f"Chemistry: {ctx['chemistry']}\n"
        f"State-of-Health: {ctx['soh_now'] * 100:.1f}% (end-of-life at "
        f"{ctx['eol_soh'] * 100:.0f}%)\n"
        f"Equivalent full cycles: {ctx['efc_total']:.0f}\n"
        f"Projected remaining useful life: "
        f"{('~%.0f days' % ctx['rul_days']) if ctx.get('rul_days') is not None else 'indeterminate'}\n"
        f"Dominant fade driver: {ctx['dominant_driver']}\n"
        f"Candidate actions: {' '.join(ctx.get('recommendations') or [])}"
    )
    try:
        resp = client.messages.create(
            model=settings.briefing_model,
            max_tokens=600,
            system=(
                "You are a battery asset-performance analyst writing for an EV "
                "fleet operations manager. Write a tight 3-4 sentence executive "
                "brief. Lead with the State-of-Health and the remaining useful "
                "life, then the single most important maintenance action. No "
                "preamble, no bullet lists, no markdown."
            ),
            messages=[{"role": "user", "content": facts}],
        )
        text = "".join(
            getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
        ).strip()
        return text or _template_brief(ctx)
    except Exception:
        return _template_brief(ctx)
