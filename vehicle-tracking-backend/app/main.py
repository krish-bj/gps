import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.services.seed_service import SeedService
from app.mqtt.client import mqtt_client
from app.exceptions.custom_exceptions import VehicleTrackingException
from app.exceptions.handlers import register_exception_handlers

from app.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger("fastapi_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} (Environment: {settings.APP_ENV})...")

    # 1. Initialize DB tables
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    # 2. Seed initial data
    db = SessionLocal()
    try:
        seeder = SeedService(db)
        seeder.seed_initial_data()
    finally:
        db.close()

    # 3. Start MQTT Client listener
    mqtt_client.start()

    logger.info("FastAPI application startup complete and ready to serve requests.")
    yield

    # 4. Clean shutdown for background services
    logger.info("Application shutdown initiated. Stopping background services...")
    mqtt_client.stop()
    logger.info("Application shutdown complete.")



from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.middleware import SecurityHeadersMiddleware, RequestSizeLimitMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 1. Environment-Aware CORS Middleware Configuration
cors_origins = settings.ALLOWED_ORIGINS
allow_credentials = True
if "*" in cors_origins and settings.APP_ENV == "production":
    cors_origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Trusted Host Header Middleware
if "*" not in settings.ALLOWED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# 3. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 4. Request Size Limit Middleware
app.add_middleware(RequestSizeLimitMiddleware)


# Centralized Exception Handlers (Standardized error payloads & leak prevention)
register_exception_handlers(app)


from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Production-ready REST & MQTT GPS Vehicle Tracking System API featuring multi-user access isolation, JWT authentication, Mosquitto MQTT ingestion, and automated seeder.",
        routes=app.routes,
    )

    openapi_schema["tags"] = [
        {"name": "Authentication", "description": "User authentication, JWT token issuance & profile login APIs."},
        {"name": "Tracking", "description": "User assigned route, vehicle, live tracking summary, and history APIs."},
        {"name": "GPS", "description": "Device GPS telemetry ingestion endpoints over REST & MQTT."},
        {"name": "Users", "description": "User management & profile retrieval APIs."},
        {"name": "Health", "description": "System health check and diagnostic status APIs."},
    ]

    # Configure JWT Bearer Security Scheme for Swagger UI
    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter JWT Bearer token obtained from `POST /api/v1/auth/login`"
    }

    # Attach BearerAuth security scheme to non-public endpoints
    for path, methods in openapi_schema.get("paths", {}).items():
        for method, config in methods.items():
            if not path.endswith("/auth/login") and not path.endswith("/health") and path != "/" and path != f"{settings.API_V1_STR}/gps":
                config.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Health Check Endpoint (Root & /health)
@app.get("/health", tags=["Health"], summary="System Health Check", description="Returns operational health status of the backend API service.")
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

@app.get("/", tags=["Health"], summary="API Root Metadata", description="Returns system root metadata and documentation links.")
def root_check():
    return {
        "system": settings.PROJECT_NAME,
        "status": "ONLINE",
        "health": "/health",
        "docs": f"{settings.API_V1_STR}/docs",
        "api_v1": settings.API_V1_STR
    }

# Include Versioned API Router (/api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)

