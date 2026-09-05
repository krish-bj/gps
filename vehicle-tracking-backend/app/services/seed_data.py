import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.models import User, BusRoute, Vehicle, GPSTelemetry, RoutePoint, UserAssignment

logger = logging.getLogger("seed_service")

# Predefined Development / Demo Route Points
ROUTE_A_WAYPOINTS = [
    {"sequence": 1, "lat": 12.971598, "lng": 77.594562, "name": "Stop 1: Downtown Hub"},
    {"sequence": 2, "lat": 12.975000, "lng": 77.599000, "name": "Stop 2: City Center"},
    {"sequence": 3, "lat": 12.980000, "lng": 77.605000, "name": "Stop 3: Commercial Zone"},
    {"sequence": 4, "lat": 12.986000, "lng": 77.612000, "name": "Stop 4: Tech Hub East"},
    {"sequence": 5, "lat": 12.992000, "lng": 77.620000, "name": "Stop 5: North Terminal"},
]

ROUTE_B_WAYPOINTS = [
    {"sequence": 1, "lat": 12.930000, "lng": 77.580000, "name": "Stop 1: South Terminal"},
    {"sequence": 2, "lat": 12.940000, "lng": 77.585000, "name": "Stop 2: University Gate"},
    {"sequence": 3, "lat": 12.950000, "lng": 77.590000, "name": "Stop 3: Hospital Square"},
    {"sequence": 4, "lat": 12.960000, "lng": 77.595000, "name": "Stop 4: Metro Interchange"},
    {"sequence": 5, "lat": 12.970000, "lng": 77.600000, "name": "Stop 5: Central Plaza"},
]

def init_db_seed(db: Session, force: bool = False):
    """
    Idempotent development seed script.
    Populates demo users, routes, route points, vehicles, assignments, and initial GPS telemetry.
    Strictly disabled in production unless force=True.
    """
    if settings.APP_ENV == "production" and not force:
        logger.info("[SEED] Skipping automatic development data seed in production environment (APP_ENV='production').")
        return

    logger.info("[SEED] Seeding development / demo data...")

    # 1. Seed Routes & RoutePoints
    route_a = db.query(BusRoute).filter(BusRoute.route_code == "ROUTE-101").first()
    if not route_a:
        route_a = BusRoute(
            route_code="ROUTE-101",
            route_name="Route A - Downtown Express [DEV DEMO]",
            description="[DEV DATA] High frequency express route connecting Downtown Hub to North Terminal",
            start_location="Downtown Hub",
            end_location="North Terminal",
            waypoints_json=json.dumps(ROUTE_A_WAYPOINTS)
        )
        db.add(route_a)
        db.flush()

        for wp in ROUTE_A_WAYPOINTS:
            rp = RoutePoint(
                route_id=route_a.id,
                sequence=wp["sequence"],
                latitude=wp["lat"],
                longitude=wp["lng"],
                name=wp["name"]
            )
            db.add(rp)
        db.flush()

    route_b = db.query(BusRoute).filter(BusRoute.route_code == "ROUTE-202").first()
    if not route_b:
        route_b = BusRoute(
            route_code="ROUTE-202",
            route_name="Route B - Uptown Shuttle [DEV DEMO]",
            description="[DEV DATA] Scenic shuttle route connecting South Terminal to Central Plaza",
            start_location="South Terminal",
            end_location="Central Plaza",
            waypoints_json=json.dumps(ROUTE_B_WAYPOINTS)
        )
        db.add(route_b)
        db.flush()

        for wp in ROUTE_B_WAYPOINTS:
            rp = RoutePoint(
                route_id=route_b.id,
                sequence=wp["sequence"],
                latitude=wp["lat"],
                longitude=wp["lng"],
                name=wp["name"]
            )
            db.add(rp)
        db.flush()

    # 2. Seed Vehicles
    vehicle_1 = db.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-001").first()
    if not vehicle_1:
        vehicle_1 = Vehicle(
            vehicle_code="BUS-001",
            license_plate="BUS-1001-PLATE",
            model_name="Standard Transit Bus [DEV DEMO]",
            status="ONLINE",
            assigned_route_id=route_a.id,
            last_latitude=ROUTE_A_WAYPOINTS[0]["lat"],
            last_longitude=ROUTE_A_WAYPOINTS[0]["lng"],
            last_speed=0.0,
            last_timestamp=datetime.now(timezone.utc)
        )
        db.add(vehicle_1)
        db.flush()

    vehicle_2 = db.query(Vehicle).filter(Vehicle.vehicle_code == "BUS-002").first()
    if not vehicle_2:
        vehicle_2 = Vehicle(
            vehicle_code="BUS-002",
            license_plate="BUS-2002-PLATE",
            model_name="City Express Bus [DEV DEMO]",
            status="ONLINE",
            assigned_route_id=route_b.id,
            last_latitude=ROUTE_B_WAYPOINTS[0]["lat"],
            last_longitude=ROUTE_B_WAYPOINTS[0]["lng"],
            last_speed=0.0,
            last_timestamp=datetime.now(timezone.utc)
        )
        db.add(vehicle_2)
        db.flush()

    # 3. Seed Users & Enforce Assignments
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            full_name="System Administrator [DEV DEMO]",
            password_hash=get_password_hash("admin123"),
            role="admin",
            assigned_route_id=route_a.id,
            assigned_vehicle_id=vehicle_1.id
        )
        db.add(admin)
        db.flush()

    user_a = db.query(User).filter(User.email == "usera@example.com").first()
    if not user_a:
        user_a = User(
            email="usera@example.com",
            full_name="User A [DEV DEMO]",
            password_hash=get_password_hash("user123"),
            role="user",
            assigned_route_id=route_a.id,
            assigned_vehicle_id=vehicle_1.id
        )
        db.add(user_a)
        db.flush()

    assign_a = db.query(UserAssignment).filter(
        UserAssignment.user_id == user_a.id,
        UserAssignment.is_active == True
    ).first()
    if not assign_a:
        assign_a = UserAssignment(
            user_id=user_a.id,
            route_id=route_a.id,
            vehicle_id=vehicle_1.id,
            is_active=True
        )
        db.add(assign_a)

    user_b = db.query(User).filter(User.email == "userb@example.com").first()
    if not user_b:
        user_b = User(
            email="userb@example.com",
            full_name="User B [DEV DEMO]",
            password_hash=get_password_hash("user123"),
            role="user",
            assigned_route_id=route_b.id,
            assigned_vehicle_id=vehicle_2.id
        )
        db.add(user_b)
        db.flush()

    assign_b = db.query(UserAssignment).filter(
        UserAssignment.user_id == user_b.id,
        UserAssignment.is_active == True
    ).first()
    if not assign_b:
        assign_b = UserAssignment(
            user_id=user_b.id,
            route_id=route_b.id,
            vehicle_id=vehicle_2.id,
            is_active=True
        )
        db.add(assign_b)

    # 4. Seed Initial Telemetry Records
    if db.query(GPSTelemetry).filter(GPSTelemetry.vehicle_id == vehicle_1.id).count() == 0:
        telemetry_1 = GPSTelemetry(
            vehicle_id=vehicle_1.id,
            latitude=ROUTE_A_WAYPOINTS[0]["lat"],
            longitude=ROUTE_A_WAYPOINTS[0]["lng"],
            speed=0.0,
            heading=0.0,
            recorded_at=datetime.now(timezone.utc),
            received_at=datetime.now(timezone.utc),
            source="REST"
        )
        db.add(telemetry_1)

    if db.query(GPSTelemetry).filter(GPSTelemetry.vehicle_id == vehicle_2.id).count() == 0:
        telemetry_2 = GPSTelemetry(
            vehicle_id=vehicle_2.id,
            latitude=ROUTE_B_WAYPOINTS[0]["lat"],
            longitude=ROUTE_B_WAYPOINTS[0]["lng"],
            speed=0.0,
            heading=0.0,
            recorded_at=datetime.now(timezone.utc),
            received_at=datetime.now(timezone.utc),
            source="REST"
        )
        db.add(telemetry_2)

    db.commit()
    logger.info("[SEED] Development data seeded successfully (Idempotent execution verified).")

