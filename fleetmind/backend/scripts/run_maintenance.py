"""Print the predictive-maintenance service queue.

    python scripts/run_maintenance.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.maintenance import generate_plan  # noqa: E402
from app.ops.schedule import build_schedule  # noqa: E402


def main() -> None:
    sched = build_schedule()
    m = sched["meta"]
    print("=" * 78)
    print("FLEETMIND — Predictive-Maintenance Service Queue")
    print("=" * 78)
    print(
        f"{m['scheduled']}/{m['fleet_size']} assets scheduled | {m['overdue']} overdue | "
        f"{m['service_bays']} bay(s) | {m['parts_lead_days']}d parts lead | "
        f"queue clears day {m['queue_clears_day']}\n"
    )
    print(f"{'#':>2}  {'ASSET':<14}{'SoH':>6}{'RUL(d)':>8}{'START':>7}{'DONE':>6}  {'STATUS':<9}ACTION")
    print("-" * 78)
    for w in sched["work_orders"]:
        status = "OVERDUE" if w["overdue"] else "on-time"
        print(
            f"{w['priority']:>2}  {w['asset_id']:<14}{w['soh'] * 100:>5.0f}%"
            f"{w['rul_days']:>8.0f}{w['recommended_start_day']:>7.0f}"
            f"{w['completion_day']:>6.0f}  {status:<9}{w['action']}"
        )
    print("\nPlan:\n  " + generate_plan(sched))


if __name__ == "__main__":
    main()
