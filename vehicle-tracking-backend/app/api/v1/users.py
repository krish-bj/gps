import json
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.models.models import User, BusRoute, Vehicle, GPSTelemetry
from app.schemas.schemas import (
    UserResponse, UserAssignedRouteResponse, BusRouteResponse,
    VehicleResponse, GPSTelemetryResponse, Waypoint
)

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get profile of currently logged-in user.
    """
    return current_user

@router.get("/me/assigned-route", response_model=UserAssignedRouteResponse)
def get_user_assigned_route(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get the logged-in user's assigned route, waypoints, assigned vehicle, and latest location.
    Enforces that users strictly receive their own assigned route and vehicle details.
    """
    if not current_user.assigned_route_id or not current_user.assigned_vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No route or vehicle assigned to this user account."
        )

    # Fetch assigned route
    route = db.query(BusRoute).filter(BusRoute.id == current_user.assigned_route_id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned route not found."
        )

    waypoints_data = []
    if route.waypoints_json:
        try:
            raw_waypoints = json.loads(route.waypoints_json)
            waypoints_data = [Waypoint(**wp) for wp in raw_waypoints]
        except Exception:
            waypoints_data = []

    route_response = BusRouteResponse(
        id=route.id,
        route_code=route.route_code,
        route_name=route.route_name,
        description=route.description,
        start_location=route.start_location,
        end_location=route.end_location,
        waypoints=waypoints_data,
        created_at=route.created_at
    )

    # Fetch assigned vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == current_user.assigned_vehicle_id).first()
    vehicle_response = None
    latest_telemetry_response = None

    if vehicle:
        vehicle_response = VehicleResponse.model_validate(vehicle)

        latest_telemetry = db.query(GPSTelemetry)\
            .filter(GPSTelemetry.vehicle_id == vehicle.id)\
            .order_by(GPSTelemetry.timestamp.desc())\
            .first()
        
        if latest_telemetry:
            latest_telemetry_response = GPSTelemetryResponse.model_validate(latest_telemetry)

    return UserAssignedRouteResponse(
        user=UserResponse.model_validate(current_user),
        assigned_route=route_response,
        assigned_vehicle=vehicle_response,
        latest_telemetry=latest_telemetry_response
    )

@router.get("", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve users list (Admin access only).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users
