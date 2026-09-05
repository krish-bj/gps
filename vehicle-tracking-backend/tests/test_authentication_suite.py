"""
PHASE AC — Authentication Test Suite (Prompt AC1)
Automated test suite proving:
- Valid login (JSON and OAuth2 Form data)
- Wrong password handling (401 Unauthorized)
- Unknown email handling (401 Unauthorized)
- Expired JWT token handling (401 Unauthorized)
- Malformed JWT token handling (401 Unauthorized)
- Missing Authorization token header (401 Unauthorized)
- Inactive user account handling (403 Forbidden)
- Valid /users/me and /me profile endpoints
- Password hashes & credentials are NEVER exposed in any API response
"""

from datetime import datetime, timedelta, timezone
import pytest
from app.models.models import User
from app.core import security


def test_valid_login_json(client):
    """Test valid user login via JSON payload."""
    response = client.post("/api/v1/auth/login", json={"email": "usera@example.com", "password": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert data["expires_in"] > 0
    assert "user" in data
    assert data["user"]["email"] == "usera@example.com"


def test_valid_login_form_data(client):
    """Test valid user login via OAuth2 Form data."""
    response = client.post("/api/v1/auth/login", data={"username": "usera@example.com", "password": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Test login attempt with an incorrect password."""
    response = client.post("/api/v1/auth/login", json={"email": "usera@example.com", "password": "WrongPassword123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."


def test_login_unknown_email(client):
    """Test login attempt with a non-existent email address."""
    response = client.post("/api/v1/auth/login", json={"email": "nonexistent@example.com", "password": "user123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."


def test_expired_jwt_token(client, db_session):
    """Test accessing protected endpoints with an expired JWT token."""
    user_a = db_session.query(User).filter(User.email == "usera@example.com").first()
    expired_token = security.create_access_token(user_a.id, expires_delta=timedelta(minutes=-30))
    
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 401
    assert "could not validate authentication credentials" in response.json()["detail"].lower()


def test_malformed_jwt_token(client):
    """Test accessing protected endpoints with a malformed JWT token string."""
    headers = {"Authorization": "Bearer malformed.invalid.token.string"}
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 401
    assert "could not validate authentication credentials" in response.json()["detail"].lower()


def test_missing_auth_token(client):
    """Test accessing protected endpoints without an Authorization header."""
    response = client.get("/api/v1/me")
    assert response.status_code == 401


def test_inactive_account_login_and_access(client, db_session):
    """Test that inactive accounts are denied login and access."""
    inactive_user = User(
        email="inactive_test@example.com",
        full_name="Inactive Test User",
        password_hash=security.get_password_hash("password123"),
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()

    # 1. Login attempt for inactive user must fail (403 Forbidden)
    login_res = client.post("/api/v1/auth/login", json={"email": "inactive_test@example.com", "password": "password123"})
    assert login_res.status_code == 403
    assert "inactive user" in login_res.json()["detail"].lower()

    # 2. Direct token request for inactive user must fail (403 Forbidden)
    token = security.create_access_token(inactive_user.id)
    headers = {"Authorization": f"Bearer {token}"}
    access_res = client.get("/api/v1/me", headers=headers)
    assert access_res.status_code == 403


def test_valid_users_me_and_me_endpoints(client, user_a_headers):
    """Test valid profile retrieval via /me and /users/me."""
    res_me = client.get("/api/v1/me", headers=user_a_headers)
    assert res_me.status_code == 200
    data_me = res_me.json()
    assert data_me["email"] == "usera@example.com"
    assert data_me["role"] == "user"

    res_users_me = client.get("/api/v1/users/me", headers=user_a_headers)
    assert res_users_me.status_code == 200
    assert res_users_me.json()["email"] == "usera@example.com"


def test_password_hashes_never_returned(client, user_a_headers):
    """Prove password_hash and plaintext passwords are NEVER exposed in response JSON."""
    endpoints_to_check = [
        client.post("/api/v1/auth/login", json={"email": "usera@example.com", "password": "user123"}),
        client.get("/api/v1/me", headers=user_a_headers),
        client.get("/api/v1/users/me", headers=user_a_headers),
        client.get("/api/v1/me/route", headers=user_a_headers),
        client.get("/api/v1/me/vehicle", headers=user_a_headers),
        client.get("/api/v1/me/tracking", headers=user_a_headers),
    ]

    for res in endpoints_to_check:
        assert res.status_code == 200
        res_str = res.text
        assert "password_hash" not in res_str
        assert "hashed_password" not in res_str
        assert "user123" not in res_str
        assert "admin123" not in res_str
