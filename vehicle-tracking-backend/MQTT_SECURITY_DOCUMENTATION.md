# MQTT Security Architecture & Production Authentication Guide

> **Target Audience**: Backend Engineers, Systems Architects, and Security Reviewers  
> **Repository Path**: `vehicle-tracking-backend/`

---

## 1. Overview of Assessment Security Implementation

In this assessment environment, the Mosquitto MQTT broker and FastAPI consumer are configured with **authenticated access control**:

- **Anonymous Access Disabled**: `allow_anonymous false` in `mosquitto.conf`.
- **Password File Authentication**: Credentials managed via `/mosquitto/config/pwfile`.
- **FastAPI Consumer Credentials**: Authenticates using environment variables (`MQTT_USERNAME` and `MQTT_PASSWORD`) supplied to the background Paho-MQTT loop.

---

## 2. Environment & Docker Configuration

### A. Mosquitto Configuration (`mosquitto.conf`)
```ini
listener 1883 0.0.0.0
allow_anonymous false
password_file /mosquitto/config/pwfile

listener 9001 0.0.0.0
protocol websockets
allow_anonymous false
password_file /mosquitto/config/pwfile
```

### B. Docker Secrets & Environment Handling
In `docker-compose.yml`, credentials are supplied to the FastAPI container via environment variables:
```yaml
environment:
  MQTT_BROKER_HOST: "mqtt"
  MQTT_BROKER_PORT: 1883
  MQTT_USERNAME: "gps_ingest_user"
  MQTT_PASSWORD: "gps_secure_pass_2026"
```

In production setups, these secrets are injected via **Docker Secrets** or Kubernetes Secret objects (`/run/secrets/mqtt_password`) rather than plaintext compose environment strings.

---

## 3. How Real Hardware GPS Devices Authenticate in Production

While password-file authentication satisfies assessment requirements, enterprise GPS tracking systems implement multi-layered hardware security:

### A. X.509 Mutual TLS (mTLS) Client Certificates (Recommended)
1. **Device Provisioning**: During factory manufacturing, each hardware device is flashed with a unique private key stored inside a **Secure Element (ATECC608) / TPM chip** and a client X.509 certificate signed by the internal Certificate Authority (CA).
2. **TLS Handshake**: When connecting to port 8883 (MQTTS), Mosquitto verifies the client certificate against the CA chain before allowing a connection.
3. **Common Name (CN) Resolution**: Mosquitto extracts the `vehicle_code` directly from the certificate's `Common Name` (e.g. `CN=BUS-001`), eliminating client identity spoofing.

### B. Per-Device Credentials & Tokens
- Hardware devices are assigned unique MQTT credentials (e.g., username `device_BUS001` and rotating token).
- Revocation of a compromised device credential does not affect other fleet vehicles.

### C. Mosquitto Access Control Lists (ACLs)
To prevent a compromised hardware unit (e.g., `BUS-001`) from publishing telemetry under another vehicle's identity (e.g., `BUS-002`), Mosquitto ACLs enforce topic authorization:

```acl
# Mosquitto ACL File (mosquitto.acl)
user device_BUS001
topic write vehicles/BUS-001/gps

user device_BUS002
topic write vehicles/BUS-202/gps

user fastapi_backend_consumer
topic read vehicles/+/gps
```

---

## 4. FastAPI MQTT Consumer Verification

The FastAPI background consumer (`app/mqtt/client.py`) automatically invokes `username_pw_set()` prior to initiating the loop:

```python
if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
    self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
```

Unauthenticated connection attempts or invalid credentials result in immediate rejection by Mosquitto (`rc = 4` / `rc = 5` Unauthorized).
