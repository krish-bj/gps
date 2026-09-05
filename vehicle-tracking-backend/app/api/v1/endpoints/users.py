from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.models import User
from app.services.tracking_service import TrackingService
from app.services.assignment_service import AssignmentService
from app.repositories.user_repository import UserRepository
from app.repositories.route_repository import RouteRepository
from app.schemas.schemas import UserResponse, BusRouteResponse, VehicleResponse, UserAssignedRouteResponse, Waypoint
from app.schemas.route_point import RoutePointResponse
from app.utils.helpers import parse_json_waypoints

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    GET /api/v1/users/me
    Return authenticated user's safe profile.
    Never exposes password hash.
    Denied for inactive accounts.
    """
    return current_user

@router.get("/me/route", response_model=BusRouteResponse)
def get_user_assigned_route_only(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    GET /api/v1/users/me/route
    Returns only the route assigned to the authenticated user.
    """
    assignment_service = AssignmentService(db)
    assigned_details = assignment_service.get_user_assigned_details(current_user)
    route_db = RouteRepository(db).get_by_id(assigned_details["route"].id)
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

@router.get("/me/vehicle", response_model=VehicleResponse)
def get_user_assigned_vehicle_only(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    GET /api/v1/users/me/vehicle
    Returns only the authenticated user's assigned vehicle.
    """
    assignment_service = AssignmentService(db)
    assigned_details = assignment_service.get_user_assigned_details(current_user)
    return VehicleResponse.model_validate(assigned_details["vehicle"])

@router.get("/me/assigned-route", response_model=UserAssignedRouteResponse)
def get_user_assigned_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    tracking_service = TrackingService(db)
    return tracking_service.get_assigned_route_for_user(current_user)

@router.get("", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin),
) -> Any:
    user_repo = UserRepository(db)
    return user_repo.get_all(skip=skip, limit=limit)

