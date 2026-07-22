"""Real cycling data adapter — NASA Li-ion battery aging dataset.

Source: NASA Prognostics Center of Excellence "Battery Aging" dataset (four
2 Ah 18650 LiCoO2 cells B0005/B0006/B0007/B0018, cycled to failure at ~24 C).
We ship a compact per-cycle discharge-capacity extract (`nasa_capacity.csv`,
derived from the public dataset) so the repo is self-contained.

This adapter exposes each real cell through the SAME observation contract the
synthetic fleet uses (`observed_series`-style points), so the exact estimator
and RUL projection that run the operational fleet can be validated against real
ground-truth degradation in `eval/nasa_eval.py`.

For lab cells the natural ageing clock is the cycle count, so we map
EFC = cycle index (referenced to the first cycle) and State-of-Health =
capacity / first-cycle capacity (each cell normalised to start at 100%).
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

from ..config import get_settings

_CSV = Path(__file__).with_name("nasa_capacity.csv")

# Cell metadata for display (all four were cycled at 24 C ambient).
CELL_META = {
    "B0005": {"label": "NASA B0005", "ambient_c": 24},
    "B0006": {"label": "NASA B0006", "ambient_c": 24},
    "B0007": {"label": "NASA B0007", "ambient_c": 24},
    "B0018": {"label": "NASA B0018", "ambient_c": 24},
}


@lru_cache(maxsize=1)
def _raw() -> dict[str, list[tuple[int, float]]]:
    cells: dict[str, list[tuple[int, float]]] = {}
    with open(_CSV, newline="") as f:
        for row in csv.DictReader(f):
            cells.setdefault(row["battery"], []).append(
                (int(row["cycle"]), float(row["capacity_ah"]))
            )
    for k in cells:
        cells[k].sort()
    return cells


def cell_ids() -> list[str]:
    return sorted(_raw())


@lru_cache(maxsize=None)
def observed_series(cell_id: str) -> list[dict]:
    """Per-cycle observations for one real cell.

    EFC is referenced to the first cycle (so loss starts at 0, matching the
    model form); SoH is capacity normalised to the first-cycle capacity.
    `day` mirrors EFC so the shared estimator (which keys on EFC) is unchanged.
    """
    raw = _raw()[cell_id]
    cycle0, cap0 = raw[0]
    out: list[dict] = []
    for cycle, cap in raw:
        efc = cycle - cycle0
        soh = cap / cap0
        out.append(
            {
                "day": float(efc),
                "efc": float(efc),
                "capacity_ah": round(cap, 5),
                "soh_observed": round(min(1.0, soh), 5),
                # Real measurement IS the ground truth here.
                "soh_true": round(min(1.0, soh), 5),
            }
        )
    return out


def true_eol_cycle(cell_id: str) -> float | None:
    """First EFC at which observed SoH crosses the end-of-life knee (default 80%).
    The conventional RUL ground-truth definition."""
    eol = get_settings().eol_soh
    for p in observed_series(cell_id):
        if p["soh_observed"] <= eol:
            return p["efc"]
    return None


def summary(cell_id: str) -> dict:
    series = observed_series(cell_id)
    return {
        "id": cell_id,
        "label": CELL_META.get(cell_id, {}).get("label", cell_id),
        "ambient_c": CELL_META.get(cell_id, {}).get("ambient_c"),
        "cycles": len(series),
        "soh_start": series[0]["soh_observed"],
        "soh_end": series[-1]["soh_observed"],
        "true_eol_cycle": true_eol_cycle(cell_id),
    }
