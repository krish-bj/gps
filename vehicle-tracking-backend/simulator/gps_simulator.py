import time
import math
import json
import logging
from datetime import datetime, timezone
import requests
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("gps_simulator")

# Backend API REST fallback URL
REST_API_URL = "http://localhost:8000/api/v1/gps/telemetry"

# MQTT Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# Route Waypoints Definition
ROUTE_A_WAYPOINTS = [
    {"lat": 37.774929, "lng": -122.419416}, # Central Station
    {"lat": 37.778500, "lng": -122.415000}, # Civic Center
    {"lat": 37.783333, "lng": -122.408889}, # Market Street
    {"lat": 37.788500, "lng": -122.402000}, # Financial District
    {"lat": 37.795000, "lng": -122.394000}, # Tech Park
]

ROUTE_B_WAYPOINTS = [
    {"lat": 37.804400, "lng": -122.408000}, # Fisherman Wharf
    {"lat": 37.800000, "lng": -122.418000}, # Russian Hill
    {"lat": 37.791000, "lng": -122.427000}, # Pacific Heights
    {"lat": 37.783000, "lng": -122.435000}, # Japantown
    {"lat": 37.776000, "lng": -122.451000}, # University Campus
]

class VehicleSimulator:
    def __init__(self, vehicle_code: str, waypoints: list, speed_base: float = 35.0):
        self.vehicle_code = vehicle_code
        self.waypoints = waypoints
        self.current_segment = 0
        self.progress = 0.0  # 0.0 to 1.0 along current segment
        self.speed_base = speed_base

    def get_next_telemetry(self):
        p1 = self.waypoints[self.current_segment]
        p2 = self.waypoints[(self.current_segment + 1) % len(self.waypoints)]

        # Interpolate location
        lat = p1["lat"] + (p2["lat"] - p1["lat"]) * self.progress
        lng = p1["lng"] + (p2["lng"] - p1["lng"]) * self.progress

        # Compute heading angle
        d_lat = p2["lat"] - p1["lat"]
        d_lng = p2["lng"] - p1["lng"]
        heading = (math.degrees(math.atan2(d_lng, d_lat)) + 360) % 360

        # Speed fluctuation
        speed = max(15.0, self.speed_base + (math.sin(self.progress * math.pi) * 15.0))

        # Advance progress
        self.progress += 0.1
        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_segment = (self.current_segment + 1) % len(self.waypoints)

        return {
            "vehicle_code": self.vehicle_code,
            "latitude": round(lat, 6),
            "longitude": round(lng, 6),
            "speed_kmh": round(speed, 1),
            "heading": round(heading, 1),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def run_simulation():
    bus_001 = VehicleSimulator("BUS-001", ROUTE_A_WAYPOINTS, speed_base=40.0)
    bus_002 = VehicleSimulator("BUS-002", ROUTE_B_WAYPOINTS, speed_base=32.0)
    simulators = [bus_001, bus_002]

    # Try initializing MQTT Client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="gps_simulator_client")
    mqtt_connected = False

    try:
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        mqtt_connected = True
        logger.info(f"Connected to MQTT Broker at {MQTT_HOST}:{MQTT_PORT}")
    except Exception as e:
        logger.warning(f"Could not connect to MQTT Broker ({e}). Will use REST API fallback: {REST_API_URL}")

    logger.info("GPS Simulator running... Publishing telemetry every 3 seconds.")

    while True:
        try:
            for sim in simulators:
                telemetry = sim.get_next_telemetry()
                topic = f"vehicles/{sim.vehicle_code}/telemetry"

                # Publish via MQTT if connected
                if mqtt_connected:
                    mqtt_client.publish(topic, json.dumps(telemetry))
                    logger.info(f"[MQTT -> {topic}] Lat: {telemetry['latitude']}, Lng: {telemetry['longitude']}, Speed: {telemetry['speed_kmh']} km/h")

                # Always post to REST API for instant database updates
                try:
                    res = requests.post(REST_API_URL, json=telemetry, timeout=2)
                    if res.status_code == 201:
                        logger.info(f"[REST -> {sim.vehicle_code}] Updated successfully via REST endpoint.")
                    else:
                        logger.warning(f"[REST -> {sim.vehicle_code}] API returned {res.status_code}: {res.text}")
                except Exception as req_err:
                    logger.debug(f"REST request error: {req_err}")

            time.sleep(3)
        except KeyboardInterrupt:
            logger.info("GPS Simulator stopped.")
            break
        except Exception as ex:
            logger.error(f"Simulator error: {ex}")
            time.sleep(3)

if __name__ == "__main__":
    run_simulation()
