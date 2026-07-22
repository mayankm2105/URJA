import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Absolute DB path relative to this file, not the CWD
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(_BASE_DIR, 'netzero.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Fleet(Base):
    __tablename__ = "fleets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    operator = Column(String)
    asset_class = Column(String)           # freight, mining, logistics, construction
    total_vehicles = Column(Integer)
    ev_vehicles = Column(Integer)
    diesel_vehicles = Column(Integer)
    avg_daily_km = Column(Float)
    avg_payload_tons = Column(Float)
    hub_city = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    net_zero_target_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    routes = relationship("Route", back_populates="fleet")
    emissions = relationship("EmissionRecord", back_populates="fleet")


class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    fleet_id = Column(Integer, ForeignKey("fleets.id"))
    name = Column(String)
    origin_city = Column(String)
    dest_city = Column(String)
    origin_lat = Column(Float)
    origin_lon = Column(Float)
    dest_lat = Column(Float)
    dest_lon = Column(Float)
    distance_km = Column(Float)
    trips_per_month = Column(Integer)
    vehicle_type = Column(String)       # diesel / EV
    payload_tons = Column(Float)
    co2_per_km_kg = Column(Float)       # diesel baseline
    ev_co2_per_km_kg = Column(Float)    # EV equivalent
    is_electrified = Column(Boolean, default=False)
    fleet = relationship("Fleet", back_populates="routes")


class EmissionRecord(Base):
    __tablename__ = "emission_records"
    id = Column(Integer, primary_key=True, index=True)
    fleet_id = Column(Integer, ForeignKey("fleets.id"))
    year = Column(Integer)
    month = Column(Integer)
    scope1_tons = Column(Float)         # Direct diesel combustion
    scope3_tons = Column(Float)         # Upstream fuel, supply chain
    ev_avoided_tons = Column(Float)     # CO2 avoided due to EVs
    target_tons = Column(Float)         # Net zero trajectory
    fleet = relationship("Fleet", back_populates="emissions")


class NetZeroCommitment(Base):
    __tablename__ = "net_zero_commitments"
    id = Column(Integer, primary_key=True, index=True)
    organization = Column(String)
    baseline_year = Column(Integer)
    target_year = Column(Integer)
    baseline_scope1_tons = Column(Float)
    baseline_scope3_tons = Column(Float)
    reduction_target_pct = Column(Float)    # e.g. 0.45 for 45%
    current_reduction_pct = Column(Float)
    status = Column(String)                 # on_track / at_risk / off_track


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    material = Column(String)           # lithium, cobalt, NMC cells, LFP cells
    country = Column(String)
    risk_score = Column(Float)          # 0-100
    carbon_intensity = Column(Float)    # kg CO2 / kg material
    concentration_pct = Column(Float)   # % of total supply from this supplier


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
