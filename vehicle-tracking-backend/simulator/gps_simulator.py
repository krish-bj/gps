import os
import time
import math
import json
import logging
from datetime import datetime, timezone
import requests
import paho.mqtt.client as mqtt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SIMULATOR] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("gps_simulator")

# Environment-based Configuration
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "gps_ingest_user")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "gps_secure_pass_2026")

VEHICLE_CODE = os.getenv("VEHICLE_CODE", "BUS-001")
SIMULATION_INTERVAL = float(os.getenv("SIMULATION_INTERVAL", 3.0))

REST_API_URL = os.getenv("REST_API_URL", "http://localhost:8000/api/v1/gps")
GPS_API_KEY = os.getenv("GPS_API_KEY", "dev_gps_ingest_secret_key_2026")

# Predefined Routes with Realistic Coordinates
ROUTES = {
    "BUS-001": [
        {"name": "Downtown Hub", "lat": 12.971598, "lng": 77.594562},
        {"name": "City Center Stop", "lat": 12.975000, "lng": 77.599000},
        {"name": "Commercial Zone", "lat": 12.980000, "lng": 77.605000},
        {"name": "Tech Hub East", "lat": 12.986000, "lng": 77.612000},
        {"name": "North Terminal", "lat": 12.992000, "lng": 77.620000},
    ],
    "BUS-002": [
        {"name": "South Terminal", "lat": 12.930000, "lng": 77.580000},
        {"name": "University Gate", "lat": 12.940000, "lng": 77.585000},
        {"name": "Hospital Square", "lat": 12.950000, "lng": 77.590000},
        {"name": "Metro Interchange", "lat": 12.960000, "lng": 77.595000},
        {"name": "Central Plaza", "lat": 12.970000, "lng": 77.600000},
    ]
}

class VehicleSimulator:
    """
    Simulates smooth, realistic vehicle movements along a predefined bus route.
    Generates latitude, longitude, realistic speeds, heading, and ISO timestamps.
    """
    def __init__(self, vehicle_code: str, waypoints: list, speed_base: float = 35.0):
        self.vehicle_code = vehicle_code
        self.waypoints = waypoints
        self.current_segment = 0
        self.progress = 0.0  # 0.0 to 1.0 within segment
        self.speed_base = speed_base
        self.step_count = 0

    def get_next_telemetry(self) -> dict:
        self.step_count += 1
        p1 = self.waypoints[self.current_segment]
        p2 = self.waypoints[(self.current_segment + 1) % len(self.waypoints)]

        # Interpolate location gradually
        lat = p1["lat"] + (p2["lat"] - p1["lat"]) * self.progress
        lng = p1["lng"] + (p2["lng"] - p1["lng"]) * self.progress

        # Realistic speed fluctuation (slower near stops, faster mid-route)
        speed = max(15.0, self.speed_base + (math.sin(self.progress * math.pi) * 15.0))

        # Advance progress along segment
        self.progress += 0.05
        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_segment = (self.current_segment + 1) % len(self.waypoints)

        timestamp_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "vehicle_code": self.vehicle_code,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "speed": round(speed, 1),
            "timestamp": timestamp_iso
        }

def run_simulation():
    waypoints = ROUTES.get(VEHICLE_CODE, ROUTES["BUS-001"])
    simulator = VehicleSimulator(VEHICLE_CODE, waypoints, speed_base=38.0)

    # Initialize MQTT Client with authentication
    mqtt_client = None
    try:
        if hasattr(mqtt, "CallbackAPIVersion"):
            mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"gps_sim_{VEHICLE_CODE}")
        else:
            mqtt_client = mqtt.Client(client_id=f"gps_sim_{VEHICLE_CODE}")
    except Exception:
        mqtt_client = mqtt.Client(client_id=f"gps_sim_{VEHICLE_CODE}")

    if MQTT_USERNAME and MQTT_PASSWORD:
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    mqtt_connected = False
    try:
        logger.info(f"Connecting to MQTT Broker ({MQTT_HOST}:{MQTT_PORT}) as user '{MQTT_USERNAME}'...")
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        mqtt_connected = True
        logger.info(f"Successfully connected to MQTT Broker ({MQTT_HOST}:{MQTT_PORT})")
    except Exception as e:
        logger.warning(f"Could not connect to MQTT Broker ({e}). Will use REST API fallback ({REST_API_URL}).")

    topic = f"vehicles/{VEHICLE_CODE}/gps"
    logger.info(f"Starting GPS simulation for '{VEHICLE_CODE}'. Target Topic: '{topic}'. Interval: {SIMULATION_INTERVAL}s")

    step = 0
    try:
        while True:
            step += 1
            telemetry = simulator.get_next_telemetry()
            payload_json = json.dumps(telemetry)

            if mqtt_connected:
                mqtt_client.publish(topic, payload_json)
                logger.info(
                    f"#{step:04d} [MQTT -> {topic}] Lat: {telemetry['latitude']}, Lng: {telemetry['longitude']}, Speed: {telemetry['speed']} km/h"
                )
            else:
                # REST API fallback ingestion
                headers = {"X-API-Key": GPS_API_KEY, "Content-Type": "application/json"}
                try:
                    res = requests.post(REST_API_URL, json=telemetry, headers=headers, timeout=2.5)
                    if res.status_code == 201:
                        logger.info(
                            f"#{step:04d} [REST API Fallback] Lat: {telemetry['latitude']}, Lng: {telemetry['longitude']}, Speed: {telemetry['speed']} km/h"
                        )
                    else:
                        logger.warning(f"#{step:04d} [REST Fallback] API status {res.status_code}: {res.text}")
                except Exception as req_err:
                    logger.warning(f"#{step:04d} [REST Fallback Error] {req_err}")

            time.sleep(SIMULATION_INTERVAL)
    except KeyboardInterrupt:
        logger.info("GPS Simulator stopped cleanly by user.")
    finally:
        if mqtt_client and mqtt_connected:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()

if __name__ == "__main__":
    run_simulation()
