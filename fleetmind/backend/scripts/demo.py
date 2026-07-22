"""Demo: print the fleet health board and drill into the worst asset.

    python scripts/demo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.soh import service  # noqa: E402


def main() -> None:
    fleet = service.build_fleet()
    m = fleet["meta"]
    print("=" * 72)
    print("FLEETMIND — Battery Asset Health Board")
    print("=" * 72)
    print(
        f"Fleet size {m['fleet_size']} | avg SoH {m['fleet_soh_avg'] * 100:.1f}% | "
        f"at-risk {m['at_risk_count']} | end-of-life {m['end_of_life_count']}\n"
    )
    print(f"{'ASSET':<16}{'CHEM':<6}{'SoH':>7}{'BAND':>13}{'RUL(d)':>9}  DRIVER")
    print("-" * 72)
    for a in fleet["assets"]:
        rul = "capped" if a["horizon_capped"] else f"{a['rul_days']:.0f}"
        print(
            f"{a['id']:<16}{a['chemistry']:<6}{a['soh'] * 100:>6.1f}%"
            f"{a['soh_band']:>13}{rul:>9}  {a['dominant_driver']}"
        )

    worst = fleet["assets"][0]
    print("\n" + "=" * 72)
    print(f"WORST ASSET — {worst['name']} ({worst['id']})")
    print("=" * 72)
    detail = service.build_detail(worst["id"], generate_llm_brief=True)
    f = detail["fit"]
    print(f"Fitted curve: loss = {f['a']:.5f}*sqrt(EFC) + {f['c']:.6f}*EFC "
          f"(n={f['n']}, in-sample RMSE {f['rmse'] * 100:.2f}%)")
    fb = detail["fade_breakdown"]
    print(f"Fade split: cycle {fb['cycle_loss'] * 100:.1f}% | "
          f"calendar {fb['calendar_loss'] * 100:.1f}%")
    print("\nBrief:\n  " + detail["brief"])
    print("\nRecommendations:")
    for r in detail["recommendations"]:
        print(f"  - {r}")


if __name__ == "__main__":
    main()
