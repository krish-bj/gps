from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.models import User
from app.services.tracking_service import TrackingService
from app.services.user_service import UserService
from app.schemas.schemas import UserResponse, BusRouteResponse, VehicleResponse, UserAssignedRouteResponse

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
    tracking_service = TrackingService(db)
    return tracking_service.get_my_assigned_route(current_user)

@router.get("/me/vehicle", response_model=VehicleResponse)
def get_user_assigned_vehicle_only(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    GET /api/v1/users/me/vehicle
    Returns only the authenticated user's assigned vehicle.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_my_assigned_vehicle(current_user)

@router.get("/me/assigned-route", response_model=UserAssignedRouteResponse)
def get_user_assigned_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    GET /api/v1/users/me/assigned-route
    Returns detailed user assignment record with route, vehicle, and telemetry.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_assigned_route_for_user(current_user)

@router.get("", response_model=List[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin),
) -> Any:
    """
    GET /api/v1/users
    Returns list of all users. Admin protected.
    """
    user_service = UserService(db)
    return user_service.get_all_users(skip=skip, limit=limit)
