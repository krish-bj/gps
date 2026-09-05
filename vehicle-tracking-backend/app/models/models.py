from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default="user")  # 'user' or 'admin'

    assigned_route_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bus_routes.id", ondelete="SET NULL"), nullable=True)
    assigned_vehicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)

    assigned_route: Mapped[Optional["BusRoute"]] = relationship("BusRoute", back_populates="assigned_users")
    assigned_vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="assigned_users")

class BusRoute(Base):
    __tablename__ = "bus_routes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    route_code: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    route_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_location: Mapped[str] = mapped_column(String, nullable=False)
    end_location: Mapped[str] = mapped_column(String, nullable=False)
    waypoints_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of waypoint dicts
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="route")
    assigned_users: Mapped[List["User"]] = relationship("User", back_populates="assigned_route")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vehicle_code: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    license_plate: Mapped[str] = mapped_column(String, nullable=False)
    model_name: Mapped[str] = mapped_column(String, default="Standard Transit Bus")
    status: Mapped[str] = mapped_column(String, default="ONLINE")  # ONLINE, MOVING, IDLE, OFFLINE

    assigned_route_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bus_routes.id", ondelete="SET NULL"), nullable=True)

    last_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    route: Mapped[Optional["BusRoute"]] = relationship("BusRoute", back_populates="vehicles")
    assigned_users: Mapped[List["User"]] = relationship("User", back_populates="assigned_vehicle")
    telemetry_logs: Mapped[List["GPSTelemetry"]] = relationship("GPSTelemetry", back_populates="vehicle", cascade="all, delete-orphan")

class GPSTelemetry(Base):
    __tablename__ = "gps_telemetry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    speed_kmh: Mapped[float] = mapped_column(Float, default=0.0)
    heading: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="telemetry_logs")
