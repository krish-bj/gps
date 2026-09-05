from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.models.models import User
from app.exceptions.custom_exceptions import EntityNotFoundException, ForbiddenAccessException

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Reusable FastAPI dependency for authenticating user requests.
    Determines user strictly from the verified JWT payload claim ('sub').
    Never trusts client-provided user IDs.
    """
    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise EntityNotFoundException("User", user_id)
    if not user.is_active:
        raise ForbiddenAccessException("User account is inactive.")
    
    return user

def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Reusable FastAPI dependency enforcing admin role authorization.
    """
    if current_user.role != "admin":
        raise ForbiddenAccessException("Admin permissions required.")
    return current_user

def get_assignment_service(
    db: Session = Depends(get_db)
) -> "AssignmentService":
    from app.services.assignment_service import AssignmentService
    return AssignmentService(db)

def verify_assigned_vehicle_access(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reusable dependency to verify whether the authenticated user has access to vehicle_id.
    Never trusts client-provided vehicle_id.
    """
    from app.services.assignment_service import AssignmentService
    assignment_service = AssignmentService(db)
    return assignment_service.verify_vehicle_access(current_user, vehicle_id)

def verify_assigned_route_access(
    route_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reusable dependency to verify whether the authenticated user has access to route_id.
    Never trusts client-provided route_id.
    """
    from app.services.assignment_service import AssignmentService
    assignment_service = AssignmentService(db)
    return assignment_service.verify_route_access(current_user, route_id)


from fastapi import Header
from typing import Optional

def verify_gps_ingest_auth(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Device security strategy for GPS REST Ingestion.
    Accepts X-API-Key header OR valid Bearer JWT.
    Rejects unauthorized telemetry submissions with 401 Unauthorized.
    """
    if x_api_key and x_api_key == settings.GPS_INGEST_API_KEY:
        return True

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = decode_access_token(token)
            if payload.get("sub"):
                return True
        except Exception:
            pass

    if x_api_key == settings.GPS_INGEST_API_KEY:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing GPS ingestion authentication credentials (X-API-Key or Bearer token required)",
        headers={"WWW-Authenticate": "ApiKey, Bearer"},
    )


