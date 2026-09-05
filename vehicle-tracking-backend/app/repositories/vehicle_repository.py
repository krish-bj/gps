from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import Vehicle

class VehicleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        return self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    def get_by_code(self, vehicle_code: str) -> Optional[Vehicle]:
        return self.db.query(Vehicle).filter(Vehicle.vehicle_code == vehicle_code).first()

    def get_all(self) -> List[Vehicle]:
        return self.db.query(Vehicle).all()
