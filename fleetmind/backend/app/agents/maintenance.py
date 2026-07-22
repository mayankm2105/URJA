"""Predictive-maintenance briefing agent.

Writes a short operations narrative over the computed service queue — Claude when
a key is configured, deterministic template otherwise.
"""
from __future__ import annotations

from ..config import get_settings
from .llm import get_client


def _template_plan(schedule: dict) -> str:
    m = schedule["meta"]
    orders = schedule["work_orders"]
    if not orders:
        return "No assets are within the maintenance planning horizon — the fleet is healthy."
    top = orders[0]
    overdue = m["overdue"]
    overdue_txt = (
        f" {overdue} asset(s) are already past the 80% end-of-life knee and "
        f"cannot be serviced before failure given the {m['parts_lead_days']}-day "
        f"parts lead — prioritise these and expedite procurement."
        if overdue
        else ""
    )
    return (
        f"{m['scheduled']} of {m['fleet_size']} assets need pack service within the "
        f"planning horizon, sequenced worst-first across {m['service_bays']} "
        f"service bay(s); the queue clears by day {m['queue_clears_day']}. Start with "
        f"{top['name']} ({top['asset_id']}, {top['soh'] * 100:.0f}% SoH, driver: "
        f"{top['driver']}).{overdue_txt} Pre-ordering packs on the RUL projection "
        f"instead of waiting for failure removes the {m['parts_lead_days']}-day "
        f"lead time from the critical path."
    )


def generate_plan(schedule: dict) -> str:
    client = get_client()
    if client is None:
        return _template_plan(schedule)
    settings = get_settings()
    m = schedule["meta"]
    lines = [
        f"- {w['name']} ({w['asset_id']}): {w['soh'] * 100:.0f}% SoH, RUL "
        f"{w['rul_days']:.0f}d, action '{w['action']}' on day "
        f"{w['recommended_start_day']}{' [OVERDUE]' if w['overdue'] else ''}, "
        f"driver {w['driver']}"
        for w in schedule["work_orders"][:8]
    ]
    facts = (
        f"Fleet size {m['fleet_size']}, {m['scheduled']} scheduled, {m['overdue']} overdue. "
        f"{m['service_bays']} service bay(s), {m['parts_lead_days']}-day parts lead, "
        f"queue clears day {m['queue_clears_day']}.\nWork orders (worst-first):\n"
        + "\n".join(lines)
    )
    try:
        resp = client.messages.create(
            model=settings.briefing_model,
            max_tokens=500,
            system=(
                "You are a fleet maintenance planner for an EV operator. Given a "
                "predictive-maintenance work-order queue, write a tight 3-4 "
                "sentence ops brief: lead with how many assets need service and "
                "the most urgent one, name any overdue/at-risk assets, and state "
                "the single highest-leverage action. No preamble, no bullet "
                "lists, no markdown."
            ),
            messages=[{"role": "user", "content": facts}],
        )
        text = "".join(
            getattr(b, "text", "") for b in resp.content if getattr(b, "type", None) == "text"
        ).strip()
        return text or _template_plan(schedule)
    except Exception:
        return _template_plan(schedule)
