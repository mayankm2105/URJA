import pytest
from app.services.degradation_service import compute_soh, median_pairwise_slope

def test_compute_soh():
    # 1. Given a hand-constructed list of (cycle, capacity) pairs
    cycles = [1, 2, 3]
    capacities = [2.0, 1.8, 1.6]
    sohs = compute_soh(cycles, capacities)
    # assert compute_soh returns capacity[i] / capacity[0] exactly
    assert sohs == [1.0, 0.9, 0.8]

def test_median_pairwise_slope_linear():
    # 2. Given a hand-constructed perfectly linear SoH series
    # e.g. soh decreasing by exactly 0.001 per cycle for 20 cycles with zero noise
    cycles = list(range(1, 21))
    sohs = [1.0 - 0.001 * (c - 1) for c in cycles]
    slope = median_pairwise_slope(cycles, sohs)
    # assert median_pairwise_slope returns -0.001 within float tolerance
    assert abs(slope - (-0.001)) < 1e-9

def test_median_pairwise_slope_flat():
    # 3. Given a flat SoH series (no change across cycles)
    cycles = list(range(1, 10))
    sohs = [0.85] * 9
    slope = median_pairwise_slope(cycles, sohs)
    # assert median_pairwise_slope returns 0
    assert abs(slope - 0.0) < 1e-9
