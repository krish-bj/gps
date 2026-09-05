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
            .order_by(GPSTelemetry.recorded_at.desc())\
            .first()

    def get_history_by_vehicle_id(self, vehicle_id: int, limit: int = 100) -> List[GPSTelemetry]:
        return self.db.query(GPSTelemetry)\
            .filter(GPSTelemetry.vehicle_id == vehicle_id)\
            .order_by(GPSTelemetry.recorded_at.desc())\
            .limit(limit)\
            .all()

    def create(self, vehicle_id: int, latitude: float, longitude: float, speed_kmh: float, heading: float, timestamp: Optional[datetime] = None, source: str = "REST") -> GPSTelemetry:
        ts = timestamp or datetime.now(timezone.utc)
        telemetry = GPSTelemetry(
            vehicle_id=vehicle_id,
            latitude=latitude,
            longitude=longitude,
            speed=speed_kmh,
            heading=heading,
            recorded_at=ts,
            received_at=datetime.now(timezone.utc),
            source=source
        )
        self.db.add(telemetry)
        return telemetry
