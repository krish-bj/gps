import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_data import init_db_seed
from app.services.mqtt_service import mqtt_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)

    # Seed initial routes, vehicles, users, and telemetry
    db = SessionLocal()
    try:
        init_db_seed(db)
    finally:
        db.close()

    # Start MQTT background service
    mqtt_service.start()

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "status": "ONLINE",
        "docs": f"{settings.API_V1_STR}/docs",
        "api_v1": settings.API_V1_STR
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
