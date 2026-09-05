from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.models import User
from app.services.tracking_service import TrackingService
from app.repositories.route_repository import RouteRepository
from app.schemas.schemas import BusRouteResponse, Waypoint
from app.utils.helpers import parse_json_waypoints

router = APIRouter()

@router.get("", response_model=List[BusRouteResponse])
def get_all_routes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    route_repo = RouteRepository(db)
    if current_user.role == "admin":
        routes = route_repo.get_all()
    else:
        if not current_user.assigned_route_id:
            return []
        assigned = route_repo.get_by_id(current_user.assigned_route_id)
        routes = [assigned] if assigned else []
    
    res = []
    for r in routes:
        waypoints_data = [Waypoint(**wp) for wp in parse_json_waypoints(r.waypoints_json)]
        res.append(
            BusRouteResponse(
                id=r.id,
                route_code=r.route_code,
                route_name=r.route_name,
                description=r.description,
                start_location=r.start_location,
                end_location=r.end_location,
                waypoints=waypoints_data,
                created_at=r.created_at
            )
        )
    return res

@router.get("/{route_id}", response_model=BusRouteResponse)
def get_route_by_id(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    tracking_service = TrackingService(db)
    tracking_service.verify_route_access(current_user, route_id)
    
    route_repo = RouteRepository(db)
    route = route_repo.get_by_id(route_id)
    waypoints_data = [Waypoint(**wp) for wp in parse_json_waypoints(route.waypoints_json)]
    
    return BusRouteResponse(
        id=route.id,
        route_code=route.route_code,
        route_name=route.route_name,
        description=route.description,
        start_location=route.start_location,
        end_location=route.end_location,
        waypoints=waypoints_data,
        created_at=route.created_at
    )
