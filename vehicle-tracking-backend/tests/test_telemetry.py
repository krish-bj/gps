def test_telemetry_ingestion_and_history(client, user_a_headers, db_session):
    # 1. Post telemetry
    payload = {
        "vehicle_code": "BUS-001",
        "latitude": 37.7812,
        "longitude": -122.4111,
        "speed_kmh": 41.5,
        "heading": 90.0
    }
    response = client.post("/api/v1/gps/telemetry", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["latitude"] == 37.7812
    assert data["speed_kmh"] == 41.5

    # 2. Get latest location for User A's assigned vehicle
    assigned_res = client.get("/api/v1/users/me/assigned-route", headers=user_a_headers)
    vehicle_id = assigned_res.json()["assigned_vehicle"]["id"]

    latest_res = client.get(f"/api/v1/vehicles/{vehicle_id}/location/latest", headers=user_a_headers)
    assert latest_res.status_code == 200
    assert latest_res.json()["latitude"] == 37.7812

    # 3. Get history for User A's assigned vehicle
    history_res = client.get(f"/api/v1/vehicles/{vehicle_id}/location/history", headers=user_a_headers)
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 1
