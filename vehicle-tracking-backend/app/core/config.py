import os
from typing import Optional, Dict, Any, Union
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Configuration
    APP_NAME: str = Field(default="GPS Vehicle Tracking System Backend", description="Application Name")
    APP_ENV: str = Field(default="development", description="Environment: development, testing, production")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API Version 1 Prefix")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")

    
    # Backward compatibility aliases
    @property
    def PROJECT_NAME(self) -> str:
        return self.APP_NAME

    @property
    def API_V1_STR(self) -> str:
        return self.API_V1_PREFIX

    @property
    def SECRET_KEY(self) -> str:
        return self.JWT_SECRET_KEY

    @property
    def ALGORITHM(self) -> str:
        return self.JWT_ALGORITHM

    @property
    def MQTT_BROKER_HOST(self) -> str:
        return self.MQTT_HOST

    @property
    def MQTT_BROKER_PORT(self) -> int:
        return self.MQTT_PORT

    @property
    def MQTT_TOPIC(self) -> str:
        return self.MQTT_TOPIC_PREFIX

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./vehicle_tracking.db",
        description="Database Connection URL (PostgreSQL or SQLite)"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    # JWT Authentication Configuration
    JWT_SECRET_KEY: str = Field(
        default="change_this_to_a_secure_32_character_random_key_for_dev",
        description="Secret key for JWT encoding and decoding"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT Signing Algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=10080, description="Token Expiration in Minutes (default 7 days)")

    # MQTT Configuration
    MQTT_HOST: str = Field(default="localhost", description="MQTT Broker Host")
    MQTT_PORT: int = Field(default=1883, description="MQTT Broker Port")
    MQTT_USERNAME: Optional[str] = Field(default="gps_ingest_user", description="MQTT Broker Username")
    MQTT_PASSWORD: Optional[str] = Field(default="gps_secure_pass_2026", description="MQTT Broker Password")
    MQTT_TOPIC_PREFIX: str = Field(default="vehicles/+/gps", description="MQTT Subscription Topic")
    MQTT_ENABLED: bool = Field(default=True, description="MQTT Service Enabled Flag")

    # GPS Telemetry Thresholds & REST Key
    GPS_INGEST_API_KEY: str = Field(default="dev_gps_ingest_secret_key_2026", description="API Key for REST ingestion")
    GPS_ONLINE_THRESHOLD_SECONDS: int = Field(default=30, description="Threshold in seconds for ONLINE status")
    GPS_STALE_THRESHOLD_SECONDS: int = Field(default=120, description="Threshold in seconds for STALE status")


    # CORS & Security Hardening Configuration
    ALLOWED_ORIGINS: Union[list[str], str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://localhost:8080", "https://gps-9ei6.onrender.com", "*"],
        description="Allowed CORS Origins"
    )
    ALLOWED_HOSTS: Union[list[str], str] = Field(
        default=["localhost", "127.0.0.1", "0.0.0.0", "gps-9ei6.onrender.com", "*"],
        description="Allowed HTTP Host Headers"
    )

    @field_validator("ALLOWED_ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_list_env_var(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                try:
                    import json
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
                except Exception:
                    pass
            if "," in v:
                return [i.strip() for i in v.split(",") if i.strip()]
            return [v]
        return v

    MAX_REQUEST_SIZE_BYTES: int = Field(
        default=2 * 1024 * 1024,
        description="Max allowed request body size in bytes (default 2MB)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_production_configuration(self) -> "Settings":
        """
        Validation logic: Fail clearly when mandatory production configuration is missing or insecure.
        """
        if self.APP_ENV == "production":
            # 1. Enforce secure JWT Secret Key in production
            if not self.JWT_SECRET_KEY or "change_this" in self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: 'JWT_SECRET_KEY' must be set to a secure, random key of at least 32 characters when APP_ENV='production'."
                )
            
            # 2. Enforce PostgreSQL database URL in production
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError(
                    "CONFIGURATION ERROR: Production environment (APP_ENV='production') must use PostgreSQL for 'DATABASE_URL', not SQLite."
                )


        return self

    def safe_dict(self) -> Dict[str, Any]:
        """
        Returns safe, non-sensitive configuration parameters for diagnostic logging or public metadata endpoints.
        Masks secrets like JWT_SECRET_KEY, MQTT_PASSWORD, and Database password.
        """
        db_url_masked = self.DATABASE_URL
        if "@" in db_url_masked:
            # Mask user:password in PostgreSQL connection string
            prefix, rest = db_url_masked.split("@", 1)
            db_url_masked = f"postgresql://***:***@{rest}"

        return {
            "APP_NAME": self.APP_NAME,
            "APP_ENV": self.APP_ENV,
            "DEBUG": self.DEBUG,
            "API_V1_PREFIX": self.API_V1_PREFIX,
            "DATABASE_URL": db_url_masked,
            "JWT_ALGORITHM": self.JWT_ALGORITHM,
            "ACCESS_TOKEN_EXPIRE_MINUTES": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "MQTT_HOST": self.MQTT_HOST,
            "MQTT_PORT": self.MQTT_PORT,
            "MQTT_TOPIC_PREFIX": self.MQTT_TOPIC_PREFIX,
            "MQTT_ENABLED": self.MQTT_ENABLED,
            "MQTT_AUTHENTICATED": bool(self.MQTT_USERNAME and self.MQTT_PASSWORD),
        }

settings = Settings()
