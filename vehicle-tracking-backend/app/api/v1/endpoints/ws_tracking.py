import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.orm import Session
import jwt

from app.db.session import SessionLocal, get_db
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.services.assignment_service import AssignmentService
from app.services.tracking_service import TrackingService
from app.exceptions.custom_exceptions import ForbiddenAccessException, EntityNotFoundException

logger = logging.getLogger("ws_tracking")

router = APIRouter()

class ConnectionManager:
    """
    Manages active WebSocket connections for live vehicle tracking updates.
    """
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Remaining connections: {len(self.active_connections)}")

manager = ConnectionManager()

def authenticate_ws_user(db: Session, token: Optional[str]):
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None
        user_id = int(user_id_str)
        user_repo = UserRepository(db)
        user = user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            return None
        return user
    except Exception:
        return None

@router.websocket("/ws/tracking")
async def websocket_tracking(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="JWT Bearer Token for WS authentication")
):
    """
    WS /api/v1/ws/tracking?token=<JWT_TOKEN>
    Optional WebSocket bonus endpoint for real-time live vehicle tracking stream.
    Strictly authenticates user via JWT token, loads backend assignment (never trusts client parameters),
    and streams live location updates for the assigned vehicle.
    """
    db = SessionLocal()
    try:
        user = authenticate_ws_user(db, token)
        if not user:
            logger.warning("WebSocket connection rejected: Invalid or missing JWT token.")
            await websocket.close(code=1008, reason="Unauthorized: Invalid or missing token")
            return

        assignment_service = AssignmentService(db)
        try:
            assigned_details = assignment_service.get_user_assigned_details(user)
            assigned_vehicle = assigned_details["vehicle"]
        except (ForbiddenAccessException, EntityNotFoundException) as e:
            logger.warning(f"WebSocket connection rejected for user '{user.email}': {e.detail}")
            await websocket.close(code=1008, reason=f"Forbidden: {e.detail}")
            return

        await manager.connect(websocket)

        # Send initial location state on connect
        tracking_service = TrackingService(db)
        current_loc = tracking_service.get_my_current_location(user)
        await websocket.send_json({
            "event": "LOCATION_UPDATE",
            "data": current_loc.model_dump(mode="json")
        })

        # Periodic streaming loop while client remains connected
        last_recorded_at = None
        while True:
            await asyncio.sleep(3) # Poll current state every 3 seconds
            
            # Create fresh DB session for long-running socket loop
            db.refresh(assigned_vehicle)
            current_loc = tracking_service.get_my_current_location(user)
            
            await websocket.send_json({
                "event": "LOCATION_UPDATE",
                "data": current_loc.model_dump(mode="json")
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket connection closed cleanly by client.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        try:
            await websocket.close(code=1011, reason="Internal Server Error")
        except Exception:
            pass
    finally:
        db.close()
