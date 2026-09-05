from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Waypoint Schema
class Waypoint(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None
    stop_order: Optional[int] = None

# Bus Route Schemas
class BusRouteBase(BaseModel):
    route_code: str
    route_name: str
    description: Optional[str] = None
    start_location: str
    end_location: str

class BusRouteResponse(BusRouteBase):
    id: int
    waypoints: List[Waypoint] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# GPS Telemetry Schemas
class GPSTelemetryCreate(BaseModel):
    vehicle_code: Optional[str] = None
    vehicle_id: Optional[int] = None
    latitude: float
    longitude: float
    speed_kmh: float = 0.0
    heading: Optional[float] = 0.0
    timestamp: Optional[datetime] = None

class GPSTelemetryResponse(BaseModel):
    id: int
    vehicle_id: int
    latitude: float
    longitude: float
    speed_kmh: float
    heading: Optional[float] = 0.0
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

# Vehicle Schemas
class VehicleBase(BaseModel):
    vehicle_code: str
    license_plate: str
    model_name: str = "Standard Transit Bus"
    status: str = "ONLINE"
    assigned_route_id: Optional[int] = None

class VehicleResponse(VehicleBase):
    id: int
    last_latitude: Optional[float] = None
    last_longitude: Optional[float] = None
    last_speed: Optional[float] = None
    last_timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "user"

class UserResponse(UserBase):
    id: int
    is_active: bool
    assigned_route_id: Optional[int] = None
    assigned_vehicle_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# Combined Assigned Route & Vehicle Schema for Mobile App
class UserAssignedRouteResponse(BaseModel):
    user: UserResponse
    assigned_route: Optional[BusRouteResponse] = None
    assigned_vehicle: Optional[VehicleResponse] = None
    latest_telemetry: Optional[GPSTelemetryResponse] = None

    model_config = ConfigDict(from_attributes=True)
