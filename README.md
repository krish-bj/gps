# GPS Vehicle Tracking System (FastAPI + Flutter)

A GPS-based vehicle tracking system featuring a Python FastAPI backend, PostgreSQL/SQLite database, MQTT telemetry ingestion, live GPS simulator, containerized Docker Compose environment, and a Flutter mobile/web client.

---

## System Architecture

```
                               ┌───────────────────────────┐
                               │       GPS Simulator       │
                               │  (BUS-001 & BUS-002 GPS)  │
                               └─────────────┬─────────────┘
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │ MQTT (Mosquitto) / REST Ingestion API    │
                       └─────────────────────┬─────────────────────┘
                                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                     FastAPI Backend                                      │
│                                                                                          │
│  • JWT Authentication & User Isolation Authorization                                      │
│  • SQLAlchemy ORM Data Layer (SQLite / PostgreSQL)                                        │
│  • REST Endpoints: Auth, Users, Assigned Route, Vehicles, Telemetry Ingestion            │
└───────────────────────────────┬───────────────────────────────┬──────────────────────────┘
                                │                               │
                                ▼                               ▼
                     ┌─────────────────────┐         ┌─────────────────────┐
                     │ PostgreSQL / SQLite │         │ Flutter Client App  │
                     │ Database            │         │ (Auth, Live Map,    │
                     │                     │         │  Route Isolation)   │
                     └─────────────────────┘         └─────────────────────┘
```

---

## Key Features & Business Logic Enforcement

1. **User-to-Route & Vehicle Assignment**:
   - **User A** (`usera@example.com` / `user123`): Assigned to **Route A** (Downtown Express) & **BUS-001**.
   - **User B** (`userb@example.com` / `user123`): Assigned to **Route B** (Uptown Shuttle) & **BUS-002**.
   - **Admin** (`admin@example.com` / `admin123`): Access to all routes and vehicles.

2. **Backend Authorization Enforcement**:
   - Route and vehicle access restrictions are strictly enforced on the **FastAPI backend level** (not just hidden in the frontend UI).
   - If User A attempts to request `/api/v1/vehicles/2/location/latest` (User B's vehicle), the backend rejects the request with **HTTP 403 Forbidden**.

3. **Dual Telemetry Ingestion**:
   - **MQTT Protocol**: Listens on `vehicles/+/telemetry` via background Paho-MQTT consumer.
   - **REST API Fallback**: `POST /api/v1/gps/telemetry` for immediate HTTP telemetry submissions.

4. **Historical & Real-Time Tracking**:
   - Telemetry logs are stored chronologically to maintain full location history.
   - Cached position updates on the vehicle record allow instant single-query latest location responses.

---

## Directory Structure

```
task/
├── backend/                  # FastAPI Service Source Code
│   ├── app/
│   │   ├── api/v1/           # Routers (Auth, Users, Routes, Vehicles, Telemetry)
│   │   ├── core/             # Config, Database Engine, JWT & Password Security
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── schemas/          # Pydantic V2 Schemas
│   │   ├── services/         # Seed Data Auto-populator & MQTT Listener Service
│   │   └── main.py           # FastAPI App Startup & Lifespan Hooks
│   ├── verify_backend.py     # End-to-End Verification Test Suite
│   ├── Dockerfile            # Container definition for FastAPI
│   └── requirements.txt      # Python Dependencies
├── simulator/                # Standalone GPS Simulation Tool
│   ├── gps_simulator.py      # Streams live BUS-001/002 coordinates
│   └── requirements.txt
├── docker-compose.yml        # Docker setup (PostgreSQL + Mosquitto + FastAPI)
├── mosquitto.conf            # Mosquitto MQTT Configuration
└── README.md
```

---

## Running the Backend

### Option A: Local Python Execution (Zero-Config SQLite)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Verification Suite (Tests auth, route isolation, telemetry)
python verify_backend.py

# 4. Start FastAPI Server
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### Option B: Docker Compose (PostgreSQL + Mosquitto MQTT + FastAPI)

```bash
docker-compose up --build
```

---

## Running the GPS Simulator

```bash
cd simulator
pip install -r requirements.txt
python gps_simulator.py
```
Streams coordinates for BUS-001 and BUS-002 along realistic route waypoints every 3 seconds.
