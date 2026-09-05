from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user

def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required"
        )
    return current_user

def verify_user_vehicle_access(user: User, vehicle_id: int):
    """
    Enforce backend user-to-vehicle authorization.
    Regular users can ONLY access details/telemetry of their assigned vehicle.
    Raises HTTP 403 Forbidden if unauthorized.
    """
    if user.role != "admin" and user.assigned_vehicle_id != vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Authorization Error: User '{user.email}' is forbidden from accessing vehicle ID {vehicle_id}."
        )

def verify_user_route_access(user: User, route_id: int):
    """
    Enforce backend user-to-route authorization.
    Regular users can ONLY access details of their assigned route.
    Raises HTTP 403 Forbidden if unauthorized.
    """
    if user.role != "admin" and user.assigned_route_id != route_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Authorization Error: User '{user.email}' is forbidden from accessing route ID {route_id}."
        )
