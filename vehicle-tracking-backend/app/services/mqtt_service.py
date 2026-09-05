import json
import logging
import threading
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.models import Vehicle, GPSTelemetry

logger = logging.getLogger("mqtt_service")

class MQTTService:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="fastapi_gps_backend")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self._thread = None
        self.is_connected = False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
            self.is_connected = True
            client.subscribe(settings.MQTT_TOPIC)
            logger.info(f"Subscribed to MQTT Topic: {settings.MQTT_TOPIC}")
        else:
            logger.warning(f"MQTT Connect failed with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
            
            topic_parts = msg.topic.split("/")
            vehicle_code_topic = topic_parts[1] if len(topic_parts) >= 3 else None

            vehicle_code = data.get("vehicle_code") or vehicle_code_topic
            vehicle_id = data.get("vehicle_id")
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            speed_kmh = data.get("speed_kmh", 0.0)
            heading = data.get("heading", 0.0)
            
            if latitude is None or longitude is None:
                return

            db = SessionLocal()
            try:
                vehicle = None
                if vehicle_id:
                    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
                elif vehicle_code:
                    vehicle = db.query(Vehicle).filter(Vehicle.vehicle_code == vehicle_code).first()

                if vehicle:
                    timestamp_val = datetime.now(timezone.utc)
                    if data.get("timestamp"):
                        try:
                            timestamp_val = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                        except Exception:
                            pass

                    telemetry = GPSTelemetry(
                        vehicle_id=vehicle.id,
                        latitude=float(latitude),
                        longitude=float(longitude),
                        speed_kmh=float(speed_kmh),
                        heading=float(heading),
                        timestamp=timestamp_val
                    )
                    db.add(telemetry)

                    vehicle.last_latitude = float(latitude)
                    vehicle.last_longitude = float(longitude)
                    vehicle.last_speed = float(speed_kmh)
                    vehicle.last_timestamp = timestamp_val
                    vehicle.status = "MOVING" if float(speed_kmh) > 0 else "IDLE"

                    db.commit()
            finally:
                db.close()

        except Exception as e:
            logger.error(f"MQTT message processing error: {e}")

    def start(self):
        if not settings.MQTT_ENABLED:
            return

        def run_loop():
            try:
                self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
                self.client.loop_forever()
            except Exception as e:
                logger.warning(f"MQTT Broker connection failed ({e}). REST fallback is active.")

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

mqtt_service = MQTTService()
