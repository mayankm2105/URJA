"""Print the CellSentry evaluation report (Week-4 proof numbers).

Usage (from the backend/ directory):
    python scripts/run_eval.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.eval.harness import run_all  # noqa: E402


def main() -> None:
    r = run_all()
    lt, at, q = r["lead_time"], r["attribution"], r["quality"]

    print("=== CellSentry Evaluation ===\n")

    print("LEAD TIME  (signal detection -> production impact)")
    print(f"  risk events evaluated : {lt['risk_events']}")
    print(f"  events raising alerts : {lt['events_with_alerts']}  ({lt['total_alerts']} product alerts)")
    print(f"  lead time (days)      : median={lt['median_lead_days']}  mean={lt['mean_lead_days']}  range={lt['min_lead_days']}-{lt['max_lead_days']}")
    print(f"  reactive baseline     : {lt['reactive_baseline_days']} days of warning\n")

    print("PRODUCT ATTRIBUTION  (alerted products vs expected)")
    print(f"  precision={at['precision']}  recall={at['recall']}  (tp={at['tp']} fp={at['fp']} fn={at['fn']})\n")

    print("QUALITY DEFECT DETECTION  (SPC vs ground truth)")
    print(f"  lots={q['lots']}  truly defective={q['defective']}  flagged={q['flagged']}")
    print(f"  precision={q['precision']}  recall={q['recall']}  f1={q['f1']}")
    print(f"  (tp={q['tp']} fp={q['fp']} fn={q['fn']} tn={q['tn']})")


if __name__ == "__main__":
    main()
