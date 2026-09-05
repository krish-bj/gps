from app.models.models import User, BusRoute, Vehicle

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
    # Fetch User B's vehicle ID
    user_b_vehicle = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    
    # 1. Access vehicle details -> Expect 403 Forbidden
    res = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}", headers=user_a_headers)
    assert res.status_code == 403

    # 2. Access latest location -> Expect 403 Forbidden
    res_loc = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}/location/latest", headers=user_a_headers)
    assert res_loc.status_code == 403

    # 3. Access location history -> Expect 403 Forbidden
    res_hist = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}/location/history", headers=user_a_headers)
    assert res_hist.status_code == 403

def test_user_a_cannot_access_user_b_route(client, user_a_headers, db_session):
    # Fetch User B's route ID
    user_b_route = db_session.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()

    # Request route details for Route B using User A's token -> Expect 403 Forbidden
    res = client.get(f"/api/v1/routes/{user_b_route.id}", headers=user_a_headers)
    assert res.status_code == 403

def test_admin_can_access_all_vehicles(client, admin_headers, db_session):
    user_b_vehicle = db_session.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    res = client.get(f"/api/v1/vehicles/{user_b_vehicle.id}", headers=admin_headers)
    assert res.status_code == 200
