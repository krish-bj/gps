# Flutter Developer API Contract & Integration Guide
**Vehicle Tracking Backend API — v1.0.0**

Base URL: `http://<server-ip>:8000/api/v1`

---

## 1. Authentication & Security Policy
- All endpoints except `POST /api/v1/auth/login` require an HTTP `Authorization` header with a valid JWT Bearer token:
  ```http
  Authorization: Bearer <JWT_ACCESS_TOKEN>
  ```
- Error payload format is standardized across all 4xx/5xx responses:
  ```json
  {
    "error": {
      "code": "ERROR_CODE_STRING",
      "message": "Human-readable error explanation"
    }
  }
  ```

---

## 2. API Endpoints Specification

### 2.1 POST `/auth/login`
Authenticates a user and issues a JWT access token.

- **Auth Required**: `None` (Public)
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "email": "usera@example.com",
    "password": "UserA@123"
  }
  ```
- **Query Parameters**: None
- **Response JSON** (`200 OK`):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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
- **Possible Errors**:
  - `400 Bad Request` (`INVALID_CREDENTIALS`): Email and password required.
  - `401 Unauthorized` (`INVALID_CREDENTIALS`): Incorrect email or password.
  - `403 Forbidden` (`FORBIDDEN_ACCESS`): Inactive user account.

---

### 2.2 GET `/users/me`
Retrieves the safe user profile of the currently authenticated user.

- **Auth Required**: `Bearer Token`
- **Request Body**: None
- **Query Parameters**: None
- **Response JSON** (`200 OK`):
  ```json
  {
    "id": 2,
    "email": "usera@example.com",
    "full_name": "User A",
    "role": "user",
    "is_active": true
  }
  ```
- **Possible Errors**:
  - `401 Unauthorized` (`AUTHENTICATION_FAILED`): Expired, missing, or malformed JWT token.
  - `403 Forbidden` (`FORBIDDEN_ACCESS`): Account is inactive.

---

### 2.3 GET `/me/route`
Retrieves details and waypoints of the route assigned to the authenticated user.

- **Auth Required**: `Bearer Token`
- **Request Body**: None
- **Query Parameters**: None
- **Response JSON** (`200 OK`):
  ```json
  {
    "id": 1,
    "route_code": "ROUTE-101",
    "route_name": "Downtown Express Line",
    "description": "Primary downtown transit route from Central Station to North Terminal",
    "start_location": "Central Bus Station",
    "end_location": "North Transit Hub",
    "waypoints": [
      {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "name": "Stop 1 - Central Station"
      },
      {
        "latitude": 12.9750,
        "longitude": 77.5980,
        "name": "Stop 2 - City Center"
      }
    ],
    "route_points": [
      {
        "id": 1,
        "route_id": 1,
        "sequence": 1,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "name": "Stop 1 - Central Station"
      }
    ],
    "created_at": "2026-09-05T10:00:00Z"
  }
  ```
- **Possible Errors**:
  - `401 Unauthorized` (`AUTHENTICATION_FAILED`)
  - `403 Forbidden` (`FORBIDDEN_ACCESS`): User has no active route assignment.

---

### 2.4 GET `/me/vehicle`
Retrieves details of the vehicle assigned to the authenticated user.

- **Auth Required**: `Bearer Token`
- **Request Body**: None
- **Query Parameters**: None
- **Response JSON** (`200 OK`):
  ```json
  {
    "id": 1,
    "vehicle_code": "BUS-001",
    "license_plate": "KA-01-EQ-1001",
    "model_name": "Standard Transit Bus",
    "status": "ONLINE",
    "last_latitude": 12.9716,
    "last_longitude": 77.5946,
    "last_speed": 35.4,
    "last_timestamp": "2026-09-05T10:30:00Z"
  }
  ```
- **Possible Errors**:
  - `401 Unauthorized` (`AUTHENTICATION_FAILED`)
  - `403 Forbidden` (`FORBIDDEN_ACCESS`): User has no active vehicle assignment.

---

### 2.5 GET `/me/tracking`
Unified endpoint returning route details, vehicle details, latest GPS location, and dynamic status.

- **Auth Required**: `Bearer Token`
- **Request Body**: None
- **Query Parameters**: None
- **Response JSON** (`200 OK`):
  ```json
  {
    "route": {
      "id": 1,
      "route_code": "ROUTE-101",
      "route_name": "Downtown Express Line",
      "description": "Primary downtown transit route",
      "start_location": "Central Bus Station",
      "end_location": "North Transit Hub",
      "waypoints": [
        {
          "latitude": 12.9716,
          "longitude": 77.5946,
          "name": "Stop 1 - Central Station"
        }
      ],
      "created_at": "2026-09-05T10:00:00Z"
    },
    "vehicle": {
      "id": 1,
      "vehicle_code": "BUS-001",
      "license_plate": "KA-01-EQ-1001",
      "model_name": "Standard Transit Bus",
      "status": "ONLINE",
      "last_latitude": 12.9716,
      "last_longitude": 77.5946,
      "last_speed": 35.4,
      "last_timestamp": "2026-09-05T10:30:00Z"
    },
    "latest_location": {
      "id": 101,
      "vehicle_id": 1,
      "latitude": 12.9716,
      "longitude": 77.5946,
      "speed_kmh": 35.4,
      "heading": 90.0,
      "recorded_at": "2026-09-05T10:30:00Z",
      "received_at": "2026-09-05T10:30:01Z",
      "source": "MQTT"
    },
    "status": {
      "vehicle_status": "ONLINE",
      "is_active_assignment": true,
      "last_updated": "2026-09-05T10:30:00Z"
    }
  }
  ```
- **Possible Errors**:
  - `401 Unauthorized` (`AUTHENTICATION_FAILED`)
  - `403 Forbidden` (`FORBIDDEN_ACCESS`)

---

### 2.6 GET `/me/tracking/current`
Lightweight endpoint returning current location and dynamic status (`ONLINE`, `STALE`, `OFFLINE`, `NO_DATA`) for polling UI updates.

- **Auth Required**: `Bearer Token`
- **Request Body**: None
- **Query Parameters**: None
- **Response JSON** (`200 OK`):
  ```json
  {
    "vehicle_code": "BUS-001",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "speed": 35.4,
    "recorded_at": "2026-09-05T10:30:00Z",
    "received_at": "2026-09-05T10:30:01Z",
    "status": "ONLINE"
  }
  ```
- **Possible Errors**:
  - `401 Unauthorized` (`AUTHENTICATION_FAILED`)
  - `403 Forbidden` (`FORBIDDEN_ACCESS`)

---

### 2.7 GET `/me/tracking/history`
Retrieves historical GPS logs for the assigned vehicle within optional time bounds.

- **Auth Required**: `Bearer Token`
- **Request Body**: None
- **Query Parameters**:
  - `from` (optional, string): ISO 8601 timestamp (e.g. `2026-09-05T00:00:00Z`)
  - `to` (optional, string): ISO 8601 timestamp (e.g. `2026-09-05T23:59:59Z`)
  - `limit` (optional, integer, default: `100`, min: `1`, max: `1000`)
- **Response JSON** (`200 OK`):
  ```json
  [
    {
      "id": 105,
      "vehicle_id": 1,
      "latitude": 12.9720,
      "longitude": 77.5950,
      "speed_kmh": 36.0,
      "heading": 90.0,
      "recorded_at": "2026-09-05T10:31:00Z",
      "received_at": "2026-09-05T10:31:01Z",
      "source": "MQTT"
    },
    {
      "id": 101,
      "vehicle_id": 1,
      "latitude": 12.9716,
      "longitude": 77.5946,
      "speed_kmh": 35.4,
      "heading": 90.0,
      "recorded_at": "2026-09-05T10:30:00Z",
      "received_at": "2026-09-05T10:30:01Z",
      "source": "MQTT"
    }
  ]
  ```
- **Possible Errors**:
  - `400 Bad Request` (`VALIDATION_ERROR`): Invalid timestamp format or `from` > `to`.
  - `401 Unauthorized` (`AUTHENTICATION_FAILED`)
  - `403 Forbidden` (`FORBIDDEN_ACCESS`)

---

## 3. Flutter Application Integration Workflow

```
[ User Inputs Credentials ]
         │
         ▼
 1. POST /api/v1/auth/login ────────► Receives JWT access_token
         │
         ▼
 2. Secure Storage ──────────────────► Save token in flutter_secure_storage / Keychain
         │
         ▼
 3. GET /api/v1/me/tracking ────────► Fetch route, vehicle & latest location
         │
  ┌──────┴──────────────────────────┐
  ▼                                 ▼
 4. Draw Polyline          5. Place Marker
    Parse waypoints list       Render vehicle marker at (lat, lng)
    Draw route line on Map     Display status badge (ONLINE/STALE/OFFLINE)
  └──────┬──────────────────────────┘
         │
         ▼
 6. Periodic Polling / Refresh
    Call GET /api/v1/me/tracking/current every 5 seconds
    Animate vehicle marker to updated (lat, lng) & update speed badge
```

### Detailed Execution Steps:
1. **User Authentication (Login)**:
   - Present login UI (Email & Password).
   - Send `POST /api/v1/auth/login`.
2. **Save JWT Securely**:
   - On HTTP `200`, extract `access_token`.
   - Store `access_token` in OS secure storage (`flutter_secure_storage` or iOS Keychain / Android EncryptedSharedPreferences).
3. **Call Tracking API**:
   - Make an authenticated request to `GET /api/v1/me/tracking` attaching `Authorization: Bearer <token>`.
4. **Draw Route Polyline**:
   - Extract `route.waypoints` (or `route.route_points`).
   - Create map polyline coordinates list `[LatLng(wpt.latitude, wpt.longitude), ...]` sorted by `sequence`.
   - Render the polyline overlay on the Flutter map view (e.g. `google_maps_flutter` or `flutter_map`).
5. **Place Vehicle Marker**:
   - Extract initial position from `latest_location` or `vehicle.last_latitude`, `vehicle.last_longitude`.
   - Render a custom bus marker at `LatLng(latitude, longitude)`.
   - Display a status indicator badge according to `status.vehicle_status`:
     - `ONLINE` (Green badge)
     - `STALE` (Yellow/Orange badge)
     - `OFFLINE` (Red badge)
     - `NO_DATA` (Gray badge)
6. **Refresh Current Location**:
   - Set a periodic timer (e.g. every 5–10 seconds) calling `GET /api/v1/me/tracking/current`.
   - Update vehicle marker position smoothly with animation, update speed display, and refresh status badge without re-drawing the entire route.
