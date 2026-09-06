import logging
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

logger = logging.getLogger("tracking_service")

from app.models.models import User, BusRoute, Vehicle, GPSTelemetry
from app.repositories.user_repository import UserRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.exceptions.custom_exceptions import EntityNotFoundException, ForbiddenAccessException
from app.utils.helpers import parse_json_waypoints
from app.schemas.schemas import (
    UserResponse, BusRouteResponse, VehicleResponse,
    GPSTelemetryResponse, UserAssignedRouteResponse, Waypoint,
    TrackingSummaryResponse, TrackingSummaryStatus, CurrentLocationResponse,
    compute_vehicle_status
)
from app.schemas.route_point import RoutePointResponse

from app.services.assignment_service import AssignmentService

class TrackingService:
    def __init__(self, db: Session):
        self.db = db
        self.assignment_service = AssignmentService(db)
        self.user_repo = UserRepository(db)
        self.route_repo = RouteRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.telemetry_repo = TelemetryRepository(db)

    def _format_bus_route_response(self, route: BusRoute) -> BusRouteResponse:
        waypoints_list = [Waypoint(**wp) for wp in parse_json_waypoints(route.waypoints_json)]
        route_points_list = [RoutePointResponse.model_validate(rp) for rp in route.route_points] if hasattr(route, "route_points") and route.route_points else []
        return BusRouteResponse(
            id=route.id,
            route_code=route.route_code,
            route_name=route.route_name,
            description=route.description,
            start_location=route.start_location,
            end_location=route.end_location,
            waypoints=waypoints_list,
            route_points=route_points_list,
            created_at=route.created_at
        )

    def get_my_assigned_route(self, user: User) -> BusRouteResponse:
        details = self.assignment_service.get_user_assigned_details(user)
        route_db = self.route_repo.get_by_id(details["route"].id)
        return self._format_bus_route_response(route_db)

    def get_my_assigned_vehicle(self, user: User) -> VehicleResponse:
        details = self.assignment_service.get_user_assigned_details(user)
        return VehicleResponse.model_validate(details["vehicle"])

    def get_accessible_routes(self, user: User) -> List[BusRouteResponse]:
        if user.role == "admin":
            routes = self.route_repo.get_all()
        else:
            try:
                details = self.assignment_service.get_user_assigned_details(user)
                route_db = self.route_repo.get_by_id(details["route"].id)
                routes = [route_db] if route_db else []
            except ForbiddenAccessException:
                routes = []
        return [self._format_bus_route_response(r) for r in routes]

    def get_route_by_id(self, user: User, route_id: int) -> BusRouteResponse:
        route = self.verify_route_access(user, route_id)
        route_db = self.route_repo.get_by_id(route.id)
        return self._format_bus_route_response(route_db)

    def get_accessible_vehicles(self, user: User) -> List[VehicleResponse]:
        if user.role == "admin":
            vehicles = self.vehicle_repo.get_all()
        else:
            try:
                details = self.assignment_service.get_user_assigned_details(user)
                vehicles = [details["vehicle"]]
            except ForbiddenAccessException:
                vehicles = []
        return [VehicleResponse.model_validate(v) for v in vehicles]

    def get_vehicle_by_id(self, user: User, vehicle_id: int) -> VehicleResponse:
        vehicle = self.verify_vehicle_access(user, vehicle_id)
        return VehicleResponse.model_validate(vehicle)


    def get_my_current_location(self, user: User) -> CurrentLocationResponse:
        details = self.assignment_service.get_user_assigned_details(user)
        vehicle = details["vehicle"]

        latest = self.telemetry_repo.get_latest_by_vehicle_id(vehicle.id)
        if latest:
            derived_status = compute_vehicle_status(latest.recorded_at)
            return CurrentLocationResponse(
                vehicle_code=vehicle.vehicle_code,
                latitude=latest.latitude,
                longitude=latest.longitude,
                speed=latest.speed,
                heading=latest.heading or 0.0,
                recorded_at=latest.recorded_at,
                received_at=latest.received_at,
                status=derived_status
            )

        if vehicle.last_latitude is not None and vehicle.last_longitude is not None:
            derived_status = compute_vehicle_status(vehicle.last_timestamp)
            return CurrentLocationResponse(
                vehicle_code=vehicle.vehicle_code,
                latitude=vehicle.last_latitude,
                longitude=vehicle.last_longitude,
                speed=vehicle.last_speed or 0.0,
                heading=0.0,
                recorded_at=vehicle.last_timestamp or vehicle.created_at,
                received_at=vehicle.last_timestamp or vehicle.created_at,
                status=derived_status
            )

        return CurrentLocationResponse(
            vehicle_code=vehicle.vehicle_code,
            latitude=None,
            longitude=None,
            speed=0.0,
            recorded_at=None,
            received_at=None,
            status="NO_DATA"
        )


    def get_tracking_summary_for_user(self, user: User) -> TrackingSummaryResponse:
        details = self.assignment_service.get_user_assigned_details(user)
        route = details["route"]
        vehicle = details["vehicle"]

        waypoints_list = [Waypoint(**wp) for wp in parse_json_waypoints(route.waypoints_json)]
        route_points_list = [RoutePointResponse.model_validate(rp) for rp in route.route_points] if hasattr(route, "route_points") and route.route_points else []

        route_resp = BusRouteResponse(
            id=route.id,
            route_code=route.route_code,
            route_name=route.route_name,
            description=route.description,
            start_location=route.start_location,
            end_location=route.end_location,
            waypoints=waypoints_list,
            route_points=route_points_list,
            created_at=route.created_at
        )

        vehicle_resp = VehicleResponse.model_validate(vehicle) if vehicle else None

        latest_telemetry = self.telemetry_repo.get_latest_by_vehicle_id(vehicle.id) if vehicle else None
        if latest_telemetry:
            latest_resp = GPSTelemetryResponse.model_validate(latest_telemetry)
        elif vehicle and vehicle.last_latitude is not None and vehicle.last_longitude is not None:
            latest_resp = GPSTelemetryResponse(
                id=0,
                vehicle_id=vehicle.id,
                latitude=vehicle.last_latitude,
                longitude=vehicle.last_longitude,
                speed_kmh=vehicle.last_speed or 0.0,
                heading=0.0,
                recorded_at=vehicle.last_timestamp or vehicle.created_at,
                received_at=vehicle.last_timestamp or vehicle.created_at,
                source="REST"
            )
        else:
            latest_resp = None

        derived_status = compute_vehicle_status(vehicle.last_timestamp) if vehicle else "NO_DATA"
        status_resp = TrackingSummaryStatus(
            vehicle_status=derived_status,
            is_active_assignment=True,
            last_updated=vehicle.last_timestamp or (vehicle.created_at if vehicle else None)
        )

        return TrackingSummaryResponse(
            route=route_resp,
            vehicle=vehicle_resp,
            latest_location=latest_resp,
            status=status_resp
        )

    def get_assigned_route_for_user(self, user: User) -> UserAssignedRouteResponse:

        details = self.assignment_service.get_user_assigned_details(user)
        route = details["route"]
        vehicle = details["vehicle"]

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
        return self.assignment_service.verify_vehicle_access(user, vehicle_id)

    def verify_route_access(self, user: User, route_id: int):
        return self.assignment_service.verify_route_access(user, route_id)


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
                    recorded_at=vehicle.last_timestamp or vehicle.created_at,
                    received_at=vehicle.last_timestamp or vehicle.created_at,
                    source="REST"
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

    def get_my_vehicle_history(
        self,
        user: User,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[GPSTelemetryResponse]:
        details = self.assignment_service.get_user_assigned_details(user)
        vehicle = details["vehicle"]

        if from_time and to_time and from_time > to_time:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="'from' timestamp must be before or equal to 'to' timestamp."
            )

        sane_limit = min(max(1, limit), 1000)
        history = self.telemetry_repo.get_filtered_history(
            vehicle_id=vehicle.id,
            from_time=from_time,
            to_time=to_time,
            limit=sane_limit
        )
        return [GPSTelemetryResponse.model_validate(log) for log in history]

    def ingest_telemetry(
        self,
        latitude: float,
        longitude: float,
        speed_kmh: float,
        heading: float,
        vehicle_code: Optional[str] = None,
        vehicle_id: Optional[int] = None,
        timestamp: Optional[datetime] = None,
        source: str = "REST"
    ) -> GPSTelemetryResponse:
        vehicle = None
        if vehicle_id:
            vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        elif vehicle_code:
            vehicle = self.vehicle_repo.get_by_code(vehicle_code)

        if not vehicle:
            logger.warning(f"GPS telemetry REJECTED (Source: {source}): Vehicle '{vehicle_code or vehicle_id}' not found.")
            raise EntityNotFoundException("Vehicle", vehicle_code or vehicle_id or "unknown")

        log_ts = timestamp or datetime.now(timezone.utc)
        if log_ts.tzinfo is None:
            log_ts = log_ts.replace(tzinfo=timezone.utc)

        try:
            telemetry = self.telemetry_repo.create(
                vehicle_id=vehicle.id,
                latitude=latitude,
                longitude=longitude,
                speed_kmh=speed_kmh,
                heading=heading,
                timestamp=log_ts,
                source=source
            )
            logger.info(f"GPS telemetry RECEIVED (Source: {source}, Vehicle: '{vehicle.vehicle_code}'): Lat: {latitude}, Lng: {longitude}, Speed: {speed_kmh} km/h")


            # Handle out-of-order timestamps: Only update cached latest vehicle coordinates
            # if incoming timestamp is newer than or equal to current last_timestamp.
            is_newer_or_equal = True
            if vehicle.last_timestamp is not None:
                last_ts = vehicle.last_timestamp if vehicle.last_timestamp.tzinfo else vehicle.last_timestamp.replace(tzinfo=timezone.utc)
                if log_ts < last_ts:
                    is_newer_or_equal = False

            if is_newer_or_equal:
                vehicle.last_latitude = latitude
                vehicle.last_longitude = longitude
                vehicle.last_speed = speed_kmh
                vehicle.last_timestamp = log_ts
                vehicle.status = compute_vehicle_status(log_ts)

            self.db.commit()
            self.db.refresh(telemetry)
            return GPSTelemetryResponse.model_validate(telemetry)
        except Exception as e:
            self.db.rollback()
            raise e
