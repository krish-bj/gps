# GPS Vehicle Tracking & Fleet Management System

A production-grade, full-stack GPS vehicle tracking and fleet management platform featuring a Python FastAPI backend, PostgreSQL & SQLite database layers, Eclipse Mosquitto MQTT telemetry ingestion, a multi-vehicle live GPS movement simulator, and a cross-platform Flutter client app (Mobile, Web, Desktop).

---

## Table of Contents
1. [System Architecture](#1-system-architecture)
2. [Technology Stack](#2-technology-stack)
3. [Repository Layout & Core Modules](#3-repository-layout--core-modules)
4. [Database Design & Entity Relationships](#4-database-design--entity-relationships)
5. [Demo Credentials & Seed Data](#5-demo-credentials--seed-data)
6. [Authentication & Strict Authorization](#6-authentication--strict-authorization)
7. [GPS Telemetry Ingestion & Live Simulator](#7-gps-telemetry-ingestion--live-simulator)
8. [MQTT Security & Production Hardware Guide](#8-mqtt-security--production-hardware-guide)
9. [API Contract & Integration Specification](#9-api-contract--integration-specification)
10. [Flutter Client Application](#10-flutter-client-application)
11. [Environment Variables Reference](#11-environment-variables-reference)
12. [Setup & Execution Guide](#12-setup--execution-guide)
13. [Automated Testing Suite](#13-automated-testing-suite)
14. [Production Readiness Checklist](#14-production-readiness-checklist)

---

## 1. System Architecture

The platform uses a decoupled four-tier architecture (`Controller` → `Service` → `Repository` → `Database`) designed for low-latency GPS ingestion, strict data isolation, and real-time query performance.

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
│  • Middleware: CORS, Security Headers, Request Size Limits (2MB), Scrubbed Logging       │
│  • Auth Engine: OAuth2 Bearer, PyJWT (HS256), Bcrypt Password Hashing                    │
│  • Authorization Scope Guards: Strict multi-tenant vehicle & route access isolation     │
│  • Real-Time Query Cache: Instant single-query latest location responses                 │
│  • Optional Bonus WebSocket: Live real-time streaming endpoint (/ws/tracking)            │
└───────────────────────────────┬───────────────────────────────┬──────────────────────────┘
                                │                               │
                                ▼                               ▼
                     ┌─────────────────────┐         ┌─────────────────────┐
                     │ PostgreSQL 16 DB /  │         │ Flutter Client App  │
                     │ SQLite Development  │         │ (Live Map, Heading, │
                     │ (SQLAlchemy 2.0 ORM)│         │  Route Isolation)   │
                     └─────────────────────┘         └─────────────────────┘
```

### Architecture Guarantees
- **Separation of Concerns**: Controllers are thin and contain zero SQL queries or business logic. All database access is channeled through dedicated repositories, and business workflows are isolated in services.
- **Strict Backend Authorization**: Client-provided IDs (`vehicle_id`, `route_id`) are never trusted. All access checks are enforced by backend assignment lookup. Unauthorized access attempts immediately return **HTTP 403 Forbidden**.
- **Dual Ingestion**: Supports high-throughput REST HTTP ingestion (`POST /api/v1/gps`) and Mosquitto MQTT telemetry subscriptions (`vehicles/+/gps`).
- **Dynamic Vehicle Status**: Dynamically calculates vehicle status (`ONLINE`, `STALE`, `OFFLINE`, `NO_DATA`) based on configurable timestamp thresholds.

---

## 2. Technology Stack

### Backend
- **Framework**: Python 3.12+ with FastAPI (Async ASGI) & Uvicorn
- **ORM**: SQLAlchemy 2.0 (Declarative Base & Type-Annotated `Mapped[...]` columns)
- **Database**: PostgreSQL 16 (Production / Docker) & SQLite (Zero-Config Development & Testing)
- **Migrations**: Alembic
- **Validation**: Pydantic V2 & `pydantic-settings`
- **Security**: OAuth2 Bearer, PyJWT, Bcrypt (`passlib`)
- **Messaging**: Eclipse Mosquitto MQTT & Paho-MQTT 2.0+ Client
- **Testing**: Pytest, HTTPX Async Client, Pytest-Asyncio

### Frontend (Mobile / Web)
- **Framework**: Flutter 3.x / Dart 3.x
- **State Management**: Provider (`ChangeNotifier`)
- **Mapping Engine**: `flutter_map` with CartoDB Voyager & Dark basemaps
- **Polyline & Geometry**: `latlong2`
- **Network**: HTTP Client with centralized `ApiService` and persistent JWT token storage (`shared_preferences`)

---

## 3. Repository Layout & Core Modules

```
task/
├── mobile_app/                       # Cross-Platform Flutter Client App
│   ├── lib/
│   │   ├── core/                     # Constants, App Colors, Network ApiService, Parse Utils
│   │   ├── models/                   # Dart Data Models (User, Route, Vehicle, Telemetry)
│   │   ├── providers/                # AuthProvider, TrackingProvider, HistoryProvider
│   │   ├── screens/                  # LoginScreen, MapTrackingScreen, HistoryScreen, ProfileScreen
│   │   ├── widgets/                  # BusMarkerWidget (rotates with heading), StopMarkerWidget
│   │   └── main.dart                 # Flutter App Entrypoint & Route Configuration
│   ├── test/                         # Flutter Unit & Widget Tests (LoginScreen, App Initialization)
│   └── pubspec.yaml                  # Flutter Dependencies Spec
├── vehicle-tracking-backend/         # FastAPI Backend Service
│   ├── alembic/                      # Alembic Database Migrations
│   ├── app/
│   │   ├── api/                      # API Layer
│   │   │   ├── dependencies.py       # Reusable FastAPI dependencies (JWT Auth, Scope Guards)
│   │   │   └── v1/
│   │   │       ├── router.py         # Main v1 Router
│   │   │       └── endpoints/        # Controllers (auth, me, routes, vehicles, telemetry, ws)
│   │   ├── core/                     # Config (pydantic-settings), Security, Logging, Middleware
│   │   ├── db/                       # SQLAlchemy 2.0 Engine & Session Generators
│   │   ├── exceptions/               # Centralized Custom Exceptions & Handlers
│   │   ├── models/                   # SQLAlchemy 2.0 Entities (User, BusRoute, Vehicle, Telemetry)
│   │   ├── repositories/             # Data Access Repositories (User, Route, Vehicle, Telemetry)
│   │   ├── schemas/                  # Pydantic V2 Validation & Serialization Schemas
│   │   ├── services/                 # Business Logic (AuthService, TrackingService, AssignmentService)
│   │   └── main.py                   # FastAPI Application Lifespan & Middleware Mounting
│   ├── scripts/
│   │   └── seed_db.py                # Idempotent Database Seeder CLI
│   ├── simulator/
│   │   ├── gps_simulator.py          # Multi-Vehicle GPS Simulator (BUS-001 & BUS-002)
│   │   └── requirements.txt
│   ├── tests/                        # Comprehensive Pytest Test Suite
│   ├── Dockerfile                    # Containerization Build Spec
│   ├── docker-compose.yml            # Multi-container Compose Spec (PostgreSQL + MQTT + API)
│   ├── mosquitto.conf                # Mosquitto Broker Configuration
│   ├── mosquitto_pwfile              # MQTT Password File
│   ├── requirements.txt              # Python Dependencies
│   └── start.sh                      # Production Container Startup Script
├── render.yaml                       # Render Infrastructure-as-Code Deployment Blueprint
└── README.md                         # Unified Documentation (This File)
```

---

## 4. Database Design & Entity Relationships

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

### Relational Mapping
1. **User → BusRoute**: `User.assigned_route_id` references `bus_routes.id`. Regular users can only access their assigned route.
2. **User → Vehicle**: `User.assigned_vehicle_id` references `vehicles.id`. Regular users can only access their assigned vehicle telemetry.
3. **BusRoute → Vehicle**: `Vehicle.assigned_route_id` references `bus_routes.id`. Multiple vehicles can service the same route.
4. **Vehicle → GPSTelemetry**: `GPSTelemetry.vehicle_id` references `vehicles.id`. Stores chronological GPS logs (`cascade="all, delete-orphan"`).
5. **Cached Coordinates on Vehicle**: Whenever a telemetry point is ingested, `Vehicle.last_latitude`, `last_longitude`, `last_speed`, and `last_timestamp` are updated atomically in the database transaction. This provides sub-millisecond latest location queries without scanning the telemetry log table.

---

## 5. Demo Credentials & Seed Data

The database includes an idempotent seeder (`scripts/seed_db.py`). Running it multiple times will not create duplicate records.

### Development Accounts

| Role | Email | Password | Assigned Route | Assigned Vehicle | Access Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **User A** | `usera@example.com` | `user123` | Route A (`ROUTE-101`) | BUS-001 (`BUS-001`) | Strictly Route A & BUS-001 |
| **User B** | `userb@example.com` | `user123` | Route B (`ROUTE-202`) | BUS-002 (`BUS-002`) | Strictly Route B & BUS-002 |
| **Admin** | `admin@example.com` | `admin123` | All Routes | All Vehicles | System-wide fleet access |

*Passwords are hashed with Bcrypt.*

### Predefined Routes & Waypoints

#### Route A — Downtown Express Line (`ROUTE-101`)
- **Start**: Downtown Hub (`12.971598, 77.594562`)
- **End**: North Terminal (`12.992000, 77.620000`)
- **Assigned Vehicle**: `BUS-001` (`KA-01-EA-1001`)
- **Waypoints**:
  1. Stop 1: Downtown Hub (`12.971598, 77.594562`)
  2. Stop 2: City Center (`12.975000, 77.599000`)
  3. Stop 3: Commercial Zone (`12.980000, 77.605000`)
  4. Stop 4: Tech Hub East (`12.986000, 77.612000`)
  5. Stop 5: North Terminal (`12.992000, 77.620000`)

#### Route B — Uptown Shuttle (`ROUTE-202`)
- **Start**: South Terminal (`12.930000, 77.580000`)
- **End**: Central Plaza (`12.970000, 77.600000`)
- **Assigned Vehicle**: `BUS-002` (`KA-02-EA-2002`)
- **Waypoints**:
  1. Stop 1: South Terminal (`12.930000, 77.580000`)
  2. Stop 2: University Gate (`12.940000, 77.585000`)
  3. Stop 3: Hospital Square (`12.950000, 77.590000`)
  4. Stop 4: Metro Interchange (`12.960000, 77.595000`)
  5. Stop 5: Central Plaza (`12.970000, 77.600000`)

To manually run the seeder:
```bash
python -m scripts.seed_db
```

---

## 6. Authentication & Strict Authorization

### 6.1 Authentication Flow

```
Client (Flutter / HTTP)                  FastAPI Backend                       Database
       │                                       │                                  │
       │─── POST /api/v1/auth/login ──────────>│                                  │
       │    {"email": "...", "password": "..."}│─── Query User by Email ─────────>│
       │                                       │<── Return User Record ───────────│
       │                                       │                                  │
       │                                       │── Verify Bcrypt Password         │
       │                                       │   Generate JWT (sub: user.id)    │
       │<── 200 OK Token Response ─────────────│                                  │
       │    (access_token, token_type, user)   │                                  │
```

### 6.2 Scope Guard & User Isolation Flow

All vehicle and route endpoints enforce backend authorization checks:

```
Client Request                            FastAPI Dependency                     Decision
       │                                (verify_vehicle_access)                      │
       │─── GET /api/v1/vehicles/2 ───────────>│                                     │
       │    Header: Bearer <User A Token>      │── Decode JWT Token (User A)         │
       │                                       │   Get User A assigned_vehicle_id: 1 │
       │                                       │   Check vehicle_id 2 == 1           │
       │                                       │                                     │
       │                                       ├─── If ID != assigned ───────────────► HTTP 403 Forbidden!
       │                                       └─── If ID == assigned or Admin ──────► 200 OK (Data Returned)
```

- If **User A** calls `GET /api/v1/vehicles/2` or `GET /api/v1/routes/2` (User B's assets), the API immediately aborts with **HTTP 403 Forbidden**.
- Client-provided vehicle or route parameters are never trusted. The `/me/tracking`, `/me/route`, `/me/vehicle`, and `/me/tracking/current` endpoints resolve vehicle and route purely from the authenticated user's JWT identity.

---

## 7. GPS Telemetry Ingestion & Live Simulator

### 7.1 Dual Telemetry Ingestion

1. **MQTT Telemetry Ingestion**:
   - Background Paho-MQTT consumer runs alongside FastAPI.
   - Listens on `vehicles/+/gps` (or `vehicles/+/telemetry`).
   - Authenticated against Mosquitto with configurable credentials (`MQTT_USERNAME`, `MQTT_PASSWORD`).
   - When received, parses coordinates, validates bounds (-90 to 90, -180 to 180, speed >= 0), updates the vehicle cache, and logs to `gps_telemetry`.
2. **REST API Ingestion Fallback**:
   - Endpoint: `POST /api/v1/gps` (or legacy `POST /api/v1/gps/telemetry`).
   - Protected by `X-API-Key: dev_gps_ingest_secret_key_2026` or a valid Bearer token.
   - Payload:
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

### 7.2 Multi-Vehicle Live Simulator

The simulator (`simulator/gps_simulator.py`) simulates realistic transit vehicle movement along predefined routes:
- **Concurrent Multi-Vehicle Execution**: Simulates **both** `BUS-001` (Downtown Express) and `BUS-002` (Uptown Shuttle) simultaneously.
- **Dynamic Compass Bearing**: Computes the exact compass heading angle (0° to 360°) using great-circle bearing between waypoints so vehicle icons rotate in the direction of travel.
- **Physical Distance Step Interpolation**: Advances vehicles along route segments based on elapsed time and current speed (35–50 km/h).
- **Auto Fallback**: Attempts MQTT connection first; automatically falls back to HTTP REST ingestion if the MQTT broker is unreachable.

To run the simulator locally:
```bash
# Simulates all configured vehicles (BUS-001 and BUS-002)
python simulator/gps_simulator.py

# Or target a specific remote server
REST_API_URL="https://gps-9ei6.onrender.com/api/v1/gps" python simulator/gps_simulator.py
```

---

## 8. MQTT Security & Production Hardware Guide

### Assessment Security Implementation
In the Docker environment, Mosquitto enforces password authentication:
- `allow_anonymous false` in `mosquitto.conf`.
- Passwords stored in encrypted format via `mosquitto_pwfile`.
- FastAPI consumer authenticates using `MQTT_USERNAME` and `MQTT_PASSWORD`.

### Enterprise Production Hardware Guide
In real-world transit fleet deployments, hardware devices authenticate using:

1. **X.509 Mutual TLS (mTLS) Client Certificates (Recommended)**:
   - **Hardware Provisioning**: Each vehicle tracker unit is flashed with a unique private key stored inside a tamper-proof **Secure Element (e.g., Microchip ATECC608 / TPM)** and a certificate signed by the company's internal Certificate Authority (CA).
   - **Handshake Verification**: When establishing an MQTTS connection on port 8883, Mosquitto verifies the client certificate against the CA chain.
   - **Identity Extraction**: Mosquitto extracts the `vehicle_code` directly from the certificate `Common Name` (e.g., `CN=BUS-001`), preventing device spoofing.
2. **Per-Device Unique Credentials**:
   - Trackers use isolated credentials (`device_BUS001`). Revoking a compromised unit does not impact other vehicles.
3. **Mosquitto Access Control Lists (ACLs)**:
   - Prevents compromised devices from publishing under another vehicle's topic:
     ```acl
     user device_BUS001
     topic write vehicles/BUS-001/gps

     user device_BUS002
     topic write vehicles/BUS-002/gps

     user backend_consumer
     topic read vehicles/+/gps
     ```

---

## 9. API Contract & Integration Specification

Base URL: `http://localhost:8000/api/v1` (or live Render backend `https://gps-9ei6.onrender.com/api/v1`)

### Standard Error Response Format
All 4xx and 5xx responses follow this structure:
```json
{
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human-readable error explanation"
  },
  "detail": "Human-readable error explanation"
}
```

### Endpoints Specification

#### 1. POST `/auth/login` & `/auth/login/json`
Authenticates user and returns JWT token. Accepts JSON or OAuth2 form-data.
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

#### 2. GET `/users/me`
Returns current user's profile. Password hashes are never exposed.

#### 3. GET `/me/route`
Returns the assigned route and parsed waypoints for the logged-in user.
- **Response** (`200 OK`):
  ```json
  {
    "id": 1,
    "route_code": "ROUTE-101",
    "route_name": "Route A - Downtown Express [DEV DEMO]",
    "description": "Primary downtown express connection",
    "start_location": "Downtown Hub",
    "end_location": "North Terminal",
    "waypoints": [
      {
        "sequence": 1,
        "name": "Stop 1: Downtown Hub",
        "latitude": 12.971598,
        "longitude": 77.594562,
        "is_stop": true
      }
    ],
    "created_at": "2026-09-05T16:57:04.887823Z"
  }
  ```

#### 4. GET `/me/vehicle`
Returns the assigned vehicle metadata and cached latest location.

#### 5. GET `/me/tracking`
Unified tracking summary containing assigned route, assigned vehicle, latest GPS coordinate, and derived vehicle status.

#### 6. GET `/me/tracking/current`
Lightweight, high-frequency polling endpoint for live map tracking.
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

#### 7. GET `/me/tracking/history`
Returns chronological historical telemetry records for the assigned vehicle. Supports `from`, `to`, and `limit` query parameters.

#### 8. POST `/gps`
REST GPS telemetry ingestion endpoint. Requires `X-API-Key: dev_gps_ingest_secret_key_2026` or Bearer JWT token. Returns `201 Created`.

#### 9. WebSocket `/ws/tracking` (Optional Bonus)
Live real-time WebSocket streaming endpoint. Connect via `ws://localhost:8000/api/v1/ws/tracking?token=<JWT_TOKEN>`. Pushes continuous telemetry JSON frames every 3 seconds.

---

## 10. Flutter Client Application

The mobile app (`mobile_app/`) provides an intuitive map experience built for public transit passengers and dispatchers:

### Key Features
1. **Live Interactive Map**: Fullscreen CartoDB basemap with smooth panning, zoom, and auto-route framing.
2. **Heading Direction Indicator**: Bus marker circle features a direction arrow that rotates dynamically based on live compass heading.
3. **Live Speed & Status Badges**: Shows real-time speed (km/h) and status (`ONLINE` pulsing green dot, `OFFLINE` red, or `STALE` amber).
4. **Dynamic ETA Calculation**: Calculates distance to closest upcoming stop and estimates remaining minutes in real time.
5. **Route Polyline Rendering**: Renders route path with glow effect and numbered waypoint stop markers.
6. **Strict Multi-Tenant State Isolation**: When logging in as User A or User B, prior vehicle states are cleared immediately and the camera automatically frames the user's specific route (Downtown Bangalore for User A, South Bangalore for User B).
7. **Quick Login Demo Buttons**: Quick-fill credentials for User A, User B, and Admin on the login screen.

### Running the Flutter App
```bash
cd mobile_app

# Fetch dependencies
flutter pub get

# Run tests
flutter test

# Run app (Chrome Web)
flutter run -d chrome

# Run app (Connected Android / iOS device)
flutter run
```

---

## 11. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_NAME` | `GPS Vehicle Tracking System Backend` | Application Display Name |
| `APP_ENV` | `development` | Environment (`development`, `testing`, `production`) |
| `DATABASE_URL` | `sqlite:///./vehicle_tracking.db` | PostgreSQL or SQLite connection string |
| `JWT_SECRET_KEY` | *(Random 32-char key)* | Secret key used for signing JWT access tokens |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` (7 days) | JWT expiration time in minutes |
| `MQTT_HOST` | `localhost` | Mosquitto MQTT Broker Host |
| `MQTT_PORT` | `1883` | Mosquitto MQTT Broker Port |
| `MQTT_USERNAME` | `gps_ingest_user` | MQTT Ingestion Username |
| `MQTT_PASSWORD` | `gps_secure_pass_2026` | MQTT Ingestion Password |
| `MQTT_TOPIC_PREFIX` | `vehicles/+/gps` | Ingestion subscription topic |
| `GPS_INGEST_API_KEY` | `dev_gps_ingest_secret_key_2026` | REST API Key for hardware/simulator ingestion |
| `GPS_ONLINE_THRESHOLD_SECONDS` | `30` | Threshold (seconds) for vehicle `ONLINE` status |
| `GPS_STALE_THRESHOLD_SECONDS` | `120` | Threshold (seconds) for vehicle `STALE` status |
| `VEHICLE_CODES` | `BUS-001,BUS-002` | Vehicles to simulate in `gps_simulator.py` |
| `SIMULATION_INTERVAL` | `3.0` | Simulator telemetry emission interval (seconds) |

---

## 12. Setup & Execution Guide

### Option A: Local Python & Zero-Config SQLite

```bash
# 1. Navigate to backend directory
cd vehicle-tracking-backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database with seed data
python -m scripts.seed_db

# 4. Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Docker Compose (FastAPI + PostgreSQL + Mosquitto)

```bash
# Build and run containers
docker-compose up --build
```
This automatically starts:
1. **PostgreSQL 16** on port `5432`
2. **Mosquitto MQTT Broker** on port `1883`
3. **FastAPI Backend** on port `8000`

### Option C: Live Cloud Deployment (Render)
- Live Backend URL: `https://gps-9ei6.onrender.com`
- Live Health Check: `https://gps-9ei6.onrender.com/health`
- Infrastructure defined in [`render.yaml`](file:///c:/Users/Bj/Pictures/task/render.yaml).

---

## 13. Automated Testing Suite

### Backend Pytest Suite
The backend test suite covers authentication, authorization scope guards, telemetry ingestion, caching, and cross-user security proofs:

```bash
cd vehicle-tracking-backend
python -m pytest
```
Output:
```
======================== 29 passed, 1 warning in 5.74s ========================
```

Key test files:
- `test_cross_user_security_proof.py`: Verifies that User A cannot access User B's vehicle, route, coordinates, or history (asserts HTTP 403 Forbidden).
- `test_auth.py`: Tests login, invalid credentials, and token decoding.
- `test_telemetry.py`: Verifies coordinate ingestion, speed validation, and history queries.
- `test_me_endpoints.py`: Verifies user assignment resolution.

### Flutter Test Suite
```bash
cd mobile_app
flutter test
```
Output:
```
00:02 +2: All tests passed!
```

---

## 14. Production Readiness Checklist

- [x] **Layered Architecture**: Clean 4-tier separation (`Controller` → `Service` → `Repository` → `Database`).
- [x] **Strict Authorization Scope Guards**: Rejects cross-user data requests with HTTP 403 Forbidden.
- [x] **Dual Telemetry Ingestion**: Mosquitto MQTT broker + secure REST API fallback.
- [x] **Multi-Vehicle Live Simulation**: Concurrent movement for `BUS-001` and `BUS-002` with dynamic compass bearing (heading).
- [x] **Idempotent Database Seeder**: Safely re-runnable CLI script with clean demo accounts.
- [x] **Coordinate Bounds & Data Validation**: Rejects invalid latitudes, longitudes, and negative speeds.
- [x] **Single-Query Cache Optimization**: Instant latest location lookups via cached columns on the vehicle table.
- [x] **Security Hardening**: Scrubbed production logging, masked credentials, CORS whitelist, request size limits (2MB).
- [x] **Cross-Platform Mobile Client**: Interactive live tracking map with rotating heading markers, auto-camera framing, and dynamic ETAs.
- [x] **100% Automated Test Pass Rate**: Verified backend Pytest and Flutter test suites.
