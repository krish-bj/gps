from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class RoutePointBase(BaseModel):
    sequence: int = Field(default=1, ge=1, description="Stop sequence order in travel direction")
    latitude: float = Field(..., description="Latitude coordinate (-90 to 90)")
    longitude: float = Field(..., description="Longitude coordinate (-180 to 180)")
    name: Optional[str] = Field(default=None, description="Optional stop/point label")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("Latitude coordinate must be between -90.0 and 90.0 degrees.")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("Longitude coordinate must be between -180.0 and 180.0 degrees.")
        return v

class RoutePointCreate(RoutePointBase):
    route_id: int

class RoutePointResponse(RoutePointBase):
    id: int
    route_id: int

    model_config = ConfigDict(from_attributes=True)
