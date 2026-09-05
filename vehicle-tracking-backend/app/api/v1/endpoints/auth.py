from typing import Any, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.schemas import Token, UserLogin
from app.exceptions.custom_exceptions import InvalidCredentialsException

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    POST /api/v1/auth/login
    Accepts JSON body: {"email": "user@example.com", "password": "password"}
    or Form Data (OAuth2): username=user@example.com&password=password
    """
    email = None
    password = None

    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
    else:
        try:
            body = await request.json()
            if isinstance(body, dict):
                email = body.get("email") or body.get("username")
                password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        raise InvalidCredentialsException("Email and password are required.")

    auth_service = AuthService(db)
    return auth_service.authenticate_user(email=str(email), password=str(password))


@router.post("/login/json", response_model=Token)
def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    auth_service = AuthService(db)
    return auth_service.authenticate_user(login_data.email, login_data.password)

