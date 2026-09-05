# Phase A — Vehicle Tracking Backend Architecture & Analysis Document

## 1. System Architecture

The GPS Vehicle Tracking System is built on a modern, decoupled three-tier architecture designed for low-latency GPS ingestion, strict data isolation, and real-time query performance.

```
                  ┌─────────────────────────────────────┐
                  │       GPS Simulator / Hardware      │
                  │   (Publishes Lat, Lng, Speed, TS)   │
                  └──────────────────┬──────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │                                       │
                 ▼                                       ▼
    ┌─────────────────────────┐             ┌─────────────────────────┐
    │  Eclipse Mosquitto MQTT │             │    REST Ingestion API   │
    │  Broker (Port 1883)     │             │ (POST /gps/telemetry)   │
    └────────────┬────────────┘             └────────────┬────────────┘
                 │                                       │
                 │  MQTT Ingestion Thread                │
                 └───────────────────┬───────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend Service                        │
│                                                                         │
│  - Middleware: CORS, Request Logging                                    │
│  - Auth & Security: JWT Bearer Verification, Bcrypt Password Hashing   │
│  - Authorization Engine: User-to-Route & Vehicle Access Scope Guards     │
│  - Services: Database Migration (Alembic), MQTT Listener, Seeder        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PostgreSQL 16 Database Engine                      │
│                                                                         │
│  - Users Table (Auth, Roles, Assigned Route & Vehicle FKs)              │
│  - BusRoutes Table (Metadata, Route Waypoints JSON)                     │
│  - Vehicles Table (Plate, Model, Cached Latest GPS State)               │
│  - GPSTelemetry Table (Historical Coordinate Log Stream)                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Modules

| Module Name | Responsibilities |
|-------------|────────────────--|
| **`core`** | Configuration settings (`pydantic-settings`), database connection management, JWT token encoding/decoding, bcrypt password hashing. |
| **`models`** | SQLAlchemy 2.0 ORM Declarative entities (`User`, `BusRoute`, `Vehicle`, `GPSTelemetry`). |
| **`schemas`** | Pydantic V2 request & response schemas (Validation, Auth Tokens, Route Waypoints, Telemetry Payloads). |
| **`api`** | FastAPI endpoint routers (`auth`, `users`, `routes`, `vehicles`, `telemetry`) and dependency functions (`deps.py`). |
| **`services`** | MQTT background subscriber service (`paho-mqtt`) and automated database seed initializer (`seed_data.py`). |
| **`simulator`** | Standalone Python script driving GPS movement for test vehicles. |

---

## 3. Data Entities & Schema Design

```
   ┌───────────────────────────────────┐
   │               User                │
   ├───────────────────────────────────┤
   │ id: int (PK)                      │
   │ email: str (Unique, Index)        │
   │ full_name: str                    │
   │ hashed_password: str              │
   │ is_active: bool                   │
   │ role: str ('user' | 'admin')      │
   │ assigned_route_id: int (FK) ──────┼──────┐
   │ assigned_vehicle_id: int (FK) ────┼──┐   │
   └───────────────────────────────────┘  │   │
                                          │   │
   ┌───────────────────────────────────┐  │   │
   │             BusRoute              │  │   │
   ├───────────────────────────────────┤  │   │
   │ id: int (PK) <────────────────────┼──┼───┘
   │ route_code: str (Unique, Index)   │  │
   │ route_name: str                   │  │
   │ start_location: str               │  │
   │ end_location: str                 │  │
   │ waypoints_json: text (JSON List)  │  │
   │ created_at: datetime              │  │
   └─────────────────┬─────────────────┘  │
                     │                    │
                     │ 1:N                │
                     ▼                    │
   ┌───────────────────────────────────┐  │
   │              Vehicle              │  │
   ├───────────────────────────────────┤  │
   │ id: int (PK) <────────────────────┼──┘
   │ vehicle_code: str (Unique, Index) │
   │ license_plate: str                │
   │ status: str ('ONLINE'|'MOVING')   │
   │ assigned_route_id: int (FK)       │
   │ last_latitude: float (Cached)     │
   │ last_longitude: float (Cached)    │
   │ last_speed: float (Cached)        │
   │ last_timestamp: datetime (Cached) │
   └─────────────────┬─────────────────┘
                     │
                     │ 1:N
                     ▼
   ┌───────────────────────────────────┐
   │           GPSTelemetry            │
   ├───────────────────────────────────┤
   │ id: int (PK)                      │
   │ vehicle_id: int (FK, Index)       │
   │ latitude: float                   │
   │ longitude: float                  │
   │ speed_kmh: float                  │
   │ heading: float                    │
   │ timestamp: datetime (Index)       │
   │ created_at: datetime              │
   └───────────────────────────────────┘
```

---

## 4. Entity Relationships

1. **User → BusRoute** (Many-to-One / Assigned 1-to-1):
   - `User.assigned_route_id` references `BusRoute.id`.
   - Each regular user is assigned exactly 1 bus route.
2. **User → Vehicle** (Many-to-One / Assigned 1-to-1):
   - `User.assigned_vehicle_id` references `Vehicle.id`.
   - Each regular user is assigned exactly 1 vehicle.
3. **BusRoute → Vehicle** (One-to-Many):
   - `Vehicle.assigned_route_id` references `BusRoute.id`.
   - A bus route can have vehicles assigned to it.
4. **Vehicle → GPSTelemetry** (One-to-Many):
   - `GPSTelemetry.vehicle_id` references `Vehicle.id`.
   - Stores time-series historical GPS points for every vehicle update.

---

## 5. API Endpoints List

### Authentication
- `POST /api/v1/auth/login`: Form-data login endpoint returning JWT access token.
- `POST /api/v1/auth/login/json`: JSON payload login endpoint for mobile/API clients.

### User & Assignments
- `GET /api/v1/users/me`: Current user profile.
- `GET /api/v1/users/me/assigned-route`: Unified response returning the user's assigned route, parsed waypoints array, assigned vehicle, and latest telemetry point.

### Bus Routes (Authorized)
- `GET /api/v1/routes`: Returns assigned route for regular user; all routes for admin.
- `GET /api/v1/routes/{route_id}`: Route details. Enforces authorization check (HTTP 403 Forbidden if `route_id != user.assigned_route_id`).

### Vehicles & Telemetry (Authorized)
- `GET /api/v1/vehicles`: Returns assigned vehicle for regular user; all vehicles for admin.
- `GET /api/v1/vehicles/{vehicle_id}`: Vehicle metadata. Enforces authorization check.
- `GET /api/v1/vehicles/{vehicle_id}/location/latest`: Returns latest GPS coordinates. Enforces authorization check.
- `GET /api/v1/vehicles/{vehicle_id}/location/history`: Returns historical breadcrumb coordinates. Enforces authorization check.

### Telemetry Ingestion
- `POST /api/v1/gps/telemetry`: Ingests GPS point (`latitude`, `longitude`, `speed_kmh`, `heading`, `vehicle_code`).

---

## 6. Authentication & Authorization Flows

### Authentication Flow
```
Client (Flutter/HTTP)                    FastAPI Backend                       Database
       │                                       │                                  │
       │─── POST /api/v1/auth/login ──────────>│                                  │
       │    (email, password)                  │─── Query User by Email ─────────>│
       │                                       │<── Return User Record ───────────│
       │                                       │                                  │
       │                                       │── Verify Bcrypt Password         │
       │                                       │   Generate JWT (exp, sub: id)    │
       │<── 200 OK Token Response ─────────────│                                  │
       │    (access_token, token_type)         │                                  │
```

### Authorization & Scope Guard Flow
```
Client Request                            FastAPI Dependency                     Decision
       │                                 (verify_user_vehicle_access)               │
       │─── GET /vehicles/2/location/latest ──>│                                      │
       │    Header: Bearer <User A Token>      │── Decode JWT Token (User A)          │
       │                                       │   Extract User A.assigned_vehicle_id  │
       │                                       │   Compare assigned_vehicle_id vs 2    │
       │                                       │                                        │
       │                                       ├─── If assigned_vehicle_id != 2 ───────► HTTP 403 Forbidden!
       │                                       └─── If assigned_vehicle_id == 2 ───────► 200 OK (Data Returned)
```

---

## 7. Real-Time MQTT GPS Ingestion Flow

```
[ Vehicle / GPS Simulator ]
             │
             │ Publishes JSON to topic `vehicles/BUS-001/telemetry`
             ▼
[ Eclipse Mosquitto MQTT Broker ] (Port 1883)
             │
             │ Background MQTT Listener Thread (Paho-MQTT)
             ▼
[ FastAPI MQTT Consumer ]
             │
             ├── 1. Parse JSON Payload (lat, lng, speed, timestamp)
             ├── 2. Resolve Vehicle ID by vehicle_code
             ├── 3. INSERT new record into `gps_telemetry` table
             └── 4. UPDATE cached `last_latitude`, `last_longitude`, `last_speed` on `vehicles` table
```

---

## 8. Database Strategy & Migrations

1. **ORM Engine**: SQLAlchemy 2.0 with type-safe `Mapped[...]` and `mapped_column(...)`.
2. **Dual Database Support**:
   - **SQLite**: Used for zero-config local development and rapid Pytest unit testing.
   - **PostgreSQL 16**: Used for containerized production deployment via Docker Compose.
3. **Alembic Migrations**:
   - Migration scripts stored under `alembic/versions/`.
   - `alembic.ini` and `alembic/env.py` configured to connect to active database environment.

---

## 9. Repository Folder Structure (`vehicle-tracking-backend`)

```
vehicle-tracking-backend/
├── alembic/                      # Alembic Database Migrations
│   ├── versions/
│   │   └── 001_initial_schema.py
│   └── env.py
├── app/                          # Main Application Package
│   ├── api/
│   │   ├── deps.py               # Auth & Authorization Dependencies
│   │   └── v1/                   # Endpoint Routers
│   │       ├── api.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── routes.py
│   │       ├── vehicles.py
│   │       └── telemetry.py
│   ├── core/                     # Configuration, Database Engine, JWT & Bcrypt
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/                   # SQLAlchemy ORM Models
│   │   └── models.py
│   ├── schemas/                  # Pydantic V2 Request & Response Schemas
│   │   └── schemas.py
│   ├── services/                 # MQTT Subscriber & Seed Data Populator
│   │   ├── mqtt_service.py
│   │   └── seed_data.py
│   └── main.py                   # FastAPI Application Entrypoint
├── tests/                        # Pytest Test Suite
│   ├── conftest.py               # Fixtures for Test Client & Credentials
│   ├── test_auth.py              # Login & Token Tests
│   ├── test_authorization.py     # User-Isolation Scope & 403 Tests
│   └── test_telemetry.py         # Telemetry & History Tests
├── simulator/                    # GPS Coordinate Stream Simulator
│   └── gps_simulator.py
├── alembic.ini                   # Alembic Config
├── pytest.ini                    # Pytest Config
├── Dockerfile                    # Containerization Build Spec
├── docker-compose.yml            # Multi-container Compose Spec
├── mosquitto.conf                # Mosquitto Broker Spec
├── requirements.txt              # Dependency Specifications
└── README.md                     # Documentation
```

---

## 10. Testing Strategy

1. **Automated Unit & Integration Tests (`pytest`)**:
   - `test_auth.py`: Tests valid/invalid login, token creation, and OAuth2 form data compatibility.
   - `test_authorization.py`: Asserts strict **HTTP 403 Forbidden** errors when User A attempts to access User B's vehicle ID, route ID, current location, or location history.
   - `test_telemetry.py`: Tests GPS point ingestion via REST, latest position updates, and chronological history queries.
2. **Schema & Migration Verification**:
   - Execution of `alembic upgrade head` on clean database instances.

---

## 11. Production-Readiness Checklist

- [x] JWT Bearer Authentication & Bcrypt Password Hashing implemented.
- [x] Backend Authorization Scope Guards enforcing user isolation (403 Forbidden on unauthorized IDs).
- [x] Dual Telemetry Ingestion (MQTT broker + REST fallback).
- [x] Cache strategy on Vehicle table for instant single-query latest location performance.
- [x] Alembic Database Migrations configured and verified.
- [x] Pytest suite with 100% pass rate.
- [x] Multi-container Docker Compose configuration (`PostgreSQL 16`, `Mosquitto MQTT`, `FastAPI`).
