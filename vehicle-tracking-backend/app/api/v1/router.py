from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, routes, vehicles, telemetry, me

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(me.router, prefix="/me", tags=["Current User & Assignments"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(routes.router, prefix="/routes", tags=["Routes"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(telemetry.router, prefix="/gps/telemetry", tags=["GPS Telemetry"])

