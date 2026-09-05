import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
from app.schemas.route_point import RoutePointBase
from app.schemas.schemas import GPSTelemetryCreate
from app.models.models import RoutePoint, UserAssignment, GPSTelemetry

def test_latitude_longitude_validation_success():
    point = RoutePointBase(sequence=1, latitude=37.7749, longitude=-122.4194, name="Stop 1")
    assert point.latitude == 37.7749
    assert point.longitude == -122.4194

def test_latitude_out_of_range_fails():
    with pytest.raises(ValidationError) as exc:
        RoutePointBase(sequence=1, latitude=95.0, longitude=-122.4194)
    assert "latitude" in str(exc.value).lower()

def test_longitude_out_of_range_fails():
    with pytest.raises(ValidationError) as exc:
        RoutePointBase(sequence=1, latitude=37.7749, longitude=-200.0)
    assert "longitude" in str(exc.value).lower()

def test_speed_cannot_be_negative():
    with pytest.raises(ValidationError) as exc:
        GPSTelemetryCreate(vehicle_id=1, latitude=37.7, longitude=-122.4, speed_kmh=-10.0)
    assert "speed" in str(exc.value).lower()

def test_user_assignment_entity_creation():
    assignment = UserAssignment(
        id=1,
        user_id=10,
        route_id=100,
        vehicle_id=50,
        assigned_at=datetime.now(timezone.utc),
        is_active=True
    )
    assert assignment.user_id == 10
    assert assignment.route_id == 100
    assert assignment.vehicle_id == 50
    assert assignment.is_active is True
