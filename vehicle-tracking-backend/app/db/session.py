from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Connection options & pool health handling
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,  # Enables connection health check before checkout
}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # Production PostgreSQL connection pool settings
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,  # Recycle connections after 30 minutes
    })

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI database dependency providing a transactional DB session per request.
    Guarantees proper session cleanup (closing) even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
