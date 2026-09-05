from sqlalchemy import text
from app.db.session import engine, get_db

def test_database_engine_connection_health():
    """Verify database connection health ping (pool_pre_ping)."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_get_db_session_lifecycle():
    """Verify get_db dependency yields active session and handles session closing cleanly."""
    generator = get_db()
    db = next(generator)
    assert db.is_active
    
    # Trigger generator teardown
    try:
        next(generator)
    except StopIteration:
        pass
