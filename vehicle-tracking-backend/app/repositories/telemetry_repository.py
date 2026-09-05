from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import GPSTelemetry

class TelemetryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_by_vehicle_id(self, vehicle_id: int) -> Optional[GPSTelemetry]:
        return self.db.query(GPSTelemetry)\
            .filter(GPSTelemetry.vehicle_id == vehicle_id)\
            .order_by(GPSTelemetry.timestamp.desc())\
            .first()

    def get_history_by_vehicle_id(self, vehicle_id: int, limit: int = 100) -> List[GPSTelemetry]:
        return self.db.query(GPSTelemetry)\
            .filter(GPSTelemetry.vehicle_id == vehicle_id)\
            .order_by(GPSTelemetry.timestamp.desc())\
            .limit(limit)\
            .all()

    def create(self, vehicle_id: int, latitude: float, longitude: float, speed_kmh: float, heading: float, timestamp: Optional[datetime] = None) -> GPSTelemetry:
        ts = timestamp or datetime.now(timezone.utc)
        telemetry = GPSTelemetry(
            vehicle_id=vehicle_id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            heading=heading,
            timestamp=ts
        )
        self.db.add(telemetry)
        return telemetry
