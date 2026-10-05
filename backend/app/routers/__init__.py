from app.routers.auth import router as auth_router
from app.routers.session import router as session_router
from app.routers.protection import router as protection_router
from app.routers.extension import router as extension_router
from app.routers.fingerprint import router as fingerprint_router
from app.routers.policies import router as policies_router
from app.routers.events import router as events_router
from app.routers.dashboard import router as dashboard_router
from app.routers.audit import router as audit_router
from app.routers.health import router as health_router
from app.routers.websocket import router as websocket_router, broadcast_dashboard_event

__all__ = [
    "auth_router",
    "session_router",
    "protection_router",
    "extension_router",
    "fingerprint_router",
    "policies_router",
    "events_router",
    "dashboard_router",
    "audit_router",
    "health_router",
    "websocket_router",
    "broadcast_dashboard_event"
]
