from typing import Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import verify_gps_ingest_auth
from app.services.tracking_service import TrackingService
from app.schemas.schemas import GPSIngestPayload, GPSTelemetryCreate, GPSTelemetryResponse

router = APIRouter()

@router.post("", response_model=GPSTelemetryResponse, status_code=status.HTTP_201_CREATED)
def record_gps_telemetry(
    payload: GPSIngestPayload,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_gps_ingest_auth)
) -> Any:
    """
    POST /api/v1/gps
    Ingest GPS telemetry over REST API.
    Payload:
    {
      "vehicle_code": "BUS-001",
      "latitude": 12.9716,
      "longitude": 77.5946,
      "speed": 38.5,
      "timestamp": "2026-09-05T10:30:00Z"
    }
    Validates vehicle, coordinate bounds (-90 to 90, -180 to 180, speed >= 0),
    handles out-of-order timestamps, maintains history & latest position cache,
    enforces device API key / JWT security.
    """
    tracking_service = TrackingService(db)
    return tracking_service.ingest_telemetry(
        latitude=payload.latitude,
        longitude=payload.longitude,
        speed_kmh=payload.effective_speed,
        heading=payload.heading or 0.0,
        vehicle_code=payload.vehicle_code,
        vehicle_id=payload.vehicle_id,
        timestamp=payload.timestamp,
        source=payload.source
    )

@router.post("/telemetry", response_model=GPSTelemetryResponse, status_code=status.HTTP_201_CREATED)
def record_telemetry_legacy(
    telemetry_in: GPSTelemetryCreate,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_gps_ingest_auth)
) -> Any:
    """
    POST /api/v1/gps/telemetry
    Legacy REST GPS Telemetry Ingestion endpoint.
    """
    tracking_service = TrackingService(db)
    return tracking_service.ingest_telemetry(
        latitude=telemetry_in.latitude,
        longitude=telemetry_in.longitude,
        speed_kmh=telemetry_in.speed_kmh,
        heading=telemetry_in.heading or 0.0,
        vehicle_code=telemetry_in.vehicle_code,
        vehicle_id=telemetry_in.vehicle_id,
        timestamp=telemetry_in.timestamp,
        source=telemetry_in.source
    )

