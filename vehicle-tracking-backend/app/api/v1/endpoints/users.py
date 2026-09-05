from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user, get_current_admin
from app.models.models import User
from app.services.tracking_service import TrackingService
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserResponse, UserAssignedRouteResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    return current_user

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
