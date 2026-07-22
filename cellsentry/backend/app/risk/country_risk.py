"""Geopolitical baseline risk per country (0-100).

Curated index proxying governance instability + export-control / sanctions
propensity + resource-nationalism, informed by World Bank Worldwide Governance
Indicators and recent (2023-25) trade-policy actions. Higher = riskier source.
"""
from __future__ import annotations

COUNTRY_RISK: dict[str, float] = {
    "DR Congo": 85.0,
    "Russia": 90.0,
    "China": 60.0,
    "Indonesia": 50.0,
    "Philippines": 55.0,
    "Madagascar": 60.0,
    "Mozambique": 55.0,
    "India": 45.0,
    "Argentina": 40.0,
    "Brazil": 40.0,
    "Chile": 35.0,
    "South Korea": 25.0,
    "Australia": 15.0,
    "Belgium": 15.0,
}

DEFAULT_COUNTRY_RISK = 50.0  # "Others" bucket / unknown source


def country_risk(country: str | None) -> float:
    if not country:
        return DEFAULT_COUNTRY_RISK
    return COUNTRY_RISK.get(country, DEFAULT_COUNTRY_RISK)


def geo_from_shares(country_shares: dict[str, float] | None) -> float:
    """Share-weighted geopolitical risk for a raw material's global sourcing mix."""
    if not country_shares:
        return 0.0
    total = sum(country_shares.values()) or 1.0
    return sum((share / total) * country_risk(c) for c, share in country_shares.items())
