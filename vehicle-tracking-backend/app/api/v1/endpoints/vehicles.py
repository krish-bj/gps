from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.models import User
from app.services.tracking_service import TrackingService
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.schemas import VehicleResponse, GPSTelemetryResponse

router = APIRouter()

@router.get("", response_model=List[VehicleResponse])
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    v_repo = VehicleRepository(db)
    if current_user.role == "admin":
        return v_repo.get_all()
    else:
        if not current_user.assigned_vehicle_id:
            return []
        v = v_repo.get_by_id(current_user.assigned_vehicle_id)
        return [v] if v else []

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_by_id(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    tracking_service = TrackingService(db)
    tracking_service.verify_vehicle_access(current_user, vehicle_id)
    v_repo = VehicleRepository(db)
    return v_repo.get_by_id(vehicle_id)

@router.get("/{vehicle_id}/location/latest", response_model=GPSTelemetryResponse)
def get_latest_vehicle_location(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    tracking_service = TrackingService(db)
    return tracking_service.get_latest_vehicle_location(current_user, vehicle_id)

@router.get("/{vehicle_id}/location/history", response_model=List[GPSTelemetryResponse])
def get_vehicle_location_history(
    vehicle_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    tracking_service = TrackingService(db)
    return tracking_service.get_vehicle_location_history(current_user, vehicle_id, limit=limit)
