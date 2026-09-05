from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.models import User, BusRoute, Vehicle, GPSTelemetry
from app.repositories.user_repository import UserRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.exceptions.custom_exceptions import EntityNotFoundException, ForbiddenAccessException
from app.utils.helpers import parse_json_waypoints
from app.schemas.schemas import (
    UserResponse, BusRouteResponse, VehicleResponse,
    GPSTelemetryResponse, UserAssignedRouteResponse, Waypoint
)

class TrackingService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.route_repo = RouteRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.telemetry_repo = TelemetryRepository(db)

    def get_assigned_route_for_user(self, user: User) -> UserAssignedRouteResponse:
        if not user.assigned_route_id or not user.assigned_vehicle_id:
            raise EntityNotFoundException("Assigned Route/Vehicle", "user_me")

        route = self.route_repo.get_by_id(user.assigned_route_id)
        if not route:
            raise EntityNotFoundException("BusRoute", user.assigned_route_id)

        waypoints_list = [Waypoint(**wp) for wp in parse_json_waypoints(route.waypoints_json)]
        route_resp = BusRouteResponse(
            id=route.id,
            route_code=route.route_code,
            route_name=route.route_name,
            description=route.description,
            start_location=route.start_location,
            end_location=route.end_location,
            waypoints=waypoints_list,
            created_at=route.created_at
        )

        vehicle = self.vehicle_repo.get_by_id(user.assigned_vehicle_id)
        vehicle_resp = VehicleResponse.model_validate(vehicle) if vehicle else None

        latest_telemetry = self.telemetry_repo.get_latest_by_vehicle_id(vehicle.id) if vehicle else None
        latest_resp = GPSTelemetryResponse.model_validate(latest_telemetry) if latest_telemetry else None

        return UserAssignedRouteResponse(
            user=UserResponse.model_validate(user),
            assigned_route=route_resp,
            assigned_vehicle=vehicle_resp,
            latest_telemetry=latest_resp
        )

    def verify_vehicle_access(self, user: User, vehicle_id: int):
        if user.role != "admin" and user.assigned_vehicle_id != vehicle_id:
            raise ForbiddenAccessException(f"User '{user.email}' is forbidden from accessing vehicle ID {vehicle_id}.")

    def verify_route_access(self, user: User, route_id: int):
        if user.role != "admin" and user.assigned_route_id != route_id:
            raise ForbiddenAccessException(f"User '{user.email}' is forbidden from accessing route ID {route_id}.")

    def get_latest_vehicle_location(self, user: User, vehicle_id: int) -> GPSTelemetryResponse:
        self.verify_vehicle_access(user, vehicle_id)
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise EntityNotFoundException("Vehicle", vehicle_id)

        latest = self.telemetry_repo.get_latest_by_vehicle_id(vehicle_id)
        if not latest:
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
            raise EntityNotFoundException("GPSTelemetry", f"vehicle_{vehicle_id}")

        return GPSTelemetryResponse.model_validate(latest)

    def get_vehicle_location_history(self, user: User, vehicle_id: int, limit: int = 100) -> List[GPSTelemetryResponse]:
        self.verify_vehicle_access(user, vehicle_id)
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise EntityNotFoundException("Vehicle", vehicle_id)

        history = self.telemetry_repo.get_history_by_vehicle_id(vehicle_id, limit=limit)
        return [GPSTelemetryResponse.model_validate(log) for log in history]

    def ingest_telemetry(self, latitude: float, longitude: float, speed_kmh: float, heading: float, vehicle_code: Optional[str] = None, vehicle_id: Optional[int] = None, timestamp: Optional[datetime] = None) -> GPSTelemetryResponse:
        vehicle = None
        if vehicle_id:
            vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        elif vehicle_code:
            vehicle = self.vehicle_repo.get_by_code(vehicle_code)

        if not vehicle:
            raise EntityNotFoundException("Vehicle", vehicle_code or vehicle_id or "unknown")

        log_ts = timestamp or datetime.now(timezone.utc)
        telemetry = self.telemetry_repo.create(
            vehicle_id=vehicle.id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            heading=heading,
            timestamp=log_ts
        )

        vehicle.last_latitude = latitude
        vehicle.last_longitude = longitude
        vehicle.last_speed = speed_kmh
        vehicle.last_timestamp = log_ts
        vehicle.status = "MOVING" if speed_kmh > 0 else "IDLE"

        self.db.commit()
        self.db.refresh(telemetry)

        return GPSTelemetryResponse.model_validate(telemetry)
