from app.models.models import User
from app.core import security

def test_login_success(client):
    response = client.post("/api/v1/auth/login/json", json={"email": "usera@example.com", "password": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_json_phase_m(client):
    response = client.post("/api/v1/auth/login", json={"email": "usera@example.com", "password": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert data["expires_in"] > 0
    assert "user" in data
    user_data = data["user"]
    assert user_data["email"] == "usera@example.com"
    # Ensure no password leakage
    assert "password_hash" not in user_data
    assert "hashed_password" not in user_data
    assert "password" not in user_data

def test_login_invalid_password(client):
    response = client.post("/api/v1/auth/login/json", json={"email": "usera@example.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_login_invalid_credentials_generic_error(client):
    response = client.post("/api/v1/auth/login", json={"email": "usera@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."

def test_login_inactive_user_returns_forbidden(client, db_session):
    inactive_user = User(
        email="inactive@example.com",
        full_name="Inactive User",
        password_hash=security.get_password_hash("password123"),
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()

    response = client.post("/api/v1/auth/login", json={"email": "inactive@example.com", "password": "password123"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Inactive user account."

def test_login_form_data(client):
    response = client.post("/api/v1/auth/login", data={"username": "usera@example.com", "password": "user123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

