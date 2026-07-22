"""Run the scripted China-graphite-export scenario end-to-end (Week-2 proof).

Usage (from the backend/ directory):
    python scripts/demo_graphite.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.pipeline import run_scenario  # noqa: E402
from app.data.events import DEMO_EVENT_ID, EVENTS_BY_ID  # noqa: E402


def _fmt_lead(days):
    return f"~{days:.0f} days" if days is not None else "n/a"


def main() -> None:
    ev = EVENTS_BY_ID[DEMO_EVENT_ID]
    print(f"SIGNAL  {ev['date']}  {ev['headline']}  ({ev['source']['name']})\n")

    res = run_scenario([DEMO_EVENT_ID])
    print(
        f"pipeline: llm_enabled={res.meta.get('llm_enabled')}  "
        f"shocked_nodes={res.meta.get('shocked_nodes')}  alerts={res.meta.get('alert_count')}\n"
    )

    if not res.alerts:
        print("No products affected.")
        return

    for a in res.alerts:
        print(
            f"[{a.risk_band.upper()}] {a.product_label}: "
            f"risk {a.baseline_risk:.0f} -> {a.scenario_risk:.0f} (+{a.delta:.0f})"
        )
        print(f"   lead time: {_fmt_lead(a.lead_time_days)}  (via {a.via_label})")
        print(f"   risk path: {' -> '.join(a.path_labels)}")
        print(f"   brief: {a.brief}")
        print("   recommendations:")
        for r in a.recommendations:
            print(f"     - {r}")
        print()


if __name__ == "__main__":
    main()
