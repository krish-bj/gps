from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.models import User
from app.services.tracking_service import TrackingService
from app.schemas.schemas import BusRouteResponse

router = APIRouter()

@router.get("", response_model=List[BusRouteResponse])
def get_all_routes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    GET /api/v1/routes
    Returns assigned route for regular user; all routes for admin.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_accessible_routes(current_user)

@router.get("/{route_id}", response_model=BusRouteResponse)
def get_route_by_id(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    GET /api/v1/routes/{route_id}
    Returns route details. Enforces authorization check.
    """
    tracking_service = TrackingService(db)
    return tracking_service.get_route_by_id(current_user, route_id)

