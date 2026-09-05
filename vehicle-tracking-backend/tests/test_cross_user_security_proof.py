"""
PHASE AB — Cross-User Authorization Security Tests (Prompt AB1)
Proves end-to-end data isolation between User A and User B:
- User A (assigned to Route A / BUS-001) can ONLY view Route A and BUS-001 data.
- User B (assigned to Route B / BUS-002) can ONLY view Route B and BUS-002 data.
- Any cross-tenant attempt or ID manipulation results in HTTP 403 Forbidden.
- Admins possess system-wide visibility.
"""

import pytest
from app.models.models import User, BusRoute, Vehicle
from app.services.assignment_service import AssignmentService
from app.exceptions.custom_exceptions import ForbiddenAccessException


# =====================================================================
# 1. USER A PERMISSIONS & ISOLATION PROOFS
# =====================================================================

def test_user_a_sees_assigned_route_a(client, user_a_headers):
    """Prove User A can fetch assigned Route A."""
    response = client.get("/api/v1/me/route", headers=user_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["route_code"] == "ROUTE-101"
    assert "route_points" in data
    assert len(data["route_points"]) > 0


def test_user_a_sees_assigned_vehicle_1(client, user_a_headers):
    """Prove User A can fetch assigned Vehicle BUS-001."""
    response = client.get("/api/v1/me/vehicle", headers=user_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_code"] == "BUS-001"


def test_user_a_sees_bus_001_gps_latest(client, user_a_headers, db_session):
    """Prove User A can access latest GPS location of assigned BUS-001."""
    bus_001 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    res = client.get(f"/api/v1/vehicles/{bus_001.id}/location/latest", headers=user_a_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["vehicle_id"] == bus_001.id


def test_user_a_sees_bus_001_gps_history(client, user_a_headers, db_session):
    """Prove User A can access location history of assigned BUS-001."""
    bus_001 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    res = client.get(f"/api/v1/vehicles/{bus_001.id}/location/history", headers=user_a_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_user_a_cannot_see_route_b(client, user_a_headers, db_session):
    """Prove User A CANNOT view Route B (HTTP 403 Forbidden)."""
    route_b = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()
    res = client.get(f"/api/v1/routes/{route_b.id}", headers=user_a_headers)
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()


def test_user_a_cannot_see_bus_002(client, user_a_headers, db_session):
    """Prove User A CANNOT view BUS-002 metadata (HTTP 403 Forbidden)."""
    bus_002 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    res = client.get(f"/api/v1/vehicles/{bus_002.id}", headers=user_a_headers)
    assert res.status_code == 403


def test_user_a_cannot_see_bus_002_gps_latest(client, user_a_headers, db_session):
    """Prove User A CANNOT view BUS-002 latest location (HTTP 403 Forbidden)."""
    bus_002 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    res = client.get(f"/api/v1/vehicles/{bus_002.id}/location/latest", headers=user_a_headers)
    assert res.status_code == 403


def test_user_a_cannot_see_bus_002_gps_history(client, user_a_headers, db_session):
    """Prove User A CANNOT view BUS-002 location history (HTTP 403 Forbidden)."""
    bus_002 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    res = client.get(f"/api/v1/vehicles/{bus_002.id}/location/history", headers=user_a_headers)
    assert res.status_code == 403


# =====================================================================
# 2. USER B PERMISSIONS & ISOLATION PROOFS
# =====================================================================

def test_user_b_sees_assigned_route_b(client, user_b_headers):
    """Prove User B can fetch assigned Route B."""
    response = client.get("/api/v1/me/route", headers=user_b_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["route_code"] == "ROUTE-202"


def test_user_b_sees_assigned_vehicle_2(client, user_b_headers):
    """Prove User B can fetch assigned Vehicle BUS-002."""
    response = client.get("/api/v1/me/vehicle", headers=user_b_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["vehicle_code"] == "BUS-002"


def test_user_b_sees_bus_002_gps_latest(client, user_b_headers, db_session):
    """Prove User B can access latest GPS location of assigned BUS-002."""
    bus_002 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    res = client.get(f"/api/v1/vehicles/{bus_002.id}/location/latest", headers=user_b_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["vehicle_id"] == bus_002.id


def test_user_b_sees_bus_002_gps_history(client, user_b_headers, db_session):
    """Prove User B can access location history of assigned BUS-002."""
    bus_002 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    res = client.get(f"/api/v1/vehicles/{bus_002.id}/location/history", headers=user_b_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_user_b_cannot_see_route_a(client, user_b_headers, db_session):
    """Prove User B CANNOT view Route A (HTTP 403 Forbidden)."""
    route_a = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-101").first()
    res = client.get(f"/api/v1/routes/{route_a.id}", headers=user_b_headers)
    assert res.status_code == 403


def test_user_b_cannot_see_bus_001(client, user_b_headers, db_session):
    """Prove User B CANNOT view BUS-001 metadata (HTTP 403 Forbidden)."""
    bus_001 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    res = client.get(f"/api/v1/vehicles/{bus_001.id}", headers=user_b_headers)
    assert res.status_code == 403


def test_user_b_cannot_see_bus_001_gps_latest(client, user_b_headers, db_session):
    """Prove User B CANNOT view BUS-001 latest location (HTTP 403 Forbidden)."""
    bus_001 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    res = client.get(f"/api/v1/vehicles/{bus_001.id}/location/latest", headers=user_b_headers)
    assert res.status_code == 403


def test_user_b_cannot_see_bus_001_gps_history(client, user_b_headers, db_session):
    """Prove User B CANNOT view BUS-001 location history (HTTP 403 Forbidden)."""
    bus_001 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    res = client.get(f"/api/v1/vehicles/{bus_001.id}/location/history", headers=user_b_headers)
    assert res.status_code == 403


# =====================================================================
# 3. CONVENIENT /ME ENDPOINT ISOLATION PROOFS
# =====================================================================

def test_user_a_me_tracking_endpoints(client, user_a_headers):
    """Prove /me/tracking and /me/tracking/current strictly isolate User A to BUS-001."""
    res_summary = client.get("/api/v1/me/tracking", headers=user_a_headers)
    assert res_summary.status_code == 200
    summary_data = res_summary.json()
    assert summary_data["route"]["route_code"] == "ROUTE-101"
    assert summary_data["vehicle"]["vehicle_code"] == "BUS-001"

    res_current = client.get("/api/v1/me/tracking/current", headers=user_a_headers)
    assert res_current.status_code == 200
    assert res_current.json()["vehicle_code"] == "BUS-001"

    res_hist = client.get("/api/v1/me/tracking/history", headers=user_a_headers)
    assert res_hist.status_code == 200


def test_user_b_me_tracking_endpoints(client, user_b_headers):
    """Prove /me/tracking and /me/tracking/current strictly isolate User B to BUS-002."""
    res_summary = client.get("/api/v1/me/tracking", headers=user_b_headers)
    assert res_summary.status_code == 200
    summary_data = res_summary.json()
    assert summary_data["route"]["route_code"] == "ROUTE-202"
    assert summary_data["vehicle"]["vehicle_code"] == "BUS-002"

    res_current = client.get("/api/v1/me/tracking/current", headers=user_b_headers)
    assert res_current.status_code == 200
    assert res_current.json()["vehicle_code"] == "BUS-002"


# =====================================================================
# 4. ADMIN PRIVILEGE & SERVICE DIRECT PROOFS
# =====================================================================

def test_admin_can_access_any_route_and_vehicle(client, admin_headers, db_session):
    """Prove Admin users have full system-wide access to all routes and vehicles."""
    bus_001 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    bus_002 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    route_a = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-101").first()
    route_b = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()

    assert client.get(f"/api/v1/vehicles/{bus_001.id}", headers=admin_headers).status_code == 200
    assert client.get(f"/api/v1/vehicles/{bus_002.id}", headers=admin_headers).status_code == 200
    assert client.get(f"/api/v1/routes/{route_a.id}", headers=admin_headers).status_code == 200
    assert client.get(f"/api/v1/routes/{route_b.id}", headers=admin_headers).status_code == 200


def test_assignment_service_raises_forbidden_on_cross_access(db_session):
    """Direct unit test of AssignmentService authorization guards."""
    service = AssignmentService(db_session)
    user_a = db_session.query(User).filter(User.email == "usera@example.com").first()
    bus_002 = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    route_b = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()

    with pytest.raises(ForbiddenAccessException):
        service.verify_vehicle_access(user_a, bus_002.id)

    with pytest.raises(ForbiddenAccessException):
        service.verify_route_access(user_a, route_b.id)
