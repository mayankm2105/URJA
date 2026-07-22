"""Print the degradation-prediction eval metrics.

    python scripts/run_eval.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.eval.harness import run_all  # noqa: E402


def main() -> None:
    results = run_all()
    soh = results["soh_prediction"]
    rul = results["rul_prediction"]
    cr = results["coefficient_recovery"]
    print("=" * 60)
    print("FLEETMIND — Degradation-Prediction Evaluation")
    print("=" * 60)
    print(f"\nSoH prediction (temporal holdout, cutoff {soh['cutoff_fraction']:.0%}):")
    print(f"  held-out points : {soh['held_out_points']} across {soh['assets']} assets")
    print(f"  SoH MAE         : {soh['soh_mae_pct']:.3f} percentage points")
    print(f"  SoH RMSE        : {soh['soh_rmse_pct']:.3f} percentage points")
    print(f"\nRUL prediction (time-to-80%-knee):")
    print(f"  assets scored   : {rul['assets_scored']}")
    print(f"  median abs error: {rul['rul_median_abs_err_days']} days")
    print(f"  mean abs error  : {rul['rul_mean_abs_err_days']} days")
    print(f"  median APE      : {rul['rul_mape_pct']}%")
    print(f"\nFleet-pooled coefficient recovery (cycle vs calendar separation):")
    print(f"  max  rel error  : {cr['max_rel_err_pct']}%")
    print(f"  mean rel error  : {cr['mean_rel_err_pct']}%")
    for chem, e in cr["per_chemistry"].items():
        print(
            f"  {chem}: b_cyc {e['b_cyc']['fitted']:.5f} vs {e['b_cyc']['truth']:.5f} "
            f"({e['b_cyc']['rel_err_pct']}%) | "
            f"b_cal {e['b_cal']['fitted']:.5f} vs {e['b_cal']['truth']:.5f} "
            f"({e['b_cal']['rel_err_pct']}%)"
        )
    print("\nraw:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
