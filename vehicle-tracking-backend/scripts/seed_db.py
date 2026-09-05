import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.services.seed_service import SeedService

def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Seeding initial routes, vehicles, users, and telemetry data...")
    db = SessionLocal()
    try:
        seeder = SeedService(db)
        seeder.seed_initial_data()
        print("Database seed completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
