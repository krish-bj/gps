import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.models import User, BusRoute, Vehicle, GPSTelemetry

ROUTE_A_WAYPOINTS = [
    {"lat": 37.774929, "lng": -122.419416, "name": "Stop 1: Central Station", "stop_order": 1},
    {"lat": 37.778500, "lng": -122.415000, "name": "Stop 2: Civic Center", "stop_order": 2},
    {"lat": 37.783333, "lng": -122.408889, "name": "Stop 3: Market Street", "stop_order": 3},
    {"lat": 37.788500, "lng": -122.402000, "name": "Stop 4: Financial District", "stop_order": 4},
    {"lat": 37.795000, "lng": -122.394000, "name": "Stop 5: Tech Park Terminal", "stop_order": 5},
]

ROUTE_B_WAYPOINTS = [
    {"lat": 37.804400, "lng": -122.408000, "name": "Stop 1: Fisherman Wharf", "stop_order": 1},
    {"lat": 37.800000, "lng": -122.418000, "name": "Stop 2: Russian Hill", "stop_order": 2},
    {"lat": 37.791000, "lng": -122.427000, "name": "Stop 3: Pacific Heights", "stop_order": 3},
    {"lat": 37.783000, "lng": -122.435000, "name": "Stop 4: Japantown", "stop_order": 4},
    {"lat": 37.776000, "lng": -122.451000, "name": "Stop 5: University Campus", "stop_order": 5},
]

def init_db_seed(db: Session):
    """
    Populate seed data: Routes, Vehicles, Users, initial Telemetry.
    """
    # 1. Routes
    route_a = db.query(BusRoute).filter(BusRoute.route_code == "ROUTE-101").first()
    if not route_a:
        route_a = BusRoute(
            route_code="ROUTE-101",
            route_name="Route A - Downtown Express",
            description="High frequency route connecting Central Station to Tech Park",
            start_location="Central Station",
            end_location="Tech Park Terminal",
            waypoints_json=json.dumps(ROUTE_A_WAYPOINTS)
        )
        db.add(route_a)
        db.flush()

    route_b = db.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()
    if not route_b:
        route_b = BusRoute(
            route_code="ROUTE-202",
            route_name="Route B - Uptown Shuttle",
            description="Scenic shuttle route connecting Fisherman Wharf to University Campus",
            start_location="Fisherman Wharf",
            end_location="University Campus",
            waypoints_json=json.dumps(ROUTE_B_WAYPOINTS)
        )
        db.add(route_b)
        db.flush()

    # 2. Vehicles
    vehicle_1 = db.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    if not vehicle_1:
        vehicle_1 = Vehicle(
            vehicle_code="BUS-001",
            license_plate="CA-7789-EX",
            model_name="Volvo Electric Bus 7900",
            status="MOVING",
            assigned_route_id=route_a.id,
            last_latitude=ROUTE_A_WAYPOINTS[0]["lat"],
            last_longitude=ROUTE_A_WAYPOINTS[0]["lng"],
            last_speed=38.5,
            last_timestamp=datetime.now(timezone.utc)
        )
        db.add(vehicle_1)
        db.flush()

    vehicle_2 = db.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    if not vehicle_2:
        vehicle_2 = Vehicle(
            vehicle_code="BUS-002",
            license_plate="CA-9941-SH",
            model_name="BYD K9 Electric Bus",
            status="MOVING",
            assigned_route_id=route_b.id,
            last_latitude=ROUTE_B_WAYPOINTS[0]["lat"],
            last_longitude=ROUTE_B_WAYPOINTS[0]["lng"],
            last_speed=42.0,
            last_timestamp=datetime.now(timezone.utc)
        )
        db.add(vehicle_2)
        db.flush()

    # 3. Users
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            full_name="Fleet Administrator",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            assigned_route_id=route_a.id,
            assigned_vehicle_id=vehicle_1.id
        )
        db.add(admin)

    user_a = db.query(User).filter(User.email == "usera@example.com").first()
    if not user_a:
        user_a = User(
            email="usera@example.com",
            full_name="User A (Route A Driver)",
            hashed_password=get_password_hash("user123"),
            role="user",
            assigned_route_id=route_a.id,
            assigned_vehicle_id=vehicle_1.id
        )
        db.add(user_a)

    user_b = db.query(User).filter(User.email == "userb@example.com").first()
    if not user_b:
        user_b = User(
            email="userb@example.com",
            full_name="User B (Route B Driver)",
            hashed_password=get_password_hash("user123"),
            role="user",
            assigned_route_id=route_b.id,
            assigned_vehicle_id=vehicle_2.id
        )
        db.add(user_b)

    # 4. Telemetry Logs
    if db.query(GPSTelemetry).filter(GPSTelemetry.vehicle_id == vehicle_1.id).count() == 0:
        telemetry_1 = GPSTelemetry(
            vehicle_id=vehicle_1.id,
            latitude=ROUTE_A_WAYPOINTS[0]["lat"],
            longitude=ROUTE_A_WAYPOINTS[0]["lng"],
            speed_kmh=38.5,
            heading=45.0,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(telemetry_1)

    if db.query(GPSTelemetry).filter(GPSTelemetry.vehicle_id == vehicle_2.id).count() == 0:
        telemetry_2 = GPSTelemetry(
            vehicle_id=vehicle_2.id,
            latitude=ROUTE_B_WAYPOINTS[0]["lat"],
            longitude=ROUTE_B_WAYPOINTS[0]["lng"],
            speed_kmh=42.0,
            heading=120.0,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(telemetry_2)

    db.commit()
