from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, routes, vehicles, telemetry, me, ws_tracking

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(me.router, prefix="/me", tags=["Tracking"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(routes.router, prefix="/routes", tags=["Tracking"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Tracking"])
api_router.include_router(telemetry.router, prefix="/gps", tags=["GPS"])
api_router.include_router(ws_tracking.router, tags=["Tracking"])
