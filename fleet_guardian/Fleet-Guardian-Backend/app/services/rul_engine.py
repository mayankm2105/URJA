import statistics
from typing import List, Dict, Any, Callable
from .degradation_service import median_pairwise_slope

SOH_EOL_THRESHOLD = 0.80
RUL_CAP = 100
SHORT_WINDOW = 15
LONG_WINDOW = 30
BLEND_SHORT_WEIGHT = 0.3
BLEND_LONG_WEIGHT = 0.7
MIN_HISTORY_FOR_PER_ASSET_FIT = 10
FLAT_SLOPE_GUARD = -0.00001

TIER_HEALTHY_MIN_SOH = 0.85
TIER_WATCH_MIN_SOH = 0.70

ANOMALY_STD_DEV_THRESHOLD = 2.0

def estimate_band_width(window_cycles: List[int], window_soh: List[float], current_soh: float) -> float:
    slopes = []
    n = len(window_cycles)
    for i in range(n):
        for j in range(i+1, n):
            if window_cycles[j] != window_cycles[i]:
                slopes.append((window_soh[j] - window_soh[i]) / (window_cycles[j] - window_cycles[i]))
    
    if not slopes or len(slopes) < 2:
        slope_std = 0.0
    else:
        slope_std = statistics.stdev(slopes)
    
    band = abs((SOH_EOL_THRESHOLD - current_soh) / max(slope_std, 1e-6))
    band = band * 0.5
    return min(max(band, 0.0), RUL_CAP)

def get_population_median_slope(all_histories: Dict[str, Dict[str, list]]) -> float:
    # all_histories is a dict of battery_id -> {'cycles': [...], 'soh': [...]}
    slopes = []
    for batt_id, hist in all_histories.items():
        if len(hist['cycles']) >= 30:
            cycles = hist['cycles']
            soh = hist['soh']
            
            short_cycles = cycles[-SHORT_WINDOW:]
            short_soh = soh[-SHORT_WINDOW:]
            
            long_cycles = cycles[-LONG_WINDOW:]
            long_soh = soh[-LONG_WINDOW:]
            
            slope_short = median_pairwise_slope(short_cycles, short_soh)
            slope_long = median_pairwise_slope(long_cycles, long_soh)
            slope_blend = BLEND_SHORT_WEIGHT * slope_short + BLEND_LONG_WEIGHT * slope_long
            slopes.append(slope_blend)
            
    if not slopes:
        return 0.0
    return statistics.median(slopes)

def temperature_anomaly(history_temps: List[float]) -> bool:
    if not history_temps or len(history_temps) < 2:
        return False
    mean_temp = statistics.mean(history_temps)
    std_temp = statistics.stdev(history_temps) if len(history_temps) > 1 else 0.0
    latest_temp = history_temps[-1]
    return abs(latest_temp - mean_temp) > ANOMALY_STD_DEV_THRESHOLD * std_temp

def voltage_sag_anomaly(history_volts: List[float]) -> bool:
    if not history_volts or len(history_volts) < 2:
        return False
    mean_v = statistics.mean(history_volts)
    std_v = statistics.stdev(history_volts) if len(history_volts) > 1 else 0.0
    latest_v = history_volts[-1]
    return (mean_v - latest_v) > ANOMALY_STD_DEV_THRESHOLD * std_v

def compute_rul(battery_id: str, history: Dict[str, list], get_pop_slope_fn: Callable[[], float]) -> dict:
    """
    history expects a dict with lists:
    {'cycles': [...], 'soh': [...]}
    It is assumed that history is ordered ascending by cycle.
    """
    cycles = history['cycles']
    soh = history['soh']
    
    n = len(cycles)
    if n == 0:
        raise ValueError("Empty history")
        
    current_soh = soh[-1]
    current_cycle = cycles[-1]

    if n < MIN_HISTORY_FOR_PER_ASSET_FIT:
        slope_blend = get_pop_slope_fn()
        confidence_level = "low_population_estimate"
        slope_source_window_cycles = cycles
        slope_source_window_soh = soh
    else:
        short_cycles = cycles[-SHORT_WINDOW:]
        short_soh = soh[-SHORT_WINDOW:]
        long_cycles = cycles[-LONG_WINDOW:] if n >= LONG_WINDOW else cycles
        long_soh = soh[-LONG_WINDOW:] if n >= LONG_WINDOW else soh
        
        slope_short = median_pairwise_slope(short_cycles, short_soh)
        slope_long = median_pairwise_slope(long_cycles, long_soh)
        slope_blend = BLEND_SHORT_WEIGHT * slope_short + BLEND_LONG_WEIGHT * slope_long
        confidence_level = "asset_specific"
        slope_source_window_cycles = long_cycles
        slope_source_window_soh = long_soh

    if slope_blend >= FLAT_SLOPE_GUARD:
        rul_cycles = float(RUL_CAP)
    else:
        rul_cycles = (SOH_EOL_THRESHOLD - current_soh) / slope_blend
        rul_cycles = max(0.0, min(rul_cycles, float(RUL_CAP)))

    confidence_band_cycles = estimate_band_width(slope_source_window_cycles, slope_source_window_soh, current_soh)

    if current_soh < TIER_WATCH_MIN_SOH:
        risk_tier = "Critical"
    elif current_soh < TIER_HEALTHY_MIN_SOH:
        risk_tier = "Watch"
    else:
        risk_tier = "Healthy"

    return {
        "battery_id": battery_id,
        "current_soh": round(current_soh, 4),
        "current_cycle": current_cycle,
        "rul_cycles": round(rul_cycles, 1),
        "confidence_band_cycles": round(confidence_band_cycles, 1),
        "confidence_level": confidence_level,
        "risk_tier": risk_tier,
        "slope_blend": round(slope_blend, 6),
    }
