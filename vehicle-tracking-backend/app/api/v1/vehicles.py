from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.models.models import User, Vehicle, GPSTelemetry
from app.schemas.schemas import VehicleResponse, GPSTelemetryResponse

router = APIRouter()

@router.get("", response_model=List[VehicleResponse])
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve vehicles list.
    Enforces authorization: regular users only get their assigned vehicle.
    """
    if current_user.role == "admin":
        vehicles = db.query(Vehicle).all()
    else:
        if not current_user.assigned_vehicle_id:
            return []
        vehicles = db.query(Vehicle).filter(Vehicle.id == current_user.assigned_vehicle_id).all()
    
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_by_id(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get vehicle details by ID. Enforces backend user authorization (returns 403 if unauthorized).
    """
    deps.verify_user_vehicle_access(current_user, vehicle_id)

    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found."
        )
    return vehicle

@router.get("/{vehicle_id}/location/latest", response_model=GPSTelemetryResponse)
def get_latest_vehicle_location(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get latest GPS location telemetry for a vehicle.
    Strictly enforces authorization: returns HTTP 403 Forbidden if current_user's assigned_vehicle_id != vehicle_id.
    """
    deps.verify_user_vehicle_access(current_user, vehicle_id)

    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found."
        )

    latest_log = db.query(GPSTelemetry)\
        .filter(GPSTelemetry.vehicle_id == vehicle_id)\
        .order_by(GPSTelemetry.timestamp.desc())\
        .first()

    if not latest_log:
        if vehicle.last_latitude is not None and vehicle.last_longitude is not None:
            return GPSTelemetryResponse(
                id=0,
                vehicle_id=vehicle.id,
                latitude=vehicle.last_latitude,
                longitude=vehicle.last_longitude,
                speed_kmh=vehicle.last_speed or 0.0,
                heading=0.0,
                timestamp=vehicle.last_timestamp or vehicle.created_at
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No GPS telemetry data recorded yet for this vehicle."
        )

    return latest_log

@router.get("/{vehicle_id}/location/history", response_model=List[GPSTelemetryResponse])
def get_vehicle_location_history(
    vehicle_id: int,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get historical GPS tracking points for a vehicle.
    Strictly enforces authorization: returns HTTP 403 Forbidden if current_user's assigned_vehicle_id != vehicle_id.
    """
    deps.verify_user_vehicle_access(current_user, vehicle_id)

    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found."
        )

    history = db.query(GPSTelemetry)\
        .filter(GPSTelemetry.vehicle_id == vehicle_id)\
        .order_by(GPSTelemetry.timestamp.desc())\
        .limit(limit)\
        .all()

    return history
