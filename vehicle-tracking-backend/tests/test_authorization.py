import pytest
from app.models.models import User, BusRoute, Vehicle
from app.services.assignment_service import AssignmentService
from app.exceptions.custom_exceptions import ForbiddenAccessException

def test_user_a_assigned_route_success(client, user_a_headers):
    response = client.get("/api/v1/users/me/assigned-route", headers=user_a_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_route"]["route_code"] == "ROUTE-101"
    assert data["assigned_vehicle"]["vehicle_code"] == "BUS-001"

def test_user_b_assigned_route_success(client, user_b_headers):
    response = client.get("/api/v1/users/me/assigned-route", headers=user_b_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_route"]["route_code"] == "ROUTE-202"
    assert data["assigned_vehicle"]["vehicle_code"] == "BUS-002"

def test_user_a_cannot_access_user_b_vehicle(client, user_a_headers, db_session):
    user_b_vehicle = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    
    res = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}", headers=user_a_headers)
    assert res.status_code == 403

    res_loc = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}/location/latest", headers=user_a_headers)
    assert res_loc.status_code == 403

    res_hist = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}/location/history", headers=user_a_headers)
    assert res_hist.status_code == 403

def test_user_a_cannot_access_user_b_route(client, user_a_headers, db_session):
    user_b_route = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()
    res = client.get(f"/api/v1/routes/{user_b_route.id}", headers=user_a_headers)
    assert res.status_code == 403

def test_admin_can_access_all_vehicles(client, admin_headers, db_session):
    user_b_vehicle = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    res = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}", headers=admin_headers)
    assert res.status_code == 200

def test_assignment_service_direct_unit_test(db_session):
    service = AssignmentService(db_session)
    
    user_a = db_session.query(User).filter(User.email == "usera@example.com").first()
    user_b = db_session.query(User).filter(User.email == "userb@example.com").first()
    
    vehicle_b = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    route_b = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()

    details_a = service.get_user_assigned_details(user_a)
    assert details_a["vehicle"].vehicle_code == "BUS-001"
    assert details_a["route"].route_code == "ROUTE-101"

    with pytest.raises(ForbiddenAccessException):
        service.verify_vehicle_access(user_a, vehicle_b.id)

    with pytest.raises(ForbiddenAccessException):
        service.verify_route_access(user_a, route_b.id)

    vehicle_access = service.verify_vehicle_access(user_b, vehicle_b.id)
    assert vehicle_access.id == vehicle_b.id

