from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import User, BusRoute, Vehicle, UserAssignment
from app.repositories.user_repository import UserRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.exceptions.custom_exceptions import EntityNotFoundException, ForbiddenAccessException

class AssignmentService:
    """
    Reusable Assignment & Authorization Service.
    Acts as the single source of truth for user active assignments, routes, and vehicles.
    Enforces authorization logic for tracking APIs and ensures client-supplied
    vehicle_id, route_id, or user_id parameters are never trusted directly.
    """
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.route_repo = RouteRepository(db)
        self.vehicle_repo = VehicleRepository(db)

    def get_active_assignment(self, user: User) -> Optional[UserAssignment]:
        """
        Retrieves the active UserAssignment record for the given user.
        """
        return self.db.query(UserAssignment).filter(
            UserAssignment.user_id == user.id,
            UserAssignment.is_active == True
        ).first()

    def get_user_assigned_details(self, user: User) -> Dict[str, Any]:
        """
        Determines the authenticated user's active assignment, route, and vehicle.
        This service is the source of truth for protected tracking APIs.
        """
        assignment = self.get_active_assignment(user)
        
        route_id = assignment.route_id if assignment else user.assigned_route_id
        vehicle_id = assignment.vehicle_id if assignment else user.assigned_vehicle_id

        if not route_id or not vehicle_id:
            raise ForbiddenAccessException("User has no active route or vehicle assignment.")

        route = self.route_repo.get_by_id(route_id)
        if not route:
            raise EntityNotFoundException("BusRoute", route_id)

        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise EntityNotFoundException("Vehicle", vehicle_id)

        return {
            "assignment": assignment,
            "route": route,
            "vehicle": vehicle,
            "route_id": route_id,
            "vehicle_id": vehicle_id
        }

    def verify_vehicle_access(self, user: User, target_vehicle_id: int) -> Vehicle:
        """
        Verifies that the authenticated user is authorized to access target_vehicle_id.
        Admins are permitted to access any vehicle.
        Standard users are strictly restricted to their assigned vehicle.
        Do NOT trust vehicle_id coming from client requests.
        """
        if user.role == "admin":
            vehicle = self.vehicle_repo.get_by_id(target_vehicle_id)
            if not vehicle:
                raise EntityNotFoundException("Vehicle", target_vehicle_id)
            return vehicle

        assigned_details = self.get_user_assigned_details(user)
        if assigned_details["vehicle_id"] != target_vehicle_id:
            raise ForbiddenAccessException(
                f"Access forbidden: User '{user.email}' is not authorized to access vehicle ID {target_vehicle_id}."
            )
        return assigned_details["vehicle"]

    def verify_route_access(self, user: User, target_route_id: int) -> BusRoute:
        """
        Verifies that the authenticated user is authorized to access target_route_id.
        Admins are permitted to access any route.
        Standard users are strictly restricted to their assigned route.
        Do NOT trust route_id coming from client requests.
        """
        if user.role == "admin":
            route = self.route_repo.get_by_id(target_route_id)
            if not route:
                raise EntityNotFoundException("BusRoute", target_route_id)
            return route

        assigned_details = self.get_user_assigned_details(user)
        if assigned_details["route_id"] != target_route_id:
            raise ForbiddenAccessException(
                f"Access forbidden: User '{user.email}' is not authorized to access route ID {target_route_id}."
            )
        return assigned_details["route"]
