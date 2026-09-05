from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.models import BusRoute

class RouteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, route_id: int) -> Optional[BusRoute]:
        return self.db.query(BusRoute).filter(BusRoute.id == route_id).first()

    def get_by_code(self, route_code: str) -> Optional[BusRoute]:
        return self.db.query(BusRoute).filter(BusRoute.route_code == route_code).first()

    def get_all(self) -> List[BusRoute]:
        return self.db.query(BusRoute).all()
