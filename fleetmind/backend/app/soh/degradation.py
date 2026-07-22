"""Semi-empirical battery degradation model.

State-of-Health (SoH) is the usable capacity as a fraction of nameplate
capacity. Capacity fades through two coupled mechanisms, both well documented
in the Li-ion aging literature:

  * Cycle (throughput) ageing — SEI growth / lithium-plating driven loss that
    scales with the *square root* of charge throughput (equivalent full
    cycles, EFC). The sqrt law is the standard SEI-limited result
    (e.g. Severson et al. 2019; Schmalstieg et al. 2014).

  * Calendar ageing — time-driven loss that scales with the square root of
    days in service and accelerates with temperature.

Both are accelerated by stress factors:

  * Temperature — Arrhenius-like. Reaction rate roughly doubles every ~10-15 C,
    captured here as exp(k * (T - T_ref)).
  * Depth of discharge (DoD) — deeper swings widen the fade per cycle.
  * C-rate — faster charge/discharge plates lithium and heats the cell.

Chemistry sets the baseline durability: LFP cells are markedly more
cycle-stable than NMC (thousands vs ~1-2k EFC to the 80% end-of-life knee),
which the per-chemistry coefficients below reproduce.

Everything here is a pure function of an asset's static spec plus its
cumulative (EFC, days) — so the same model generates ground-truth trajectories
for the synthetic fleet *and* serves as the physical prior the estimator fits.
"""
from __future__ import annotations

import math

# Reference operating point the coefficients are calibrated at.
T_REF_C = 25.0          # cell temperature reference
DOD_REF = 0.80          # reference depth of discharge
C_RATE_REF = 0.50       # reference average C-rate

# Per-chemistry baseline fade coefficients, calibrated so an asset run at the
# reference operating point reaches the 80% SoH knee at a realistic EFC count:
#   NMC ~1,500 EFC,  LFP ~3,500 EFC.
CHEMISTRY = {
    "NMC": {"b_cyc": 0.00517, "b_cal": 0.00120},
    "LFP": {"b_cyc": 0.00338, "b_cal": 0.00090},
}

# Arrhenius temperature sensitivity (per degree C). k=0.04 => rate roughly
# doubles every ~17 C, in line with reported Li-ion acceleration factors.
TEMP_K = 0.04


def temp_factor(temp_c: float) -> float:
    """Arrhenius-like acceleration relative to the 25 C reference."""
    return math.exp(TEMP_K * (temp_c - T_REF_C))


def dod_factor(dod: float) -> float:
    """Deeper discharge => more fade per cycle. Normalised to 1.0 at DoD 0.80."""
    return (max(dod, 0.05) / DOD_REF) ** 0.5


def crate_factor(c_rate: float) -> float:
    """Higher C-rate => more fade. Normalised to 1.0 at 0.5C."""
    return (max(c_rate, 0.05) / C_RATE_REF) ** 0.5


def cycle_stress(temp_c: float, dod: float, c_rate: float) -> float:
    """Combined multiplier on the cycle-fade term for an asset's duty."""
    return temp_factor(temp_c) * dod_factor(dod) * crate_factor(c_rate)


def calendar_stress(temp_c: float) -> float:
    """Combined multiplier on the calendar-fade term (temperature only)."""
    return temp_factor(temp_c)


def soh(spec: dict, efc: float, days: float) -> float:
    """Ground-truth State-of-Health in [0, 1] for cumulative (EFC, days)."""
    coeffs = CHEMISTRY[spec["chemistry"]]
    cyc_loss = (
        coeffs["b_cyc"]
        * cycle_stress(spec["cell_temp_c"], spec["avg_dod"], spec["avg_c_rate"])
        * math.sqrt(max(efc, 0.0))
    )
    cal_loss = (
        coeffs["b_cal"]
        * calendar_stress(spec["cell_temp_c"])
        * math.sqrt(max(days, 0.0))
    )
    return max(0.0, 1.0 - cyc_loss - cal_loss)


def fade_breakdown(spec: dict, efc: float, days: float) -> dict[str, float]:
    """Split total capacity loss into its cycle vs calendar contributions."""
    coeffs = CHEMISTRY[spec["chemistry"]]
    cyc_loss = (
        coeffs["b_cyc"]
        * cycle_stress(spec["cell_temp_c"], spec["avg_dod"], spec["avg_c_rate"])
        * math.sqrt(max(efc, 0.0))
    )
    cal_loss = (
        coeffs["b_cal"]
        * calendar_stress(spec["cell_temp_c"])
        * math.sqrt(max(days, 0.0))
    )
    return {"cycle_loss": cyc_loss, "calendar_loss": cal_loss}


def dominant_driver(spec: dict, efc: float, days: float) -> str:
    """Human-readable label for the largest single fade driver right now."""
    b = fade_breakdown(spec, efc, days)
    temp = spec["cell_temp_c"]
    # Surface the strongest physical lever the operator can actually pull.
    if temp >= 38 and temp_factor(temp) > 1.5:
        return "high cell temperature"
    if b["cycle_loss"] >= b["calendar_loss"]:
        if spec["avg_c_rate"] >= 0.9:
            return "high-rate (fast) charging"
        if spec["avg_dod"] >= 0.85:
            return "deep discharge cycling"
        return "high cycle throughput"
    return "calendar ageing"
