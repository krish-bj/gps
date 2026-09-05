from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.models import User
from app.services.tracking_service import TrackingService
from app.schemas.schemas import VehicleResponse, GPSTelemetryResponse

router = APIRouter()

@router.get("", response_model=List[VehicleResponse])
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    GET /api/v1/vehicles
    Returns assigned vehicle for regular user; all vehicles for admin.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_accessible_vehicles(current_user)

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_by_id(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    GET /api/v1/vehicles/{vehicle_id}
    Returns vehicle metadata. Enforces authorization check.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_vehicle_by_id(current_user, vehicle_id)

@router.get("/{vehicle_id}/location/latest", response_model=GPSTelemetryResponse)
def get_latest_vehicle_location(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    GET /api/v1/vehicles/{vehicle_id}/location/latest
    Returns latest GPS location for vehicle. Enforces authorization check.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_latest_vehicle_location(current_user, vehicle_id)

@router.get("/{vehicle_id}/location/history", response_model=List[GPSTelemetryResponse])
def get_vehicle_location_history(
    vehicle_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    GET /api/v1/vehicles/{vehicle_id}/location/history
    Returns historical GPS logs for vehicle. Enforces authorization check.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_vehicle_location_history(current_user, vehicle_id, limit=limit)

