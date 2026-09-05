def test_login_success(client):
    response = client.post("/api/v1/auth/login/json", json={"email": "usera@example.com", "password": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client):
    response = client.post("/api/v1/auth/login/json", json={"email": "usera@example.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_login_form_data(client):
    response = client.post("/api/v1/auth/login", data={"username": "usera@example.com", "password": "user123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
