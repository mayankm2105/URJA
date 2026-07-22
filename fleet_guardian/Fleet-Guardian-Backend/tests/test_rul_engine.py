import pytest
from app.services.rul_engine import (
    compute_rul, temperature_anomaly, voltage_sag_anomaly,
    RUL_CAP, SOH_EOL_THRESHOLD, FLAT_SLOPE_GUARD
)

def test_rul_constant_fade():
    # 4. Construct a synthetic battery with a known, constant fade rate of -0.002 per cycle
    # current SoH = 0.85, >=30 cycles
    cycles = list(range(1, 35))
    sohs = [0.85 + 0.002 * (34 - c) for c in cycles] # ends at 0.85
    # Since fade is -0.002, 34th cycle is 0.85. 33rd is 0.852, 1st is 0.85 + 0.002*33
    
    history = {
        'cycles': cycles,
        'soh': sohs,
        'temperature': [25.0] * 34,
        'voltage': [3.6] * 34
    }
    
    result = compute_rul("SYN001", history, lambda: -0.001)
    
    # expected rul = (0.80 - 0.85) / -0.002 = 25.0
    expected_rul = (SOH_EOL_THRESHOLD - 0.85) / -0.002
    
    assert abs(result["rul_cycles"] - expected_rul) <= 1.0

def test_rul_flat_slope():
    # 5. Construct a battery with a flat/improving slope
    cycles = list(range(1, 35))
    sohs = [0.85] * 34
    
    history = {
        'cycles': cycles,
        'soh': sohs,
        'temperature': [25.0] * 34,
        'voltage': [3.6] * 34
    }
    
    result = compute_rul("SYN001", history, lambda: -0.001)
    
    assert result["rul_cycles"] == float(RUL_CAP)

def test_rul_population_fallback():
    # 6. Construct battery with < 10 cycles
    cycles = list(range(1, 8))
    sohs = [0.9] * 7
    history = {
        'cycles': cycles,
        'soh': sohs,
        'temperature': [25.0] * 7,
        'voltage': [3.6] * 7
    }
    
    result = compute_rul("SYN001", history, lambda: -0.003)
    
    assert result["confidence_level"] == "low_population_estimate"
    assert abs(result["slope_blend"] - (-0.003)) < 1e-9

def test_risk_tiers():
    # 7. current SoH of 0.90, 0.75, 0.60 -> Healthy, Watch, Critical
    def make_hist(soh_val):
        return {
            'cycles': list(range(1, 35)),
            'soh': [soh_val] * 34,
            'temperature': [25.0] * 34,
            'voltage': [3.6] * 34
        }
        
    res_healthy = compute_rul("1", make_hist(0.90), lambda: -0.001)
    res_watch = compute_rul("2", make_hist(0.75), lambda: -0.001)
    res_critical = compute_rul("3", make_hist(0.60), lambda: -0.001)
    
    assert res_healthy["risk_tier"] == "Healthy"
    assert res_watch["risk_tier"] == "Watch"
    assert res_critical["risk_tier"] == "Critical"

def test_rul_bounds():
    # 8. Assert rul_cycles is NEVER negative and NEVER exceeds RUL_CAP
    # Test random synthetic batteries
    import random
    for i in range(20):
        c = random.randint(30, 100)
        cycles = list(range(1, c+1))
        sohs = [random.uniform(0.5, 1.0) for _ in cycles]
        history = {
            'cycles': cycles,
            'soh': sohs,
            'temperature': [25.0] * c,
            'voltage': [3.6] * c
        }
        res = compute_rul(f"RND{i}", history, lambda: -0.001)
        assert 0.0 <= res["rul_cycles"] <= float(RUL_CAP)

def test_temperature_anomaly():
    # 9. Injected temperature spike
    temps = [25.0] * 10
    assert not temperature_anomaly(temps)
    
    temps.append(50.0) # spike
    assert temperature_anomaly(temps)

def test_voltage_sag_anomaly():
    # 10. Injected voltage sag
    volts = [3.6, 3.6, 3.6, 3.6, 3.59, 3.61]
    assert not voltage_sag_anomaly(volts)
    
    volts.append(3.1) # sag
    assert voltage_sag_anomaly(volts)

def test_anomaly_flags_do_not_leak():
    # 11. Assert that changing flag values has zero effect on rul_cycles or slope_blend
    cycles = list(range(1, 35))
    sohs = [0.85 - 0.001 * c for c in cycles]
    temps = [25.0] * 34
    volts = [3.6] * 34
    
    hist1 = {
        'cycles': cycles,
        'soh': sohs,
        'temperature': temps,
        'voltage': volts
    }
    
    hist2 = {
        'cycles': cycles,
        'soh': sohs,
        'temperature': temps[:-1] + [50.0],
        'voltage': volts
    }
    
    res1 = compute_rul("B", hist1, lambda: -0.001)
    res2 = compute_rul("B", hist2, lambda: -0.001)
    
    assert res1["rul_cycles"] == res2["rul_cycles"]
    assert res1["slope_blend"] == res2["slope_blend"]
