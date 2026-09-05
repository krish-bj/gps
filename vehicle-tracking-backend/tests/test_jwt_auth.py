from datetime import timedelta
import pytest
import jwt
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, decode_access_token
)

def test_password_hashing_and_verification():
    raw_pass = "superSecretPassword123!"
    hashed = get_password_hash(raw_pass)
    
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("wrongPass", hashed) is False

def test_create_and_decode_access_token():
    token = create_access_token(subject=100, expires_delta=timedelta(minutes=15))
    payload = decode_access_token(token)
    
    assert payload["sub"] == "100"
    assert "iat" in payload
    assert "exp" in payload
    assert payload["exp"] > payload["iat"]

def test_expired_access_token_raises_error():
    # Expired token (1 second in the past)
    expired_token = create_access_token(subject=100, expires_delta=timedelta(seconds=-1))
    
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token)
