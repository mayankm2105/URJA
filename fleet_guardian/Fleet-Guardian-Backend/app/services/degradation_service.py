import statistics
from typing import List

def compute_soh(cycles: List[int], capacities: List[float]) -> List[float]:
    """
    history = ordered cycles for battery_id, ascending by cycle number
    cap_at_cycle_1 = capacity of the first recorded cycle for this battery_id
    for each cycle: soh = capacity / cap_at_cycle_1
    """
    if not capacities:
        return []
    cap_at_cycle_1 = capacities[0]
    return [cap / cap_at_cycle_1 for cap in capacities]

def median_pairwise_slope(cycles: List[int], soh: List[float]) -> float:
    """
    Theil-Sen style median pairwise slope.
    """
    slopes = []
    n = len(cycles)
    for i in range(n):
        for j in range(i+1, n):
            if cycles[j] != cycles[i]:
                slopes.append((soh[j] - soh[i]) / (cycles[j] - cycles[i]))
    if not slopes:
        return 0.0
    return statistics.median(slopes)
