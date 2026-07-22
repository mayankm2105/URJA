"""
Carbon Accounting Engine
Calculates Scope 1 & Scope 3 emissions for EV vs Diesel fleets.

Scope 1: Direct CO2 from diesel combustion (fleet operations)
Scope 3: Upstream fuel extraction, supply chain transport, grid electricity (for EV)

Emission Factors (India-specific, 2024-25):
  - Diesel: 2.68 kg CO2e / litre
  - Diesel fuel economy (heavy truck): ~4.5 km/litre at 20T payload
  - India grid: 0.82 kg CO2e / kWh (CEA 2024)
  - EV consumption: ~1.8 kWh / km (heavy EV truck, loaded)
  - Scope 3 upstream multiplier for diesel: 1.22 (22% upstream emissions)
  - Scope 3 upstream multiplier for grid electricity: 1.10 (10% grid losses)
"""

DIESEL_CO2_PER_LITRE = 2.68          # kg CO2e
DIESEL_KM_PER_LITRE_BASE = 4.5       # km/l at 20T payload
GRID_CO2_PER_KWH = 0.82              # kg CO2e (India CEA 2024)
EV_KWH_PER_KM = 1.8                  # kWh/km heavy truck
SCOPE3_DIESEL_MULTIPLIER = 1.22
SCOPE3_EV_MULTIPLIER = 1.10
RENEWABLE_ENERGY_FACTOR = 0.35        # 35% of EV charging from renewables in India


def diesel_co2_per_km(payload_tons: float) -> float:
    """Return kg CO2e per km for a diesel truck at given payload."""
    if payload_tons <= 2.0:
        # Last-mile delivery van: ~10 km/litre
        km_per_litre = 10.0
    elif payload_tons <= 10.0:
        # Medium freight/logistics: ~6.0 km/litre
        km_per_litre = 6.0
    elif payload_tons <= 20.0:
        # Heavy freight: ~4.0 km/litre
        km_per_litre = 4.0
    else:
        # Heavy mining/heavy haulage: ~2.0 km/litre
        km_per_litre = 2.0
    return DIESEL_CO2_PER_LITRE / km_per_litre


def ev_co2_per_km(payload_tons: float, renewable_pct: float = RENEWABLE_ENERGY_FACTOR) -> float:
    """Return kg CO2e per km for an EV truck (accounting for grid mix)."""
    if payload_tons <= 2.0:
        # Last-mile light EV (e.g. Tata Ace EV): ~0.25 kWh/km
        kwh_per_km = 0.25
    elif payload_tons <= 10.0:
        # Medium cargo EV (e.g. Tata Ultra EV): ~0.75 kWh/km
        kwh_per_km = 0.75
    elif payload_tons <= 20.0:
        # Heavy freight EV: ~1.5 kWh/km
        kwh_per_km = 1.5
    else:
        # Heavy mining EV / heavy truck: ~2.2 kWh/km
        kwh_per_km = 2.2
        
    effective_grid_co2 = GRID_CO2_PER_KWH * (1 - renewable_pct)
    return kwh_per_km * effective_grid_co2



def scope1_monthly(distance_km: float, trips: int, co2_per_km: float) -> float:
    """Scope 1: direct diesel combustion, tonnes CO2e."""
    return (distance_km * trips * co2_per_km) / 1000.0


def scope3_monthly(scope1: float, is_ev: bool = False) -> float:
    """Scope 3: upstream fuel / electricity supply chain."""
    multiplier = SCOPE3_EV_MULTIPLIER if is_ev else SCOPE3_DIESEL_MULTIPLIER
    return scope1 * (multiplier - 1.0)


def scope3_monthly_blended(scope1: float, ev_share: float) -> float:
    """Scope 3: blended multiplier for electricity grid & diesel fuel supply chain."""
    blended_multiplier = (SCOPE3_EV_MULTIPLIER * ev_share) + (SCOPE3_DIESEL_MULTIPLIER * (1 - ev_share))
    return scope1 * (blended_multiplier - 1.0)


def avoided_emissions(diesel_co2_per_km: float, ev_co2_per_km_val: float,
                      distance_km: float, trips: int) -> float:
    """Tonnes of CO2e avoided by switching from diesel to EV on a route."""
    diesel_total = (distance_km * trips * diesel_co2_per_km) / 1000.0
    ev_total = (distance_km * trips * ev_co2_per_km_val) / 1000.0
    return max(0, diesel_total - ev_total)


def net_zero_trajectory(baseline: float, target_year: int, baseline_year: int = 2022) -> dict:
    """
    Generate year-by-year net zero reduction trajectory.
    Uses exponential decay curve aligned to SBTi 1.5°C pathway (4.2% annual reduction).
    """
    import math
    years = list(range(baseline_year, target_year + 1))
    annual_reduction_rate = 1 - math.exp(math.log(0.1) / (target_year - baseline_year))
    trajectory = {}
    current = baseline
    for y in years:
        trajectory[y] = round(current, 2)
        current *= (1 - annual_reduction_rate)
    return trajectory


def electrification_readiness_index(
    ev_penetration_pct: float,
    avg_daily_km: float,
    avg_payload_tons: float,
    asset_class: str
) -> float:
    """
    Score 0-100: How ready is this fleet for electrification?
    Considers current EV adoption, route suitability, payload, asset class.
    """
    # Base: current EV penetration
    score = ev_penetration_pct * 0.4

    # Route suitability: shorter daily routes = better EV candidate
    route_score = max(0, 100 - (avg_daily_km - 100) * 0.3)
    score += min(route_score, 30) * 0.3

    # Payload factor: lighter = easier to electrify
    payload_score = max(0, 100 - avg_payload_tons * 2.5)
    score += min(payload_score, 100) * 0.2

    # Asset class multiplier
    class_multipliers = {
        "intra-plant logistics": 1.3,
        "last-mile delivery": 1.2,
        "logistics": 1.1,
        "freight": 0.9,
        "construction": 0.75,
        "mining": 0.6,
    }
    multiplier = class_multipliers.get(asset_class.lower(), 1.0)

    return min(100.0, round(score * multiplier, 1))


def impact_score(annual_co2_tons: float, potential_saving_tons: float,
                 readiness_index: float) -> float:
    """
    Combined impact score for prioritisation (0-100).
    Balances carbon impact potential with operational readiness.
    """
    carbon_weight = 0.5
    saving_weight = 0.3
    readiness_weight = 0.2

    # Normalise (assume max realistic values)
    carbon_norm = min(annual_co2_tons / 5000.0, 1.0) * 100
    saving_norm = min(potential_saving_tons / 3000.0, 1.0) * 100
    readiness_norm = readiness_index

    return round(
        carbon_norm * carbon_weight +
        saving_norm * saving_weight +
        readiness_norm * readiness_weight,
        1
    )
