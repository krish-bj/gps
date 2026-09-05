# vehicle-tracking-backend

Standalone production-grade Python FastAPI backend for real-time GPS vehicle tracking, bus route management, user assignments, and authorization enforcement.

---

## Core Relationship Model

```
Authenticated User
       ↓
Assigned Route
       ↓
Assigned Vehicle
       ↓
Latest GPS Location
       ↓
Historical GPS Tracking
```

---

## Tech Stack & Architecture

- **Python 3.12**
- **FastAPI**: REST API Framework with OpenAPI docs.
- **SQLAlchemy 2.x**: ORM with Declarative Base & Mapped type annotations.
- **PostgreSQL / SQLite**: Dual DB support via SQLAlchemy.
- **Alembic**: Database migrations framework (`alembic/`).
- **Pydantic V2**: Data schemas & validation.
- **JWT & Bcrypt**: Secure OAuth2 authentication and password hashing.
- **Mosquitto MQTT & Paho-MQTT**: Asynchronous background telemetry consumer listening on `vehicles/+/telemetry`.
- **Docker & Docker Compose**: Full containerization (`PostgreSQL`, `Mosquitto`, `FastAPI`).
- **Pytest Suite**: Complete test suite testing authentication, authorization, routes, and telemetry.

---

## Authorization & Security Enforcement

Authorization is strictly enforced by FastAPI at the API layer:
- **User A** (`usera@example.com` / `user123`) → Assigned to **Route A** (ROUTE-101) & **BUS-001**.
- **User B** (`userb@example.com` / `user123`) → Assigned to **Route B** (ROUTE-202) & **BUS-002**.

> [!IMPORTANT]
> If User A manually attempts to query User B's vehicle ID, route ID, latest location, or location history, the FastAPI backend rejects the request with **HTTP 403 Forbidden**.

---

## Quick Start (Local Setup)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations (Alembic)
```bash
alembic upgrade head
```

### 3. Run Pytest Verification Suite
```bash
pytest
```

### 4. Start FastAPI Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Documentation: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

---

## Docker Compose Quick Start

```bash
docker-compose up --build
```

Runs PostgreSQL 16 on port `5432`, Eclipse Mosquitto MQTT on port `1883`, and FastAPI Backend on port `8000`.
