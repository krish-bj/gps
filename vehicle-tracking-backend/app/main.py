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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
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

    yield

    # 4. Clean shutdown for background services
    logger.info("Shutting down background services...")
    mqtt_client.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Custom Exception Handler
@app.exception_handler(VehicleTrackingException)
async def vehicle_tracking_exception_handler(request: Request, exc: VehicleTrackingException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

# Health Check Endpoint (Root & /health)
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

@app.get("/", tags=["Health"])
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
