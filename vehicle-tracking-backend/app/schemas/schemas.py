from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, computed_field

from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.route_point import RoutePointBase, RoutePointResponse
from app.schemas.user_assignment import UserAssignmentResponse

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 604800
    user: Optional[UserResponse] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Waypoint Schema
class Waypoint(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
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
    route_points: List[RoutePointResponse] = []
    created_at: datetime

    @computed_field
    @property
    def name(self) -> str:
        return self.route_name

    model_config = ConfigDict(from_attributes=True)

# GPS Telemetry Schemas with coordinate & speed validations
class GPSTelemetryCreate(BaseModel):
    vehicle_code: Optional[str] = None
    vehicle_id: Optional[int] = None
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude from -90 to 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude from -180 to 180")
    speed_kmh: float = Field(default=0.0, ge=0.0, description="Speed in km/h (cannot be negative)")
    heading: Optional[float] = Field(default=0.0, ge=0.0, le=360.0)
    timestamp: Optional[datetime] = None
    source: str = "REST"

    @field_validator("speed_kmh")
    @classmethod
    def validate_speed(cls, v: float) -> float:
        if v < 0.0:
            raise ValueError("Speed cannot be negative.")
        return v

class GPSTelemetryResponse(BaseModel):
    id: int
    vehicle_id: int
    latitude: float
    longitude: float
    speed_kmh: float
    heading: Optional[float] = 0.0
    recorded_at: datetime
    received_at: datetime
    source: str = "REST"

    @property
    def timestamp(self) -> datetime:
        return self.recorded_at

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

    @computed_field
    @property
    def registration_number(self) -> str:
        return self.license_plate

    @computed_field
    @property
    def display_name(self) -> str:
        return self.model_name

    model_config = ConfigDict(from_attributes=True)


# Combined Assigned Route & Vehicle Schema for Mobile App
class UserAssignedRouteResponse(BaseModel):
    user: UserResponse
    assigned_route: Optional[BusRouteResponse] = None
    assigned_vehicle: Optional[VehicleResponse] = None
    latest_telemetry: Optional[GPSTelemetryResponse] = None

    model_config = ConfigDict(from_attributes=True)
