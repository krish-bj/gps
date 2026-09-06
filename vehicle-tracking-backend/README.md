# Vehicle Tracking Backend (FastAPI + MQTT + PostgreSQL)

Production-grade, asynchronous Python FastAPI backend for real-time GPS fleet tracking, Mosquitto MQTT telemetry ingestion, multi-tenant user access isolation, and transit route management.

- **Live Deployed API**: `https://gps-9ei6.onrender.com/api/v1`
- **Live Health Check**: `https://gps-9ei6.onrender.com/health`
- **Interactive Swagger Docs**: `https://gps-9ei6.onrender.com/docs`

---

## Table of Contents
1. [System Architecture](#1-system-architecture)
2. [Database Design & Entity Relationships](#2-database-design--entity-relationships)
3. [Authentication & Security](#3-authentication--security)
4. [Route & Vehicle Assignment Logic](#4-route--vehicle-assignment-logic)
5. [GPS Data Flow & Dual Ingestion](#5-gps-data-flow--dual-ingestion)
6. [API Endpoints Reference](#6-api-endpoints-reference)
7. [Multi-Vehicle Live Simulator](#7-multi-vehicle-live-simulator)
8. [Setup & Running Guide](#8-setup--running-guide)
9. [Automated Testing Suite](#9-automated-testing-suite)
10. [MQTT Hardware & Production Security Guide](#10-mqtt-hardware--production-security-guide)

---

## 1. System Architecture

The backend implements a clean **Four-Tier Decoupled Architecture**:
`Controller Layer` → `Service Layer` → `Repository Layer` → `Database Layer`

```
                  ┌────────────────────────────────────────────────────────┐
                  │          GPS Fleet Simulator / Hardware Units          │
                  │       (Simulates BUS-001, BUS-002, Heading & Speed)    │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                         ┌────────────────────┴────────────────────┐
                         │                                         │
                         ▼                                         ▼
            ┌─────────────────────────┐               ┌─────────────────────────┐
            │  Eclipse Mosquitto MQTT │               │    REST Ingestion API   │
            │  Broker (Port 1883)     │               │  (POST /api/v1/gps)     │
            │  Auth: pwfile / mTLS    │               │  Auth: X-API-Key/Bearer │
            └────────────┬────────────┘               └────────────┬────────────┘
                         │                                         │
                         │ Background MQTT Thread                  │
                         └────────────────────┬────────────────────┘
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FastAPI Backend Service                                 │
│                                                                                          │
│  • Controllers (app/api/v1/endpoints/): Thin routers, zero business logic or raw SQL     │
│  • Services (app/services/): AuthService, TrackingService, AssignmentService             │
│  • Repositories (app/repositories/): Data persistence queries for User, Route, Vehicle   │
│  • Middleware: CORS, Security Headers, 2MB Request Size Cap, Sensitive Data Scrubbing   │
│  • Real-Time Cache: Instant single-query latest location responses                       │
└─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │
                                              ▼
                                   ┌─────────────────────┐
                                   │ PostgreSQL 16 DB /  │
                                   │ SQLite Development  │
                                   │ (SQLAlchemy 2.0 ORM)│
                                   └─────────────────────┘
```

### Key Structural Highlights
- **Thin Controllers**: All endpoints in `app/api/v1/endpoints/` delegate execution to domain services.
- **Repository Pattern**: `UserRepository`, `RouteRepository`, `VehicleRepository`, and `TelemetryRepository` isolate all SQLAlchemy operations.
- **Unified Service Layer**: `TrackingService` handles multi-vehicle tracking, coordinate caching, dynamic status calculation (`ONLINE`, `STALE`, `OFFLINE`), and access verification.

---

## 2. Database Design & Entity Relationships

The data layer uses **SQLAlchemy 2.0** with type-safe `Mapped[...]` attributes.

```
   ┌───────────────────────────────────┐
   │               User                │
   ├───────────────────────────────────┤
   │ id: int (PK)                      │
   │ email: str (Unique, Index)        │
   │ full_name: str                    │
   │ hashed_password: str              │
   │ is_active: bool (Default: True)   │
   │ role: str ('user' | 'admin')      │
   │ assigned_route_id: int (FK) ──────┼──────┐
   │ assigned_vehicle_id: int (FK) ────┼──┐   │
   │ created_at: datetime              │  │   │
   │ updated_at: datetime              │  │   │
   └───────────────────────────────────┘  │   │
                                          │   │
   ┌───────────────────────────────────┐  │   │
   │             BusRoute              │  │   │
   ├───────────────────────────────────┤  │   │
   │ id: int (PK) <────────────────────┼──┼───┘
   │ route_code: str (Unique, Index)   │  │
   │ route_name: str                   │  │
   │ description: str                  │  │
   │ start_location: str               │  │
   │ end_location: str                 │  │
   │ waypoints_json: text (JSON Array) │  │
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
   │ model_name: str                   │
   │ status: str ('ONLINE'|'OFFLINE')  │
   │ assigned_route_id: int (FK)       │
   │ last_latitude: float (Cached)     │
   │ last_longitude: float (Cached)    │
   │ last_speed: float (Cached)        │
   │ last_timestamp: datetime (Cached) │
   │ created_at: datetime              │
   └─────────────────┬─────────────────┘
                     │
                     │ 1:N
                     ▼
   ┌───────────────────────────────────┐
   │           GPSTelemetry            │
   ├───────────────────────────────────┤
   │ id: int (PK)                      │
   │ vehicle_id: int (FK, Index)       │
   │ latitude: float (-90 to 90)       │
   │ longitude: float (-180 to 180)    │
   │ speed: float (km/h, >= 0)         │
   │ heading: float (Degrees 0-360)    │
   │ recorded_at: datetime (Index)     │
   │ received_at: datetime             │
   │ source: str ('MQTT' | 'REST')     │
   └───────────────────────────────────┘
```

### Relational Integrity & Performance Optimizations
1. **Foreign Key Constraints & Cascades**:
   - `User.assigned_route_id` references `bus_routes.id`.
   - `User.assigned_vehicle_id` references `vehicles.id`.
   - `GPSTelemetry.vehicle_id` references `vehicles.id` with `ondelete="CASCADE"`.
2. **Composite Indexes**:
   - `idx_user_active_assignment` on `(user_id, is_active)` for O(1) assignment lookups.
   - `idx_vehicle_timestamp` on `(vehicle_id, recorded_at)` for fast historical telemetry filtering.
3. **Cached Coordinates on Vehicle Table**:
   - Ingesting a coordinate automatically updates `Vehicle.last_latitude`, `last_longitude`, `last_speed`, and `last_timestamp`.
   - Single-vehicle latest queries return immediately without performing a table scan on the high-frequency telemetry log.

---

## 3. Authentication & Security

### 3.1 OAuth2 Password Bearer & JWT Token Lifecycle
- **Password Hashing**: Bcrypt with automatic salt generation (`passlib.context.CryptContext`).
- **Token Format**: Standard JSON Web Token (JWT) signed with `HS256`.
- **Claims**:
  - `sub`: User ID integer (primary subject claim).
  - `iat`: Issued at UTC timestamp.
  - `exp`: Expiration UTC timestamp (default: 7 days / 10080 minutes).
- **Authentication Endpoint**: `POST /api/v1/auth/login` (supports JSON or OAuth2 form-data).

### 3.2 Security Hardening
- **Sensitive Data Scrubbing**: Custom logging filter (`SensitiveDataFilter`) masks database passwords, JWT tokens, and API keys.
- **Request Size Limiting**: `ContentLengthLimitMiddleware` enforces a strict 2MB body limit to prevent memory-exhaustion attacks.
- **CORS Protection**: Explicit origins and methods allowed (`GET`, `POST`, `OPTIONS`).

---

## 4. Route & Vehicle Assignment Logic

### 4.1 Strict Multi-Tenant Authorization
All access control is strictly enforced in the backend dependencies (`app/api/dependencies.py`):
1. **Never Trust Client-Provided IDs**: Endpoints like `GET /me/route`, `GET /me/vehicle`, and `GET /me/tracking/current` extract identity **exclusively** from the verified JWT `sub` claim.
2. **Cross-User Access Guards**:
   - When a user accesses an explicit resource (e.g., `GET /api/v1/vehicles/{vehicle_id}`), `AssignmentService.verify_vehicle_access()` validates that `vehicle_id == user.assigned_vehicle_id` (unless user role is `admin`).
   - If an unauthorized access attempt occurs (e.g. User A requesting User B's vehicle `2`), the API rejects it with **HTTP 403 Forbidden**.

### 4.2 Seed Accounts & Assignments

| Role | Email | Password | Assigned Route | Assigned Vehicle |
| :--- | :--- | :--- | :--- | :--- |
| **User A** | `usera@example.com` | `user123` | Route A (`ROUTE-101`) | BUS-001 (`BUS-001`) |
| **User B** | `userb@example.com` | `user123` | Route B (`ROUTE-202`) | BUS-002 (`BUS-002`) |
| **Admin** | `admin@example.com` | `admin123` | All Routes | All Vehicles |

---

## 5. GPS Data Flow & Dual Ingestion

```
[ Vehicle GPS Unit / Simulator ]
         │
         ├── 1. Publish MQTT frame to `vehicles/{vehicle_code}/gps`
         │   (Mosquitto Broker: Port 1883, Auth: pwfile)
         │   OR
         └── 2. HTTP POST fallback to `/api/v1/gps`
             (Header: `X-API-Key: dev_gps_ingest_secret_key_2026`)
                     │
                     ▼
             [ FastAPI Backend ]
                     │
                     ├── Validate payload bounds (-90 <= lat <= 90, speed >= 0)
                     ├── Atomic INSERT into `gps_telemetry` table
                     ├── Atomic UPDATE cached last coordinates on `vehicles` table
                     └── Compute dynamic vehicle status (ONLINE / STALE / OFFLINE)
```

- **Dynamic Status Thresholds**:
  - `ONLINE`: Last telemetry timestamp received within **30 seconds**.
  - `STALE`: Last telemetry timestamp between **30 and 120 seconds**.
  - `OFFLINE`: No telemetry for over **120 seconds**.

---

## 6. API Endpoints Reference

Base URL: `http://localhost:8000/api/v1` (or `https://gps-9ei6.onrender.com/api/v1`)

### 6.1 Authentication

#### `POST /auth/login` & `POST /auth/login/json`
- **Request Body**:
  ```json
  {
    "email": "usera@example.com",
    "password": "user123"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 604800,
    "user": {
      "id": 2,
      "email": "usera@example.com",
      "full_name": "User A [DEV DEMO]",
      "role": "user",
      "is_active": true,
      "assigned_route_id": 1,
      "assigned_vehicle_id": 1
    }
  }
  ```

### 6.2 User & Profile

#### `GET /users/me`
- **Auth**: `Bearer <token>`
- Returns current safe user profile. Never exposes password hash.

### 6.3 Assigned Route & Tracking

#### `GET /me/route`
- Returns assigned route metadata and parsed waypoint stops for the authenticated user.

#### `GET /me/vehicle`
- Returns assigned vehicle metadata and cached latest location.

#### `GET /me/tracking`
- Returns unified summary: assigned route, vehicle, latest GPS coordinate, and derived vehicle status.

#### `GET /me/tracking/current`
- Lightweight polling endpoint for live map tracking.
- **Response** (`200 OK`):
  ```json
  {
    "vehicle_code": "BUS-001",
    "latitude": 12.971858,
    "longitude": 77.594672,
    "speed": 38.5,
    "heading": 292.6,
    "recorded_at": "2026-09-06T01:27:03Z",
    "received_at": "2026-09-06T01:27:03.123456Z",
    "status": "ONLINE"
  }
  ```

#### `GET /me/tracking/history`
- Returns historical GPS coordinate breadcrumbs for the assigned vehicle.
- Query parameters: `from` (ISO datetime), `to` (ISO datetime), `limit` (1–1000).

### 6.4 Telemetry Ingestion

#### `POST /gps`
- **Auth**: `X-API-Key: dev_gps_ingest_secret_key_2026` or Bearer JWT token.
- **Request Body**:
  ```json
  {
    "vehicle_code": "BUS-001",
    "latitude": 12.971858,
    "longitude": 77.594672,
    "speed": 38.5,
    "heading": 292.6,
    "timestamp": "2026-09-06T01:27:03Z"
  }
  ```
- **Response**: `201 Created`

### 6.5 Live WebSocket Stream (Bonus)

#### `WS /ws/tracking?token=<JWT_TOKEN>`
- Connect via WebSocket client to receive live vehicle coordinate frames pushed every 3 seconds.

---

## 7. Multi-Vehicle Live Simulator

The simulator (`simulator/gps_simulator.py`) simulates realistic transit vehicles traveling along routes:
- **Concurrent Multi-Vehicle Tracking**: Simulates **both** `BUS-001` (Downtown Express) and `BUS-002` (Uptown Shuttle) simultaneously.
- **Dynamic Compass Bearing**: Computes compass heading (0°–360°) using great-circle bearing between waypoints.
- **Speed Physics**: Interpolates movement based on realistic city driving speeds (35–50 km/h) and interval timing (3.0s).

```bash
# Run simulator targeting local environment
python simulator/gps_simulator.py

# Run simulator targeting live Render deployment
REST_API_URL="https://gps-9ei6.onrender.com/api/v1/gps" python simulator/gps_simulator.py
```

---

## 8. Setup & Running Guide

### Option A: Local Python & Zero-Config SQLite

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Seed development database
python -m scripts.seed_db

# 3. Start development server
uvicorn app.main:app --reload --port 8000
```
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Docker Compose (PostgreSQL 16 + Mosquitto + FastAPI)

```bash
docker-compose up --build
```
Starts:
- **PostgreSQL 16** on port `5432`
- **Mosquitto MQTT Broker** on port `1883`
- **FastAPI Backend Service** on port `8000`

---

## 9. Automated Testing Suite

The Pytest suite verifies authentication, authorization scope guards, telemetry ingestion, caching, and cross-user security proofs:

```bash
python -m pytest
```
Output:
```
======================== 29 passed, 1 warning in 5.74s ========================
```

Key test files:
- `test_cross_user_security_proof.py`: Verifies that User A cannot access User B's vehicle, route, coordinates, or history (asserts HTTP 403 Forbidden).
- `test_me_endpoints.py`: Verifies `/me/route`, `/me/vehicle`, and `/me/tracking` user isolation.
- `test_auth.py`: Tests login, token issuance, and password security.
- `test_telemetry.py`: Verifies coordinate validation, ingestion, and history queries.

---

## 10. MQTT Hardware & Production Security Guide

### Assessment Implementation
- Mosquitto MQTT broker requires authentication (`allow_anonymous false`).
- Password file authentication via `/mosquitto/config/pwfile`.
- FastAPI Paho-MQTT consumer connects with `MQTT_USERNAME` and `MQTT_PASSWORD`.

### Production Hardware Tracker Deployment
In enterprise fleet deployments, hardware devices authenticate using:
1. **X.509 Mutual TLS (mTLS) Client Certificates**:
   - Each hardware unit has a private key stored inside a tamper-resistant **Secure Element (ATECC608 / TPM)** and a certificate signed by the company's internal Certificate Authority (CA).
   - Mosquitto verifies the client certificate on port 8883 (MQTTS) and extracts `vehicle_code` from the certificate `Common Name` (`CN=BUS-001`), eliminating spoofing.
2. **Mosquitto Access Control Lists (ACLs)**:
   - Restricts each vehicle to publishing strictly to its own topic (`vehicles/BUS-001/gps`), while the backend consumer is granted read access to `vehicles/+/gps`.
