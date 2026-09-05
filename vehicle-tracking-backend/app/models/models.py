from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Float, DateTime, Boolean, ForeignKey, Text, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String(50), default="user")  # 'user' or 'admin'

    # Direct FK assignment attributes for quick access
    assigned_route_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bus_routes.id", ondelete="SET NULL"), nullable=True)
    assigned_vehicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    @property
    def hashed_password(self) -> str:
        return self.password_hash

    @hashed_password.setter
    def hashed_password(self, value: str):
        self.password_hash = value

    assigned_route: Mapped[Optional["BusRoute"]] = relationship("BusRoute", back_populates="assigned_users")
    assigned_vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="assigned_users")
    assignments: Mapped[List["UserAssignment"]] = relationship("UserAssignment", back_populates="user", cascade="all, delete-orphan")

class BusRoute(Base):
    __tablename__ = "bus_routes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    route_code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    route_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_location: Mapped[str] = mapped_column(String(255), nullable=False)
    end_location: Mapped[str] = mapped_column(String(255), nullable=False)
    waypoints_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    vehicles: Mapped[List["Vehicle"]] = relationship("Vehicle", back_populates="route")
    assigned_users: Mapped[List["User"]] = relationship("User", back_populates="assigned_route")
    route_points: Mapped[List["RoutePoint"]] = relationship("RoutePoint", back_populates="route", cascade="all, delete-orphan", order_by="RoutePoint.sequence")
    user_assignments: Mapped[List["UserAssignment"]] = relationship("UserAssignment", back_populates="route")

class RoutePoint(Base):
    __tablename__ = "route_points"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("bus_routes.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    route: Mapped["BusRoute"] = relationship("BusRoute", back_populates="route_points")

    __table_args__ = (
        Index("idx_route_sequence", "route_id", "sequence"),
    )

class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vehicle_code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    license_plate: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), default="Standard Transit Bus")
    status: Mapped[str] = mapped_column(String(50), default="ONLINE")

    assigned_route_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bus_routes.id", ondelete="SET NULL"), nullable=True)

    last_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    route: Mapped[Optional["BusRoute"]] = relationship("BusRoute", back_populates="vehicles")
    assigned_users: Mapped[List["User"]] = relationship("User", back_populates="assigned_vehicle")
    user_assignments: Mapped[List["UserAssignment"]] = relationship("UserAssignment", back_populates="vehicle")
    telemetry_logs: Mapped[List["GPSTelemetry"]] = relationship("GPSTelemetry", back_populates="vehicle", cascade="all, delete-orphan")

class UserAssignment(Base):
    __tablename__ = "user_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("bus_routes.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="assignments")
    route: Mapped["BusRoute"] = relationship("BusRoute", back_populates="user_assignments")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="user_assignments")

    __table_args__ = (
        Index("idx_user_active_assignment", "user_id", "is_active"),
    )

class GPSTelemetry(Base):
    __tablename__ = "gps_telemetry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    speed: Mapped[float] = mapped_column(Float, default=0.0)
    heading: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="REST")

    @property
    def speed_kmh(self) -> float:
        return self.speed

    @speed_kmh.setter
    def speed_kmh(self, value: float):
        self.speed = value

    @property
    def timestamp(self) -> datetime:
        return self.recorded_at

    @timestamp.setter
    def timestamp(self, value: datetime):
        self.recorded_at = value

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="telemetry_logs")

    __table_args__ = (
        Index("idx_vehicle_history", "vehicle_id", "recorded_at"),
    )
