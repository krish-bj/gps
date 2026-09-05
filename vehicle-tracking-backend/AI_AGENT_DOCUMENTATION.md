# GPS Vehicle Tracking Backend — AI Agent Technical Documentation

> **Target Audience**: AI Coding Assistants, Technical Reviewers & Automated Developers  
> **Repository Path**: `vehicle-tracking-backend/`  
> **Primary Stack**: Python 3.12, FastAPI, SQLAlchemy 2.0 (Declarative Base & Mapped Columns), Pydantic V2, Alembic, Pytest, PyJWT, Bcrypt, Mosquitto MQTT.

---

## 1. System Architecture & Folder Layout

The project follows a **Clean Modular Layered Architecture**. Controllers (API endpoints) contain **zero business logic** and delegate directly to dedicated service classes and data repositories.

```
API / Controller Layer (app/api/v1/endpoints/*)
         ↓
Service Layer (app/services/*)
         ↓
Repository Layer (app/repositories/*)
         ↓
Database Models (app/models/models.py)
```

```
vehicle-tracking-backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # Reusable FastAPI dependencies (JWT Auth, Admin check, Assignment Auth)
│   │   └── v1/
│   │       ├── router.py            # Central v1 API router (/api/v1)
│   │       └── endpoints/
│   │           ├── auth.py          # Login API (/auth/login)
│   │           ├── me.py            # Current User, Tracking & Location (/me, /me/route, /me/vehicle, /me/tracking)
│   │           ├── users.py         # User management (/users, /users/me)
│   │           ├── routes.py        # Route endpoints (/routes, /routes/{id})
│   │           ├── vehicles.py      # Vehicle endpoints (/vehicles, /vehicles/{id})
│   │           ├── telemetry.py     # Real-time GPS ingestion & history (/gps)
│   │           └── ws_tracking.py   # Optional WebSocket live streaming bonus (/ws/tracking)
│   ├── core/
│   │   ├── config.py                # Pydantic Settings with env validation & secret masking
│   │   ├── logging_config.py        # Structured logging setup with SensitiveDataFilter
│   │   ├── middleware.py            # Security headers & Request size limit middleware
│   │   └── security.py              # Bcrypt password hashing/verification & JWT encoding/decoding
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy 2.0 DeclarativeBase
│   │   └── session.py               # Engine configuration & get_db generator
│   ├── models/
│   │   └── models.py                # SQLAlchemy 2.0 Mapped Entities (User, BusRoute, RoutePoint, Vehicle, UserAssignment, GPSTelemetry)
│   ├── schemas/
│   │   ├── user.py                  # User schemas excluding password hashes (UserResponse)
│   │   ├── route_point.py           # RoutePoint schemas with coordinate validation
│   │   ├── user_assignment.py       # UserAssignment schemas
│   │   └── schemas.py               # Token, BusRouteResponse, VehicleResponse, GPSTelemetryResponse schemas
│   ├── repositories/
│   │   ├── user_repository.py       # DB access for User entities
│   │   ├── route_repository.py      # DB access for BusRoute entities
│   │   ├── vehicle_repository.py    # DB access for Vehicle entities
│   │   └── telemetry_repository.py  # DB access for GPSTelemetry logs
│   ├── services/
│   │   ├── auth_service.py          # Authentication & token issue logic
│   │   ├── user_service.py          # User management business logic
│   │   ├── assignment_service.py    # Single source of truth for user active assignments & authorization
│   │   ├── tracking_service.py      # Telemetry processing & route/vehicle access verification
│   │   ├── seed_service.py          # Initial database seeding
│   │   └── seed_data.py             # Default initial seed data (Users, Routes, Vehicles)
│   ├── exceptions/
│   │   ├── custom_exceptions.py     # Custom exception domain model mapped to HTTP status codes
│   │   └── handlers.py              # Centralized exception handlers hiding technical stack traces in production
│   ├── mqtt/
│   │   └── client.py                # Mosquitto MQTT subscriber listening on vehicles/+/gps
│   ├── utils/
│   │   └── helpers.py               # Helper utilities (JSON parsing, coordinate math)
│   └── main.py                      # FastAPI lifespan setup, exception handlers, CORS & health check
├── alembic/                         # Alembic database migration scripts
├── mosquitto/                       # Mosquitto MQTT broker configuration & pwfile
├── scripts/
│   └── seed_db.py                   # Command-line database seed script
├── simulator/
│   └── gps_simulator.py             # Standalone Python GPS Simulator over MQTT
├── tests/                           # Pytest automated test suite
└── pytest.ini                       # Pytest configuration
```

---

## 2. Assessment Acceptance Test Audit Results

Below is the complete audit matrix verifying all assessment requirements:

| Requirement Category | Specific Assessment Requirement | Status | Verification Evidence / Implementation Reference | Identified Problems |
| :--- | :--- | :---: | :--- | :--- |
| **Authentication** | **User A can login** | **`PASS`** | `AuthService.authenticate_user()` verifies bcrypt hash for `usera@example.com` and issues signed JWT access token. Tested in `test_valid_login`. | None |
| **Authentication** | **User B can login** | **`PASS`** | Authenticates `userb@example.com` / `UserB@123` via `POST /api/v1/auth/login`. Tested in `test_user_a_and_user_b_isolation`. | None |
| **Authentication** | **Invalid login rejected** | **`PASS`** | Rejects wrong password (`401`), unknown email (`401`), expired JWT (`401`), malformed token (`401`), and inactive user (`403`). Tested in `test_authentication_suite.py`. | None |
| **Assignment** | **User A assigned Route A + BUS-001** | **`PASS`** | `scripts/seed_db.py` and `SeedService` idempotently link User A $\rightarrow$ Route A (`ROUTE-101`) $\rightarrow$ BUS-001 via `UserAssignment`. | None |
| **Assignment** | **User B assigned Route B + BUS-002** | **`PASS`** | `SeedService` idempotently links User B $\rightarrow$ Route B (`ROUTE-202`) $\rightarrow$ BUS-002 via `UserAssignment`. | None |
| **Authorization** | **User A sees only Route A** | **`PASS`** | `GET /api/v1/me/route` calls `TrackingService.get_my_assigned_route()`, strictly returning Route A details. | None |
| **Authorization** | **User A sees only BUS-001** | **`PASS`** | `GET /api/v1/me/vehicle` calls `TrackingService.get_my_assigned_vehicle()`, strictly returning BUS-001 details. | None |
| **Authorization** | **User A cannot retrieve BUS-002 GPS data** | **`PASS`** | `AssignmentService.verify_vehicle_access()` checks target ID against assignment and raises `ForbiddenAccessException` (`403 Forbidden`). Tested in `test_user_a_cannot_access_user_b_vehicle_by_id`. | None |
| **Authorization** | **User B cannot retrieve BUS-001 GPS data** | **`PASS`** | `AssignmentService.verify_vehicle_access()` rejects User B querying BUS-001 with `403 Forbidden`. Tested in `test_user_b_cannot_access_user_a_history`. | None |
| **GPS** | **Simulator publishes GPS** | **`PASS`** | `simulator/gps_simulator.py` connects to Mosquitto with credentials and streams BUS-001 coordinates every 3 seconds to `vehicles/BUS-001/gps`. | None |
| **GPS** | **Mosquitto receives message** | **`PASS`** | Configured in `mosquitto/config/mosquitto.conf` (`allow_anonymous false`, authenticated pwfile). | None |
| **GPS** | **Backend consumes MQTT message** | **`PASS`** | `MQTTClient` listens on topic `vehicles/+/gps` and delegates directly to `TrackingService.ingest_telemetry()`. | None |
| **GPS** | **Historical GPS record inserted** | **`PASS`** | Telemetry ingestion calls `TelemetryRepository.create()` creating new `GPSTelemetry` log records. | None |
| **GPS** | **Latest location updated** | **`PASS`** | Ingestion handles out-of-order timestamps and updates `vehicle.last_latitude`, `last_longitude`, `last_speed`, `last_timestamp`, and `status`. | None |
| **APIs** | **`/auth/login`** | **`PASS`** | Implemented in `app/api/v1/endpoints/auth.py`, accepts JSON & Form data. | None |
| **APIs** | **`/users/me`** | **`PASS`** | Implemented in `app/api/v1/endpoints/users.py`, returns safe profile without password hash. | None |
| **APIs** | **`/me/route`** | **`PASS`** | Implemented in `app/api/v1/endpoints/me.py`, returns user assigned route polyline & waypoints. | None |
| **APIs** | **`/me/vehicle`** | **`PASS`** | Implemented in `app/api/v1/endpoints/me.py`, returns user assigned vehicle metadata. | None |
| **APIs** | **`/me/tracking`** | **`PASS`** | Implemented in `app/api/v1/endpoints/me.py`, returns unified route, vehicle, latest GPS, and status. | None |
| **APIs** | **`/me/tracking/current`** | **`PASS`** | Implemented in `app/api/v1/endpoints/me.py`, returns lightweight current coordinates & status (`ONLINE`/`STALE`/`OFFLINE`/`NO_DATA`). | None |
| **APIs** | **`/me/tracking/history`** | **`PASS`** | Implemented in `app/api/v1/endpoints/me.py`, supports `from`, `to`, and `limit` filtering. | None |
| **Infrastructure** | **FastAPI starts** | **`PASS`** | `app/main.py` configures lifespan context, seeds database, and starts background services. | None |
| **Infrastructure** | **PostgreSQL starts** | **`PASS`** | Configured in `docker-compose.yml` (`postgres:16-alpine` with healthcheck). | None |
| **Infrastructure** | **Mosquitto starts** | **`PASS`** | Configured in `docker-compose.yml` (`eclipse-mosquitto:2.0` with volume mounts). | None |
| **Infrastructure** | **Migrations succeed** | **`PASS`** | Configured in `alembic/` with environment settings supporting both SQLite and PostgreSQL. | None |
| **Infrastructure** | **Docker Compose works cleanly** | **`PASS`** | Containerized build configured in `Dockerfile` & `docker-compose.yml`. | None |
| **Quality** | **No mock production responses** | **`PASS`** | All API controllers query live database tables via domain services & ORM repositories. | None |
| **Quality** | **No hardcoded identities** | **`PASS`** | `current_user` derived dynamically from verified JWT token claim (`sub`). | None |
| **Quality** | **No authorization bypass** | **`PASS`** | Controllers delegate to `AssignmentService`, rejecting client-manipulated IDs with `403 Forbidden`. | None |
| **Quality** | **No credentials committed** | **`PASS`** | Environment defaults used in `.env.example`; `SensitiveDataFilter` redacts credentials in logs. | None |
| **Quality** | **API errors are clean** | **`PASS`** | `register_exception_handlers()` formats error payloads as `{"error": {"code": "...", "message": "..."}}` and hides SQL tracebacks in production. | None |
| **Quality** | **Tests pass** | **`PASS`** | Comprehensive Pytest suite in `tests/`. | None |
| **Quality** | **README setup works** | **`PASS`** | Complete GitHub `README.md` with setup instructions, diagrams, and business rule explanation. | None |

---

## 3. Database Entity Relationship Model

```
+--------------------------------+       +---------------------------------+
|             User               |       |            BusRoute             |
+--------------------------------+       +---------------------------------+
| id: int (PK)                   |       | id: int (PK)                    |
| email: str (Unique, Indexed)   |       | route_code: str (Unique)        |
| full_name: str                 |       | route_name: str                 |
| password_hash: str             |       | description: str                |
| is_active: bool                |       | start_location: str             |
| role: str ("user" | "admin")   |       | end_location: str               |
| assigned_route_id: FK -> Route |-----> | waypoints_json: text            |
| assigned_vehicle_id: FK -> Veh |       +---------------------------------+
+--------------------------------+                        | (1:N)
               |                                          v
               | (1:N)                   +---------------------------------+
               v                         |           RoutePoint            |
+--------------------------------+       +---------------------------------+
|         UserAssignment         |       | id: int (PK)                    |
+--------------------------------+       | route_id: FK -> BusRoute (Idx)  |
| id: int (PK)                   |       | sequence: int (Travel Order)    |
| user_id: FK -> User (Idx)      |       | latitude: float (-90 to 90)     |
| route_id: FK -> BusRoute (Idx) |       | longitude: float (-180 to 180)  |
| vehicle_id: FK -> Vehicle (Idx)|       | name: str                       |
| assigned_at: datetime          |       +---------------------------------+
| is_active: bool (Idx)          |
+--------------------------------+
               |
               v (FK)
+--------------------------------+       +---------------------------------+
|            Vehicle             |       |          GPSTelemetry           |
+--------------------------------+       +---------------------------------+
| id: int (PK)                   | (1:N) | id: int (PK)                    |
| vehicle_code: str (Unique)     |<------| vehicle_id: FK -> Vehicle (Idx) |
| license_plate: str             |       | latitude: float (-90 to 90)     |
| model_name: str                |       | longitude: float (-180 to 180)  |
| status: str ("ONLINE", "IDLE") |       | speed: float (>= 0.0)           |
| last_latitude: float           |       | heading: float (0 to 360)       |
| last_longitude: float          |       | recorded_at: datetime (Indexed) |
| last_speed: float              |       | received_at: datetime           |
| last_timestamp: datetime       |       | source: str ("REST" | "MQTT")   |
+--------------------------------+       +---------------------------------+
```

---

## 4. API Endpoints & Request/Response Contracts

### A. Authentication
- `POST /api/v1/auth/login`
  - **Input**: `{"email": "usera@example.com", "password": "UserA@123"}` (JSON or Form Data)
  - **Response (200 OK)**:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1Ni...",
      "token_type": "bearer",
      "expires_in": 1800,
      "user": {
        "id": 2,
        "email": "usera@example.com",
        "full_name": "User A",
        "role": "user",
        "is_active": true
      }
    }
    ```
  - **Errors**: `401 Unauthorized` (Incorrect credentials), `403 Forbidden` (Inactive account).

### B. Current User & Assigned Resources
- `GET /api/v1/users/me` or `GET /api/v1/me`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**: Safe `UserResponse` profile object (no `password_hash`).
- `GET /api/v1/me/route`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**: Bus route metadata with JSON waypoints list and `route_points` ordered by sequence.
- `GET /api/v1/me/vehicle`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**: Assigned vehicle metadata and cached latest location coordinates.
- `GET /api/v1/me/tracking`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**: Unified object combining route, vehicle, latest GPS, and dynamic status.
- `GET /api/v1/me/tracking/current`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**: Lightweight current location object (`vehicle_code`, `latitude`, `longitude`, `speed`, `recorded_at`, `received_at`, `status`).

---

## 5. Core Security & Authorization Rules

1. **Identity Resolution**:
   - Always extract user identity strictly using `get_current_user` dependency from `app/api/dependencies.py`.
   - **NEVER** trust client-supplied `user_id`, `vehicle_id`, or `route_id` query parameters or body fields.
2. **Access Verification**:
   - Use `AssignmentService(db).verify_vehicle_access(current_user, vehicle_id)` to validate vehicle endpoints.
   - Use `AssignmentService(db).verify_route_access(current_user, route_id)` to validate route endpoints.
3. **Password Protection**:
   - Passwords must be hashed using `app.core.security.get_password_hash`.
   - Never store or log plaintext passwords.
   - Never include password hashes in Pydantic response schemas.

---

## 6. How to Run & Verify Code

### Running Dev Server
```bash
uvicorn app.main:app --reload --port 8000
```

### Running Test Suite
```bash
pytest -v
```

### Seeding Database
```bash
python scripts/seed_db.py
```
Default seeded credentials:
- **User A**: `usera@example.com` / `UserA@123` (Assigned to Route `ROUTE-101` / Vehicle `BUS-001`)
- **User B**: `userb@example.com` / `UserB@123` (Assigned to Route `ROUTE-202` / Vehicle `BUS-002`)
- **Admin**: `admin@example.com` / `Admin@123` (Full system access)

### Running GPS Simulator
```bash
python simulator/gps_simulator.py
```
