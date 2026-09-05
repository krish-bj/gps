from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.models import User
from app.services.assignment_service import AssignmentService
from app.schemas.schemas import UserResponse, BusRouteResponse, VehicleResponse, Waypoint
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
