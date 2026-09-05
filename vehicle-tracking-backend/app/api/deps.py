from app.api.dependencies import (
    get_current_user,
    get_current_admin as get_current_active_admin,
    oauth2_scheme
)
from app.services.tracking_service import TrackingService

def verify_user_vehicle_access(user, vehicle_id: int):
    # Delegate scope check to TrackingService rules
    if user.role != "admin" and user.assigned_vehicle_id != vehicle_id:
        from app.exceptions.custom_exceptions import ForbiddenAccessException
        raise ForbiddenAccessException(f"User '{user.email}' is forbidden from accessing vehicle ID {vehicle_id}.")

def verify_user_route_access(user, route_id: int):
    if user.role != "admin" and user.assigned_route_id != route_id:
        from app.exceptions.custom_exceptions import ForbiddenAccessException
        raise ForbiddenAccessException(f"User '{user.email}' is forbidden from accessing route ID {route_id}.")
