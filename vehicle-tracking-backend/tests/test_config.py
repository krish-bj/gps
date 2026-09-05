import pytest
from pydantic import ValidationError
from app.core.config import Settings

def test_safe_dict_masks_secrets():
    s = Settings(
        DATABASE_URL="postgresql://user:secretpassword@localhost:5432/mydb",
        JWT_SECRET_KEY="supersecretkey12345678901234567890",
        MQTT_PASSWORD="mqttsecretpassword"
    )
    safe = s.safe_dict()
    assert "secretpassword" not in safe["DATABASE_URL"]
    assert "postgresql://***:***@localhost:5432/mydb" in safe["DATABASE_URL"]
    assert "JWT_SECRET_KEY" not in safe
    assert "MQTT_PASSWORD" not in safe

def test_production_fails_on_insecure_jwt_secret():
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            DATABASE_URL="postgresql://postgres:pass@localhost:5432/db",
            JWT_SECRET_KEY="change_this_default_key"
        )
    assert "JWT_SECRET_KEY" in str(exc_info.value)

def test_production_fails_on_sqlite_database():
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_ENV="production",
            DATABASE_URL="sqlite:///./dev.db",
            JWT_SECRET_KEY="a_very_secure_long_random_jwt_secret_key_32_chars!"
        )
    assert "DATABASE_URL" in str(exc_info.value)
