from datetime import timedelta
from sqlalchemy.orm import Session
from app.core import security
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse
from app.exceptions.custom_exceptions import InvalidCredentialsException, ForbiddenAccessException

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def authenticate_user(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not security.verify_password(password, user.hashed_password):
            raise InvalidCredentialsException("Incorrect email or password.")
        if not user.is_active:
            raise ForbiddenAccessException("Inactive user account.")
        
        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expires_in_seconds,
            "user": UserResponse.model_validate(user)
        }

