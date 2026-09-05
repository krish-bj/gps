import pytest
from app.models.models import User
from app.core import security

def test_get_current_user_me_success(client, user_a_headers):
    # Test GET /api/v1/users/me and GET /api/v1/me
    res1 = client.get("/api/v1/users/me", headers=user_a_headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["email"] == "usera@example.com"
    assert "password_hash" not in data1
    assert "hashed_password" not in data1

    res2 = client.get("/api/v1/me", headers=user_a_headers)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["email"] == "usera@example.com"
    assert "password_hash" not in data2

def test_get_current_user_unauthorized_fails(client):
    res = client.get("/api/v1/users/me")
    assert res.status_code == 401

def test_get_current_user_inactive_account_denied(client, db_session):
    inactive = User(
        email="inactive_me@example.com",
        full_name="Inactive Me",
        password_hash=security.get_password_hash("pass123"),
        is_active=False
    )
    db_session.add(inactive)
    db_session.commit()

    token = security.create_access_token(inactive.id)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/users/me", headers=headers)
    assert res.status_code == 403

def test_get_me_route_user_a(client, user_a_headers):
    res = client.get("/api/v1/me/route", headers=user_a_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["route_code"] == "ROUTE-101"
    assert "Downtown Express" in data["name"]
    assert "start_location" in data
    assert "end_location" in data
    assert "route_points" in data

def test_get_me_route_user_b(client, user_b_headers):
    res = client.get("/api/v1/me/route", headers=user_b_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["route_code"] == "ROUTE-202"

def test_get_me_vehicle_user_a(client, user_a_headers):
    res = client.get("/api/v1/me/vehicle", headers=user_a_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["vehicle_code"] == "BUS-001"
    assert "registration_number" in data
    assert "display_name" in data
    assert "status" in data

def test_get_me_vehicle_user_b(client, user_b_headers):
    res = client.get("/api/v1/me/vehicle", headers=user_b_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["vehicle_code"] == "BUS-002"

def test_user_without_assignment_returns_error(client, db_session):
    no_assign_user = User(
        email="unassigned@example.com",
        full_name="Unassigned Driver",
        password_hash=security.get_password_hash("pass123"),
        is_active=True
    )
    db_session.add(no_assign_user)
    db_session.commit()

    token = security.create_access_token(no_assign_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    res_route = client.get("/api/v1/me/route", headers=headers)
    assert res_route.status_code in [403, 404]

    res_vehicle = client.get("/api/v1/me/vehicle", headers=headers)
    assert res_vehicle.status_code in [403, 404]
