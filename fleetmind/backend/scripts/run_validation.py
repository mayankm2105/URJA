"""Validate the FleetMind degradation model against real NASA battery data.

    python scripts/run_validation.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.eval.nasa_eval import evaluate  # noqa: E402


def main() -> None:
    r = evaluate()
    ma = r["model_adequacy"]
    fc = r["knee_onset_forecast"]
    print("=" * 70)
    print("FLEETMIND — Real-Data Validation (NASA Battery Aging Dataset)")
    print("=" * 70)
    print(f"\nSource: {r['source']}")
    print(f"\nModel adequacy (full-trajectory fit, sqrt+linear):")
    print(f"  in-sample RMSE: mean {ma['mean_rmse_pct']}% / max {ma['max_rmse_pct']}% SoH")
    for c in ma["per_cell"]:
        print(f"    {c['cell']}: a={c['a_sqrt']:.5f} c={c['c_linear']:.6f}  RMSE {c['in_sample_rmse_pct']}%")
    print(f"\nKnee-onset forecast ({fc['fit_window']}):")
    print(f"  SoH MAE : mean {fc['soh_mae_pct_mean']}pp / max {fc['soh_mae_pct_max']}pp")
    print(f"  RUL err : median {fc['rul_median_abs_err_cycles']} / mean {fc['rul_mean_abs_err_cycles']} cycles")
    for c in fc["per_cell"]:
        rr = c["rul"]
        line = f"    {c['cell']}: SoH MAE {c['soh_mae_pct']}pp"
        if rr:
            line += (
                f" | fit {rr['fit_window_cycles']}cyc to {rr['cutoff_soh_pct']}%"
                f" -> RUL true {rr['rul_true_cycles']} pred {rr['rul_pred_cycles']}"
                f" (err {rr['rul_abs_err_cycles']}cyc)"
            )
        print(line)
    print("\nraw:")
    print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
