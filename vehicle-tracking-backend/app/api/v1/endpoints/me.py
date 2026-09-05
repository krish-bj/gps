from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.models import User
from app.services.assignment_service import AssignmentService
from app.services.tracking_service import TrackingService
from app.schemas.schemas import UserResponse, BusRouteResponse, VehicleResponse, Waypoint, TrackingSummaryResponse, GPSTelemetryResponse, CurrentLocationResponse
from app.schemas.route_point import RoutePointResponse
from app.repositories.route_repository import RouteRepository
from app.utils.helpers import parse_json_waypoints

router = APIRouter()

@router.get("", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    GET /api/v1/me or GET /api/v1/users/me
    Return authenticated user's safe profile.
    Never exposes password hash.
    Denied for inactive accounts.
    """
    return current_user

@router.get("/route", response_model=BusRouteResponse)
def get_my_assigned_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    GET /api/v1/me/route
    Returns only the route assigned to the authenticated user.
    Includes route_points ordered by sequence.
    Determines user strictly from JWT. Does NOT accept arbitrary user_id.
    """
    assignment_service = AssignmentService(db)
    assigned_details = assignment_service.get_user_assigned_details(current_user)
    route = assigned_details["route"]

    route_repo = RouteRepository(db)
    route_db = route_repo.get_by_id(route.id)

    waypoints_list = [Waypoint(**wp) for wp in parse_json_waypoints(route_db.waypoints_json)]
    route_points_list = [RoutePointResponse.model_validate(rp) for rp in route_db.route_points]

    return BusRouteResponse(
        id=route_db.id,
        route_code=route_db.route_code,
        route_name=route_db.route_name,
        description=route_db.description,
        start_location=route_db.start_location,
        end_location=route_db.end_location,
        waypoints=waypoints_list,
        route_points=route_points_list,
        created_at=route_db.created_at
    )

@router.get("/vehicle", response_model=VehicleResponse)
def get_my_assigned_vehicle(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    GET /api/v1/me/vehicle
    Return only the authenticated user's assigned vehicle.
    Determines user strictly from JWT. User cannot retrieve another vehicle.
    """
    assignment_service = AssignmentService(db)
    assigned_details = assignment_service.get_user_assigned_details(current_user)
    vehicle = assigned_details["vehicle"]
    return VehicleResponse.model_validate(vehicle)

@router.get("/tracking", response_model=TrackingSummaryResponse)
def get_my_tracking_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    GET /api/v1/me/tracking
    Returns unified tracking summary for authenticated user:
    - route (with route_points)
    - vehicle
    - latest_location
    - status
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_tracking_summary_for_user(current_user)

@router.get("/tracking/current", response_model=CurrentLocationResponse)
def get_my_current_location(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    GET /api/v1/me/tracking/current
    Returns latest GPS location and dynamic status for the authenticated user's assigned vehicle.
    Gracefully handles vehicles that have never reported GPS data (status="NO_DATA").
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_my_current_location(current_user)

@router.get("/tracking/history", response_model=List[GPSTelemetryResponse])
def get_my_vehicle_history(
    from_time: Optional[datetime] = Query(None, alias="from", description="Filter start ISO timestamp"),
    to_time: Optional[datetime] = Query(None, alias="to", description="Filter end ISO timestamp"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return (1-1000)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    GET /api/v1/me/tracking/history
    Returns historical GPS data for the authenticated user's assigned vehicle.
    Supports 'from', 'to', and 'limit' filters.
    Strictly isolated to user's assigned vehicle.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_my_vehicle_history(
        user=current_user,
        from_time=from_time,
        to_time=to_time,
        limit=limit
    )
