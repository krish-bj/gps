import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.services.seed_service import SeedService

def main():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Executing idempotent development database seeder...")
    db = SessionLocal()
    try:
        seeder = SeedService(db)
        seeder.seed_initial_data()
        
        print("\n" + "=" * 60)
        print(" DEVELOPMENT / DEMO DATA SEEDED SUCCESSFULLY")
        print("=" * 60)
        print(" Credentials Summary:")
        print("  • User A: usera@example.com / user123 (Route A - Downtown Express, BUS-001)")
        print("  • User B: userb@example.com / user123 (Route B - Uptown Shuttle, BUS-002)")
        print("  • Admin : admin@example.com / admin123 (System-wide Administrator)")
        print("=" * 60 + "\n")
    finally:
        db.close()

if __name__ == "__main__":
    main()

