import json
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("maskit.websocket")
router = APIRouter(tags=["Real-Time Dashboard Streaming"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active listeners: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Active listeners: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        serialized = json.dumps(message)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(serialized)
            except Exception as e:
                logger.warning(f"Error broadcasting to WebSocket: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

async def broadcast_dashboard_event(payload: Dict[str, Any]):
    """Global helper to broadcast real-time telemetry to all connected dashboard clients."""
    await manager.broadcast(payload)

@router.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial confirmation handshake
        await websocket.send_text(json.dumps({
            "event": "CONNECTED",
            "message": "Connected to MaskIt live telemetry stream."
        }))
        while True:
            # Keep connection alive; process client ping/pong
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "PING":
                    await websocket.send_text(json.dumps({"event": "PONG"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket session error: {e}")
        manager.disconnect(websocket)
