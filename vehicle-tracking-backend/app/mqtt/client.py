import json
import logging
import threading
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.tracking_service import TrackingService

logger = logging.getLogger("mqtt_client")

class MQTTClient:
    def __init__(self):
        self.client = None
        self._thread = None
        self._is_running = False

    def _init_client(self):
        try:
            if hasattr(mqtt, "CallbackAPIVersion"):
                self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="fastapi_gps_backend")
            else:
                self.client = mqtt.Client(client_id="fastapi_gps_backend")
        except Exception:
            self.client = mqtt.Client(client_id="fastapi_gps_backend")

        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            logger.info(f"Successfully connected to Mosquitto MQTT Broker ({settings.MQTT_HOST}:{settings.MQTT_PORT})")
            client.subscribe(settings.MQTT_TOPIC_PREFIX)
            client.subscribe("vehicles/+/gps")
            client.subscribe("vehicles/+/telemetry")
            logger.info(f"Subscribed to MQTT topics: '{settings.MQTT_TOPIC_PREFIX}', 'vehicles/+/gps'")
        else:
            logger.warning(f"MQTT broker connection failed with return code {rc}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection (rc={rc}). Automatic reconnect active.")

    def on_message(self, client, userdata, msg):
        """
        Handle incoming MQTT messages on topic: vehicles/{vehicle_code}/gps
        Payload:
        {
          "latitude": 12.9716,
          "longitude": 77.5946,
          "speed": 35.4,
          "timestamp": "2026-09-05T10:30:00Z"
        }
        Calls the SAME TrackingService.ingest_telemetry() used by REST API ingestion.
        """
        db = None
        try:
            payload_str = msg.payload.decode("utf-8")
            data = json.loads(payload_str)
            
            # Extract vehicle_code from topic: vehicles/{vehicle_code}/gps
            topic_parts = msg.topic.split("/")
            vehicle_code_topic = topic_parts[1] if len(topic_parts) >= 2 else None

            vehicle_code = data.get("vehicle_code") or vehicle_code_topic
            vehicle_id = data.get("vehicle_id")
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            speed = data.get("speed", data.get("speed_kmh", 0.0))
            heading = data.get("heading", 0.0)

            if latitude is None or longitude is None:
                logger.warning(f"MQTT message ignored: missing latitude or longitude on topic '{msg.topic}'")
                return

            if not vehicle_code and not vehicle_id:
                logger.warning(f"MQTT message ignored: missing vehicle_code or vehicle_id on topic '{msg.topic}'")
                return

            timestamp_val = None
            if data.get("timestamp"):
                try:
                    ts_str = str(data["timestamp"]).replace("Z", "+00:00")
                    timestamp_val = datetime.fromisoformat(ts_str)
                except Exception as parse_err:
                    logger.warning(f"Failed to parse MQTT timestamp '{data.get('timestamp')}': {parse_err}")
                    timestamp_val = datetime.now(timezone.utc)

            # Delegate to the SAME TrackingService used by REST API ingestion
            db = SessionLocal()
            tracking_service = TrackingService(db)
            tracking_service.ingest_telemetry(
                latitude=float(latitude),
                longitude=float(longitude),
                speed_kmh=float(speed),
                heading=float(heading),
                vehicle_code=str(vehicle_code) if vehicle_code else None,
                vehicle_id=int(vehicle_id) if vehicle_id else None,
                timestamp=timestamp_val,
                source="MQTT"
            )
            logger.debug(f"MQTT telemetry ingested for vehicle '{vehicle_code or vehicle_id}'")
        except Exception as e:
            logger.error(f"Error processing MQTT payload on '{msg.topic}': {e}", exc_info=False)
        finally:
            if db:
                db.close()

    def start(self):
        if not settings.MQTT_ENABLED:
            logger.info("MQTT Service is disabled via settings (MQTT_ENABLED=False).")
            return

        if self._is_running:
            return

        self._init_client()
        self._is_running = True

        def run_loop():
            try:
                logger.info(f"Connecting MQTT client to broker at {settings.MQTT_HOST}:{settings.MQTT_PORT}...")
                self.client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
                self.client.loop_forever()
            except Exception as e:
                logger.warning(f"MQTT broker unavailable ({e}). REST API ingestion active.")

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self._is_running:
            return
        self._is_running = False
        if self.client:
            try:
                self.client.disconnect()
                self.client.loop_stop()
                logger.info("MQTT Client disconnected cleanly.")
            except Exception as e:
                logger.warning(f"Error disconnecting MQTT client: {e}")

mqtt_client = MQTTClient()

