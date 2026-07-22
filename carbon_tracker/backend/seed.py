"""
Seed realistic Indian EV fleet data for the Net Zero tracker.
12 industrial operators, 30 routes, 36 months of emission records.
"""
import random
from datetime import datetime
from database import SessionLocal, Base, engine, Fleet, Route, EmissionRecord, NetZeroCommitment, Supplier
from services.carbon_engine import (
    diesel_co2_per_km, ev_co2_per_km, scope1_monthly, scope3_monthly,
    scope3_monthly_blended, avoided_emissions, net_zero_trajectory
)

random.seed(42)


FLEETS = [
    {"name": "Tata Steel Intra-Plant Fleet", "operator": "Tata Steel", "asset_class": "intra-plant logistics",
     "total_vehicles": 120, "ev_vehicles": 28, "hub_city": "Jamshedpur",
     "lat": 22.8046, "lon": 86.2029, "avg_daily_km": 80, "avg_payload_tons": 8, "net_zero_target_year": 2040},

    {"name": "Mahindra Logistics Pune Hub", "operator": "Mahindra Logistics", "asset_class": "logistics",
     "total_vehicles": 85, "ev_vehicles": 12, "hub_city": "Pune",
     "lat": 18.5204, "lon": 73.8567, "avg_daily_km": 220, "avg_payload_tons": 12, "net_zero_target_year": 2035},

    {"name": "Adani Ports Freight Mundra", "operator": "Adani Ports", "asset_class": "freight",
     "total_vehicles": 200, "ev_vehicles": 8, "hub_city": "Mundra",
     "lat": 22.8392, "lon": 69.7218, "avg_daily_km": 300, "avg_payload_tons": 25, "net_zero_target_year": 2038},

    {"name": "Flipkart Last-Mile Delhi NCR", "operator": "Flipkart", "asset_class": "last-mile delivery",
     "total_vehicles": 340, "ev_vehicles": 180, "hub_city": "Delhi",
     "lat": 28.6139, "lon": 77.2090, "avg_daily_km": 120, "avg_payload_tons": 2, "net_zero_target_year": 2030},

    {"name": "JSW Steel Mining Fleet", "operator": "JSW Steel", "asset_class": "mining",
     "total_vehicles": 60, "ev_vehicles": 2, "hub_city": "Bellary",
     "lat": 15.1394, "lon": 76.9214, "avg_daily_km": 50, "avg_payload_tons": 40, "net_zero_target_year": 2045},

    {"name": "Zomato Hyper-Local Chennai", "operator": "Zomato", "asset_class": "last-mile delivery",
     "total_vehicles": 500, "ev_vehicles": 290, "hub_city": "Chennai",
     "lat": 13.0827, "lon": 80.2707, "avg_daily_km": 90, "avg_payload_tons": 0.5, "net_zero_target_year": 2028},

    {"name": "L&T Construction Bengaluru", "operator": "L&T", "asset_class": "construction",
     "total_vehicles": 75, "ev_vehicles": 5, "hub_city": "Bengaluru",
     "lat": 12.9716, "lon": 77.5946, "avg_daily_km": 45, "avg_payload_tons": 15, "net_zero_target_year": 2040},

    {"name": "Blue Dart Express Mumbai", "operator": "Blue Dart", "asset_class": "logistics",
     "total_vehicles": 150, "ev_vehicles": 35, "hub_city": "Mumbai",
     "lat": 19.0760, "lon": 72.8777, "avg_daily_km": 180, "avg_payload_tons": 5, "net_zero_target_year": 2032},

    {"name": "NTPC Renewable Freight", "operator": "NTPC", "asset_class": "freight",
     "total_vehicles": 90, "ev_vehicles": 10, "hub_city": "Nagpur",
     "lat": 21.1458, "lon": 79.0882, "avg_daily_km": 250, "avg_payload_tons": 20, "net_zero_target_year": 2035},

    {"name": "Amazon India Last Mile Kolkata", "operator": "Amazon India", "asset_class": "last-mile delivery",
     "total_vehicles": 420, "ev_vehicles": 195, "hub_city": "Kolkata",
     "lat": 22.5726, "lon": 88.3639, "avg_daily_km": 110, "avg_payload_tons": 1.5, "net_zero_target_year": 2030},

    {"name": "Coal India Mining Fleet", "operator": "Coal India", "asset_class": "mining",
     "total_vehicles": 180, "ev_vehicles": 0, "hub_city": "Dhanbad",
     "lat": 23.7957, "lon": 86.4304, "avg_daily_km": 40, "avg_payload_tons": 50, "net_zero_target_year": 2050},

    {"name": "Delhivery Intercity Freight", "operator": "Delhivery", "asset_class": "freight",
     "total_vehicles": 110, "ev_vehicles": 6, "hub_city": "Gurgaon",
     "lat": 28.4595, "lon": 77.0266, "avg_daily_km": 400, "avg_payload_tons": 18, "net_zero_target_year": 2036},
]


ROUTES = [
    # (origin, origin_lat, origin_lon, dest, dest_lat, dest_lon, km, trips/month)
    ("Mumbai", 19.076, 72.878, "Pune", 18.520, 73.857, 150, 180),
    ("Delhi", 28.614, 77.209, "Jaipur", 26.912, 75.787, 268, 90),
    ("Chennai", 13.083, 80.271, "Bengaluru", 12.972, 77.595, 346, 120),
    ("Kolkata", 22.573, 88.364, "Bhubaneswar", 20.296, 85.825, 440, 60),
    ("Pune", 18.520, 73.857, "Nashik", 19.998, 73.780, 210, 75),
    ("Jamshedpur", 22.805, 86.203, "Kolkata", 22.573, 88.364, 280, 45),
    ("Mundra", 22.839, 69.722, "Ahmedabad", 23.023, 72.572, 380, 90),
    ("Bengaluru", 12.972, 77.595, "Mysuru", 12.296, 76.639, 145, 60),
    ("Delhi", 28.614, 77.209, "Chandigarh", 30.734, 76.779, 250, 80),
    ("Mumbai", 19.076, 72.878, "Surat", 21.170, 72.831, 290, 100),
    ("Hyderabad", 17.385, 78.487, "Vijayawada", 16.506, 80.648, 275, 55),
    ("Nagpur", 21.146, 79.088, "Raipur", 21.251, 81.629, 295, 40),
    ("Lucknow", 26.847, 80.947, "Kanpur", 26.449, 80.331, 85, 120),
    ("Ahmedabad", 23.023, 72.572, "Rajkot", 22.303, 70.802, 220, 70),
    ("Chennai", 13.083, 80.271, "Coimbatore", 11.017, 76.966, 500, 45),
    ("Gurgaon", 28.460, 77.027, "Agra", 27.176, 78.008, 210, 95),
    ("Bellary", 15.139, 76.921, "Hospet", 15.269, 76.387, 15, 200),
    ("Dhanbad", 23.796, 86.430, "Bokaro", 23.669, 85.989, 55, 150),
    ("Mumbai", 19.076, 72.878, "Nagpur", 21.146, 79.088, 840, 30),
    ("Delhi", 28.614, 77.209, "Lucknow", 26.847, 80.947, 550, 60),
    ("Kolkata", 22.573, 88.364, "Patna", 25.594, 85.137, 600, 35),
    ("Chennai", 13.083, 80.271, "Madurai", 9.925, 78.120, 450, 50),
    ("Pune", 18.520, 73.857, "Mumbai", 19.076, 72.878, 150, 200),
    ("Bengaluru", 12.972, 77.595, "Hyderabad", 17.385, 78.487, 570, 55),
    ("Jamshedpur", 22.805, 86.203, "Ranchi", 23.344, 85.310, 130, 80),
    ("Ahmedabad", 23.023, 72.572, "Vadodara", 22.307, 73.181, 110, 130),
    ("Nagpur", 21.146, 79.088, "Pune", 18.520, 73.857, 590, 40),
    ("Delhi", 28.614, 77.209, "Amritsar", 31.634, 74.872, 450, 50),
    ("Mumbai", 19.076, 72.878, "Goa", 15.491, 73.829, 590, 35),
    ("Hyderabad", 17.385, 78.487, "Nagpur", 21.146, 79.088, 500, 45),
]

NET_ZERO_COMMITMENTS = [
    {"organization": "Tata Group Industrial Fleet", "baseline_year": 2019, "target_year": 2040,
     "baseline_scope1_tons": 85000, "baseline_scope3_tons": 18700,
     "reduction_target_pct": 0.90, "current_reduction_pct": 0.223, "status": "on_track"},
    {"organization": "Mahindra Group Fleet", "baseline_year": 2020, "target_year": 2035,
     "baseline_scope1_tons": 42000, "baseline_scope3_tons": 9240,
     "reduction_target_pct": 0.75, "current_reduction_pct": 0.189, "status": "on_track"},
    {"organization": "Adani Group Logistics", "baseline_year": 2021, "target_year": 2038,
     "baseline_scope1_tons": 120000, "baseline_scope3_tons": 26400,
     "reduction_target_pct": 0.70, "current_reduction_pct": 0.062, "status": "at_risk"},
    {"organization": "E-Commerce India Delivery Cos", "baseline_year": 2020, "target_year": 2030,
     "baseline_scope1_tons": 28000, "baseline_scope3_tons": 6160,
     "reduction_target_pct": 0.50, "current_reduction_pct": 0.412, "status": "on_track"},
]

SUPPLIERS = [
    {"name": "Ganfeng Lithium", "material": "Lithium (LiOH)", "country": "China",
     "risk_score": 78.5, "carbon_intensity": 12.4, "concentration_pct": 32.0},
    {"name": "Glencore", "material": "Cobalt", "country": "DRC/Switzerland",
     "risk_score": 85.2, "carbon_intensity": 8.7, "concentration_pct": 28.0},
    {"name": "CATL", "material": "NMC Cells", "country": "China",
     "risk_score": 65.0, "carbon_intensity": 18.2, "concentration_pct": 45.0},
    {"name": "BYD", "material": "LFP Cells", "country": "China",
     "risk_score": 60.0, "carbon_intensity": 14.8, "concentration_pct": 22.0},
    {"name": "Vale", "material": "Nickel", "country": "Brazil/Indonesia",
     "risk_score": 55.3, "carbon_intensity": 6.2, "concentration_pct": 18.0},
    {"name": "Amara Raja Energy", "material": "LFP Cells", "country": "India",
     "risk_score": 32.1, "carbon_intensity": 11.2, "concentration_pct": 8.0},
    {"name": "Exide Industries", "material": "Battery Packs", "country": "India",
     "risk_score": 28.4, "carbon_intensity": 9.8, "concentration_pct": 12.0},
]


def seed_database():
    db = SessionLocal()
    try:
        if db.query(Fleet).count() > 0:
            print("Database already seeded.")
            return

        print("Seeding fleets...")
        fleet_objs = []
        for f in FLEETS:
            total = f["total_vehicles"]
            ev = f["ev_vehicles"]
            diesel = total - ev
            fleet = Fleet(
                name=f["name"], operator=f["operator"], asset_class=f["asset_class"],
                total_vehicles=total, ev_vehicles=ev, diesel_vehicles=diesel,
                avg_daily_km=f["avg_daily_km"], avg_payload_tons=f["avg_payload_tons"],
                hub_city=f["hub_city"], lat=f["lat"], lon=f["lon"],
                net_zero_target_year=f["net_zero_target_year"],
            )
            db.add(fleet)
            fleet_objs.append(fleet)
        db.flush()

        print("Seeding routes...")
        fleet_cycle = 0
        for i, r in enumerate(ROUTES):
            orig, o_lat, o_lon, dest, d_lat, d_lon, km, trips = r
            fleet_obj = fleet_objs[fleet_cycle % len(fleet_objs)]
            fleet_cycle += 1
            payload = fleet_obj.avg_payload_tons
            d_co2 = diesel_co2_per_km(payload)
            e_co2 = ev_co2_per_km(payload)
            # Some routes already electrified if fleet has EVs
            is_elec = (fleet_obj.ev_vehicles / max(fleet_obj.total_vehicles, 1)) > 0.3 and i % 3 == 0

            route = Route(
                fleet_id=fleet_obj.id, name=f"{orig} → {dest}",
                origin_city=orig, dest_city=dest,
                origin_lat=o_lat, origin_lon=o_lon,
                dest_lat=d_lat, dest_lon=d_lon,
                distance_km=km, trips_per_month=trips,
                vehicle_type="EV" if is_elec else "Diesel",
                payload_tons=payload, co2_per_km_kg=round(d_co2, 4),
                ev_co2_per_km_kg=round(e_co2, 4), is_electrified=is_elec,
            )
            db.add(route)
        db.flush()

        print("Seeding emission records (36 months)...")
        for fleet_obj in fleet_objs:
            ev_pct = fleet_obj.ev_vehicles / max(fleet_obj.total_vehicles, 1)
            d_co2 = diesel_co2_per_km(fleet_obj.avg_payload_tons)
            e_co2 = ev_co2_per_km(fleet_obj.avg_payload_tons)
            base_km = fleet_obj.avg_daily_km * fleet_obj.diesel_vehicles * 30

            # Calculate a fixed baseline for the net zero trajectory based on initial emissions
            initial_s1 = scope1_monthly(base_km, 1, d_co2) * (1 - ev_pct * 0.5)
            traj = net_zero_trajectory(initial_s1 * 12, fleet_obj.net_zero_target_year, baseline_year=2023)

            # Different fleets have different adoption curves
            fleet_ev_momentum = random.uniform(0.05, 0.25)
            fleet_volatility = random.uniform(0.01, 0.04)

            for year in [2023, 2024, 2025]:
                for month in range(1, 13):
                    if year == 2025 and month > 6:
                        break
                    
                    # Add some realistic noise to monthly mileage (seasonal/random)
                    noise = random.uniform(-fleet_volatility, fleet_volatility)
                    growth = 1 + (year - 2023) * 0.03 + (month - 1) * 0.002 + noise
                    
                    # EV growth accelerates over time based on fleet momentum
                    ev_growth = 1 + (year - 2023) * fleet_ev_momentum
                    
                    km = base_km * max(0.5, growth)
                    s1 = scope1_monthly(km, 1, d_co2)
                    s1 = s1 * max(0.1, (1 - ev_pct * ev_growth * 0.5))
                    ev_share = min(1.0, ev_pct * ev_growth * 0.5)
                    s3 = scope3_monthly_blended(s1, ev_share)
                    
                    avoided = avoided_emissions(d_co2, e_co2, fleet_obj.avg_daily_km, fleet_obj.ev_vehicles * 30 * ev_growth)

                    # Smooth monthly target (interpolate between years)
                    target_annual = traj.get(year, initial_s1 * 12)
                    next_target_annual = traj.get(year + 1, target_annual * 0.95)
                    # Interpolate down smoothly each month
                    monthly_target = (target_annual - ((target_annual - next_target_annual) * (month - 1) / 12)) / 12

                    rec = EmissionRecord(
                        fleet_id=fleet_obj.id, year=year, month=month,
                        scope1_tons=round(s1, 2), scope3_tons=round(s3, 2),
                        ev_avoided_tons=round(avoided, 2), target_tons=round(monthly_target, 2),
                    )
                    db.add(rec)

        print("Seeding net zero commitments...")
        for c in NET_ZERO_COMMITMENTS:
            db.add(NetZeroCommitment(**c))

        print("Seeding suppliers...")
        for s in SUPPLIERS:
            db.add(Supplier(**s))

        db.commit()
        print("✅ Seed complete!")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
