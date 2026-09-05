from datetime import datetime, timedelta, timezone
from typing import Any, Union, Dict, Optional
import bcrypt
import jwt
from app.core.config import settings

def get_password_hash(password: str) -> str:
    """Hash plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def create_access_token(subject: Union[str, int], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token containing standard claims:
    sub = user ID
    iat = issued at timestamp (UTC)
    exp = expiration timestamp (UTC)
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token claims.
    Validates expiration and signature.
    Raises jwt.PyJWTError if expired or invalid.
    """
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    return payload
