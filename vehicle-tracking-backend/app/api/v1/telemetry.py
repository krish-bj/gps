from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Vehicle, GPSTelemetry
from app.schemas.schemas import GPSTelemetryCreate, GPSTelemetryResponse

router = APIRouter()

@router.post("", response_model=GPSTelemetryResponse, status_code=status.HTTP_201_CREATED)
def record_telemetry(
    telemetry_in: GPSTelemetryCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Ingest GPS telemetry data for a vehicle (REST API endpoint).
    """
    vehicle = None
    if telemetry_in.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == telemetry_in.vehicle_id).first()
    elif telemetry_in.vehicle_code:
        vehicle = db.query(Vehicle).filter(Vehicle.vehicle_code == telemetry_in.vehicle_code).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found. Provide a valid vehicle_id or vehicle_code."
        )

    log_timestamp = telemetry_in.timestamp or datetime.now(timezone.utc)

    # Create telemetry log
    telemetry = GPSTelemetry(
        vehicle_id=vehicle.id,
        latitude=telemetry_in.latitude,
        longitude=telemetry_in.longitude,
        speed_kmh=telemetry_in.speed_kmh,
        heading=telemetry_in.heading or 0.0,
        timestamp=log_timestamp
    )
    db.add(telemetry)

    # Update cached latest position on vehicle
    vehicle.last_latitude = telemetry_in.latitude
    vehicle.last_longitude = telemetry_in.longitude
    vehicle.last_speed = telemetry_in.speed_kmh
    vehicle.last_timestamp = log_timestamp
    vehicle.status = "MOVING" if telemetry_in.speed_kmh > 0 else "IDLE"

    db.commit()
    db.refresh(telemetry)

    return telemetry
