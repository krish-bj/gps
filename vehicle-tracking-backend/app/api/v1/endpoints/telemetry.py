from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.tracking_service import TrackingService
from app.schemas.schemas import GPSTelemetryCreate, GPSTelemetryResponse

router = APIRouter()

@router.post("", response_model=GPSTelemetryResponse, status_code=status.HTTP_201_CREATED)
def record_telemetry(
    telemetry_in: GPSTelemetryCreate,
    db: Session = Depends(get_db)
) -> Any:
    tracking_service = TrackingService(db)
    return tracking_service.ingest_telemetry(
        latitude=telemetry_in.latitude,
        longitude=telemetry_in.longitude,
        speed_kmh=telemetry_in.speed_kmh,
        heading=telemetry_in.heading or 0.0,
        vehicle_code=telemetry_in.vehicle_code,
        vehicle_id=telemetry_in.vehicle_id,
        timestamp=telemetry_in.timestamp
    )
