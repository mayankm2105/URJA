from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Asset(Base):
    __tablename__ = "assets"

    battery_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=False)

    cycles = relationship("BatteryCycle", back_populates="asset", cascade="all, delete-orphan")

class BatteryCycle(Base):
    __tablename__ = "battery_cycles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    battery_id = Column(String, ForeignKey("assets.battery_id"), index=True)
    cycle = Column(Integer, nullable=False)
    voltage = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    capacity = Column(Float, nullable=False)
    soh = Column(Float, nullable=False)
    rul = Column(Integer, nullable=True) # Exists in dataset, not returned by live API directly

    asset = relationship("Asset", back_populates="cycles")
