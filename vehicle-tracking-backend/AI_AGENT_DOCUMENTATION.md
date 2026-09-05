# GPS Vehicle Tracking Backend — AI Agent Technical Documentation

> **Target Audience**: AI Coding Assistants & Automated Developers  
> **Repository Path**: `vehicle-tracking-backend/`  
> **Primary Stack**: Python 3.12, FastAPI, SQLAlchemy 2.0 (Declarative Base & Mapped Columns), Pydantic V2, Alembic, Pytest, PyJWT, Bcrypt, Mosquitto MQTT.

---

## 1. System Architecture & Folder Layout

The project follows a **Clean Modular Layered Architecture**. Controllers (API endpoints) contain **zero business logic** and delegate directly to dedicated service classes and data repositories.

```
vehicle-tracking-backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # Reusable FastAPI dependencies (JWT Auth, Admin check, Assignment Auth)
│   │   └── v1/
│   │       ├── router.py            # Central v1 API router (/api/v1)
│   │       └── endpoints/
│   │           ├── auth.py          # Login API (/auth/login)
│   │           ├── me.py            # Current User, Assigned Route & Vehicle (/me, /me/route, /me/vehicle)
│   │           ├── users.py         # User management (/users, /users/me)
│   │           ├── routes.py        # Route endpoints (/routes, /routes/{id})
│   │           ├── vehicles.py      # Vehicle endpoints (/vehicles, /vehicles/{id})
│   │           └── telemetry.py     # Real-time GPS ingestion & history (/gps/telemetry)
│   ├── core/
│   │   ├── config.py                # Pydantic Settings with production fail-fast validations & secret masking
│   │   └── security.py              # Bcrypt password hashing/verification & JWT encoding/decoding
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy 2.0 DeclarativeBase
│   │   └── session.py               # Engine configuration (pool_pre_ping=True) & get_db generator
│   ├── models/
│   │   └── models.py                # SQLAlchemy 2.0 Mapped Entities (User, BusRoute, RoutePoint, Vehicle, UserAssignment, GPSTelemetry)
│   ├── schemas/
│   │   ├── user.py                  # User schemas excluding password hashes (UserResponse)
│   │   ├── route_point.py           # RoutePoint schemas with coordinate validation
│   │   ├── user_assignment.py       # UserAssignment schemas
│   │   └── schemas.py               # Token, BusRouteResponse, VehicleResponse, GPSTelemetryResponse schemas with @computed_field
│   ├── repositories/
│   │   ├── user_repository.py       # DB access for User entities
│   │   ├── route_repository.py      # DB access for BusRoute & RoutePoint entities
│   │   ├── vehicle_repository.py    # DB access for Vehicle entities
│   │   └── telemetry_repository.py  # DB access for GPSTelemetry logs
│   ├── services/
│   │   ├── auth_service.py          # Authentication & token issue logic
│   │   ├── assignment_service.py    # Single source of truth for user active assignments & authorization
│   │   ├── tracking_service.py      # Telemetry processing & route/vehicle access verification
│   │   ├── seed_service.py          # Initial database seeding
│   │   └── seed_data.py             # Default initial seed data (Users, Routes, Vehicles)
│   ├── exceptions/
│   │   └── custom_exceptions.py     # Custom exception domain model mapped to HTTP status codes
│   ├── mqtt/
│   │   └── client.py                # Mosquitto MQTT subscriber listening on telemetry topics
│   ├── utils/
│   │   └── helpers.py               # Helper utilities (JSON parsing, coordinate math)
│   └── main.py                      # FastAPI lifespan setup, exception handlers, CORS & health check
├── alembic/                         # Alembic database migration scripts
├── scripts/
│   └── seed_db.py                   # Command-line database seed script
├── tests/                           # Pytest automated test suite (38 test cases)
└── pytest.ini                       # Pytest configuration
```

---

## 2. Completed Phases Summary

| Phase | Title | Description & Implementation Details | Key Files |
| :--- | :--- | :--- | :--- |
| **Phase A** | Requirement Analysis | Analyzed requirements for multi-user GPS tracking system with strict authorization rules. | `backend_assessment_analysis.md` |
| **Phase B & C** | Project Bootstrap & Config | Built FastAPI structure with `Pydantic Settings` for env validation (`DATABASE_URL`, `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`). | `app/core/config.py` |
| **Phase D** | Database Foundation | Implemented SQLAlchemy 2.0 engine with connection pooling and session lifecycle handling (`get_db`). | `app/db/session.py` |
| **Phase E & F** | Core Domain & Route Geometry | Defined `User`, `BusRoute`, `RoutePoint` (ordered by `sequence`), `Vehicle`, `UserAssignment`, and `GPSTelemetry` entities. | `app/models/models.py` |
| **Phase G** | User Assignment Model | Created 1-to-1 active assignment relationship linking `User`, `BusRoute`, and `Vehicle`. | `app/models/models.py` |
| **Phase J** | Database Migrations | Generated Alembic initial schema migration (`001_initial_schema.py`). | `alembic/versions/` |
| **Phase K & L** | Password & JWT Security | Implemented `bcrypt` password hashing and JWT token creation/decoding (`sub=user_id`). Implemented `get_current_user` dependency. | `app/core/security.py`, `app/api/dependencies.py` |
| **Phase M** | Authentication API | Built `POST /api/v1/auth/login` supporting JSON & Form data. Returns `access_token`, `token_type`, `expires_in`, and safe `user` profile without password leakage. | `app/services/auth_service.py`, `app/api/v1/endpoints/auth.py` |
| **Phase N** | Authorization Service | Built `AssignmentService` as single source of truth. Validates client access against assigned vehicle/route, raising HTTP 403 on mismatch. | `app/services/assignment_service.py`, `app/api/dependencies.py` |
| **Phase O** | Current User API | Built `GET /api/v1/users/me` & `GET /api/v1/me`. Requires valid JWT, excludes password hash, denies inactive users (HTTP 403). | `app/api/v1/endpoints/me.py`, `app/api/v1/endpoints/users.py` |
| **Phase P** | Assigned Route API | Built `GET /api/v1/me/route` & `GET /api/v1/users/me/route`. Returns only authenticated user's assigned route with points in sequence travel order. | `app/api/v1/endpoints/me.py` |
| **Phase Q** | Assigned Vehicle API | Built `GET /api/v1/me/vehicle` & `GET /api/v1/users/me/vehicle`. Returns assigned vehicle with `registration_number`, `display_name`, and `status`. | `app/api/v1/endpoints/me.py`, `app/schemas/schemas.py` |

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
  - **Input**: `{"email": "usera@example.com", "password": "user123"}` (JSON or Form Data)
  - **Response (200 OK)**:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1Ni...",
      "token_type": "bearer",
      "expires_in": 604800,
      "user": {
        "id": 2,
        "email": "usera@example.com",
        "full_name": "User A",
        "role": "user",
        "is_active": true,
        "assigned_route_id": 1,
        "assigned_vehicle_id": 1
      }
    }
    ```
  - **Errors**: `401 Unauthorized` (Incorrect credentials), `403 Forbidden` (Inactive account).

### B. Current User & Assigned Resources
- `GET /api/v1/me` or `GET /api/v1/users/me`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**: Safe `UserResponse` profile object (no `password_hash`).
- `GET /api/v1/me/route` or `GET /api/v1/users/me/route`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**:
    ```json
    {
      "id": 1,
      "route_code": "ROUTE-101",
      "route_name": "Route A - Downtown Express",
      "name": "Route A - Downtown Express",
      "description": "Express route linking Downtown Hub to North Terminal",
      "start_location": "Downtown Hub",
      "end_location": "North Terminal",
      "waypoints": [...],
      "route_points": [
        {"id": 1, "route_id": 1, "sequence": 1, "latitude": 37.7749, "longitude": -122.4194, "name": "Stop 1"},
        {"id": 2, "route_id": 1, "sequence": 2, "latitude": 37.7833, "longitude": -122.4167, "name": "Stop 2"}
      ]
    }
    ```
- `GET /api/v1/me/vehicle` or `GET /api/v1/users/me/vehicle`
  - **Header**: `Authorization: Bearer <token>`
  - **Response (200 OK)**:
    ```json
    {
      "id": 1,
      "vehicle_code": "BUS-001",
      "license_plate": "BUS-1001-PLATE",
      "registration_number": "BUS-1001-PLATE",
      "model_name": "Standard Transit Bus",
      "display_name": "Standard Transit Bus",
      "status": "ONLINE",
      "assigned_route_id": 1,
      "last_latitude": 37.7749,
      "last_longitude": -122.4194,
      "last_speed": 0.0,
      "last_timestamp": "2026-09-05T13:42:00Z"
    }
    ```

### C. Protected Vehicle Tracking
- `GET /api/v1/vehicles/{vehicle_id}`
- `GET /api/v1/vehicles/{vehicle_id}/location/latest`
- `GET /api/v1/vehicles/{vehicle_id}/location/history?limit=100`
  - **Authorization**: User A attempting to request User B's vehicle ID receives `403 Forbidden`. Admins can query any vehicle.

---

## 5. Security & Authorization Rules (For AI Agents)

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

## 6. How to Run & Verify Code (For AI Agents)

### Running Dev Server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Test Suite
```bash
pytest -v
```
*Current test suite status*: **38 / 38 tests passing**.

### Seeding Database
```bash
python -m scripts.seed_db
```
Default seeded credentials:
- **User A**: `usera@example.com` / `user123` (Assigned to Route `ROUTE-101` / Vehicle `BUS-001`)
- **User B**: `userb@example.com` / `user123` (Assigned to Route `ROUTE-202` / Vehicle `BUS-002`)
- **Admin**: `admin@example.com` / `admin123` (Full system access)

---

## 7. Next Architectural Steps

When continuing development (e.g., building Flutter mobile app integration or extending GPS telemetry features):
1. Use `AssignmentService` whenever adding new driver tracking endpoints.
2. Maintain standard exception handling with `VehicleTrackingException` hierarchy.
3. Ensure all incoming Pydantic schemas enforce bounds on coordinates (`latitude`: -90 to 90, `longitude`: -180 to 180, `speed`: >= 0).
