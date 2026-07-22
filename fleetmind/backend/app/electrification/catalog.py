"""India EV procurement catalog.

A representative set of commercially-available Indian electric commercial
vehicles, by class, with the attributes the readiness/procurement engine needs.
Specs are indicative (manufacturer-claimed range derated to real-world in the
engine) and prices are on-road INR order-of-magnitude figures for FY26.

Fields
------
vehicle_class   : matches a candidate's class (cargo_3w / passenger_3w / lcv /
                  sedan_taxi / city_bus / mcv_truck)
range_km        : manufacturer-claimed range on a full charge
payload_kg      : rated payload (0 for passenger vehicles, seats tracked sep.)
battery_kwh     : usable pack energy
kwh_per_km      : real-world energy consumption
charge_power_kw : typical depot AC / onboard charge power used for dwell-time calc
fast_charge     : DC fast-charge supported
price_inr       : indicative on-road price (INR)
lead_weeks      : typical procurement / delivery lead time
"""
from __future__ import annotations

LAKH = 100_000
CRORE = 10_000_000

EV_CATALOG: list[dict] = [
    # ---- Cargo 3-wheelers (last-mile logistics) ----
    {
        "id": "euler-hiload", "chemistry": "LFP", "model": "Euler HiLoad EV", "oem": "Euler Motors",
        "vehicle_class": "cargo_3w", "range_km": 110, "payload_kg": 688,
        "battery_kwh": 12.4, "kwh_per_km": 0.11, "charge_power_kw": 5.0,
        "fast_charge": True, "price_inr": int(5.0 * LAKH), "lead_weeks": 6,
    },
    {
        "id": "mahindra-treo-zor", "chemistry": "NMC", "model": "Mahindra Treo Zor", "oem": "Mahindra",
        "vehicle_class": "cargo_3w", "range_km": 125, "payload_kg": 550,
        "battery_kwh": 10.2, "kwh_per_km": 0.09, "charge_power_kw": 3.3,
        "fast_charge": False, "price_inr": int(3.6 * LAKH), "lead_weeks": 5,
    },
    {
        "id": "omega-rage", "chemistry": "LFP", "model": "Omega Seiki Rage+", "oem": "Omega Seiki",
        "vehicle_class": "cargo_3w", "range_km": 110, "payload_kg": 500,
        "battery_kwh": 10.0, "kwh_per_km": 0.10, "charge_power_kw": 3.3,
        "fast_charge": False, "price_inr": int(3.9 * LAKH), "lead_weeks": 8,
    },
    # ---- Passenger 3-wheelers (auto) ----
    {
        "id": "mahindra-treo", "chemistry": "NMC", "model": "Mahindra Treo", "oem": "Mahindra",
        "vehicle_class": "passenger_3w", "range_km": 130, "payload_kg": 0,
        "battery_kwh": 7.4, "kwh_per_km": 0.06, "charge_power_kw": 3.3,
        "fast_charge": False, "price_inr": int(3.3 * LAKH), "lead_weeks": 4,
    },
    {
        "id": "piaggio-ape-ecity", "chemistry": "LFP", "model": "Piaggio Ape E-City FX", "oem": "Piaggio",
        "vehicle_class": "passenger_3w", "range_km": 90, "payload_kg": 0,
        "battery_kwh": 7.5, "kwh_per_km": 0.07, "charge_power_kw": 3.0,
        "fast_charge": False, "price_inr": int(3.5 * LAKH), "lead_weeks": 6,
    },
    # ---- Light commercial vehicles (intra-city vans) ----
    {
        "id": "tata-ace-ev", "chemistry": "LFP", "model": "Tata Ace EV", "oem": "Tata Motors",
        "vehicle_class": "lcv", "range_km": 154, "payload_kg": 1000,
        "battery_kwh": 21.3, "kwh_per_km": 0.20, "charge_power_kw": 7.2,
        "fast_charge": True, "price_inr": int(11.0 * LAKH), "lead_weeks": 10,
    },
    {
        "id": "switch-iev4", "chemistry": "NMC", "model": "Switch IeV4", "oem": "Switch Mobility",
        "vehicle_class": "lcv", "range_km": 140, "payload_kg": 800,
        "battery_kwh": 20.0, "kwh_per_km": 0.21, "charge_power_kw": 7.0,
        "fast_charge": True, "price_inr": int(10.5 * LAKH), "lead_weeks": 14,
    },
    # ---- Sedans / fleet taxis ----
    {
        "id": "tata-xpres-t", "chemistry": "LFP", "model": "Tata Xpres-T EV", "oem": "Tata Motors",
        "vehicle_class": "sedan_taxi", "range_km": 213, "payload_kg": 0,
        "battery_kwh": 26.0, "kwh_per_km": 0.13, "charge_power_kw": 7.2,
        "fast_charge": True, "price_inr": int(12.5 * LAKH), "lead_weeks": 8,
    },
    # ---- City buses ----
    {
        "id": "tata-starbus-ev", "chemistry": "LFP", "model": "Tata Starbus EV", "oem": "Tata Motors",
        "vehicle_class": "city_bus", "range_km": 180, "payload_kg": 0,
        "battery_kwh": 200.0, "kwh_per_km": 1.05, "charge_power_kw": 80.0,
        "fast_charge": True, "price_inr": int(1.4 * CRORE), "lead_weeks": 28,
    },
    {
        "id": "switch-eiv12", "chemistry": "NMC", "model": "Switch EiV 12", "oem": "Ashok Leyland / Switch",
        "vehicle_class": "city_bus", "range_km": 250, "payload_kg": 0,
        "battery_kwh": 280.0, "kwh_per_km": 1.10, "charge_power_kw": 120.0,
        "fast_charge": True, "price_inr": int(1.8 * CRORE), "lead_weeks": 32,
    },
    # ---- Medium trucks ----
    {
        "id": "eicher-pro-x", "chemistry": "LFP", "model": "Eicher Pro X EV", "oem": "Eicher / VECV",
        "vehicle_class": "mcv_truck", "range_km": 200, "payload_kg": 5500,
        "battery_kwh": 110.0, "kwh_per_km": 0.55, "charge_power_kw": 60.0,
        "fast_charge": True, "price_inr": int(35.0 * LAKH), "lead_weeks": 24,
    },
]

_BY_CLASS: dict[str, list[dict]] = {}
for _m in EV_CATALOG:
    _BY_CLASS.setdefault(_m["vehicle_class"], []).append(_m)


def models_for_class(vehicle_class: str) -> list[dict]:
    return _BY_CLASS.get(vehicle_class, [])


def get_model(model_id: str) -> dict | None:
    return next((m for m in EV_CATALOG if m["id"] == model_id), None)
