from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GPS Vehicle Tracking System Backend"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "supersecretjwtkey_vehicle_tracking_2026_dev_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database configuration (defaults to SQLite, PostgreSQL supported via env)
    DATABASE_URL: str = "sqlite:///./vehicle_tracking.db"
    
    # MQTT Broker Configuration
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_TOPIC: str = "vehicles/+/telemetry"
    MQTT_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
