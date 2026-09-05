import json
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.database import get_db
from app.models.models import User, BusRoute
from app.schemas.schemas import BusRouteResponse, Waypoint

router = APIRouter()

@router.get("", response_model=List[BusRouteResponse])
def get_all_routes(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve bus routes. Standard users only see their assigned route.
    Admin users see all routes.
    """
    if current_user.role == "admin":
        routes = db.query(BusRoute).all()
    else:
        if not current_user.assigned_route_id:
            return []
        routes = db.query(BusRoute).filter(BusRoute.id == current_user.assigned_route_id).all()
    
    result = []
    for r in routes:
        waypoints_data = []
        if r.waypoints_json:
            try:
                raw = json.loads(r.waypoints_json)
                waypoints_data = [Waypoint(**wp) for wp in raw]
            except Exception:
                waypoints_data = []
        
        result.append(
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
    return result

@router.get("/{route_id}", response_model=BusRouteResponse)
def get_route_by_id(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve specific route by ID.
    Strictly enforces authorization: non-admin user gets 403 Forbidden if ID != assigned_route_id.
    """
    deps.verify_user_route_access(current_user, route_id)

    route = db.query(BusRoute).filter(BusRoute.id == route_id).first()
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found."
        )

    waypoints_data = []
    if route.waypoints_json:
        try:
            raw = json.loads(route.waypoints_json)
            waypoints_data = [Waypoint(**wp) for wp in raw]
        except Exception:
            waypoints_data = []

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
