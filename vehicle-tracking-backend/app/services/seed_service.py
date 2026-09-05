from sqlalchemy.orm import Session
from app.services.seed_data import init_db_seed

class SeedService:
    def __init__(self, db: Session):
        self.db = db

    def seed_initial_data(self):
        init_db_seed(self.db)
