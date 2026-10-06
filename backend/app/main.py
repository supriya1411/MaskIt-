import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.database import Base, engine
from app.routers import (
    auth_router,
    session_router,
    protection_router,
    extension_router,
    fingerprint_router,
    policies_router,
    events_router,
    dashboard_router,
    audit_router,
    health_router,
    websocket_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("maskit.api")
settings = get_settings()

# Resolve the frontend dist directory (built React app)
# Expected at: <project_root>/dist (one level up from backend/)
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "dist"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist (graceful initial bootstrap)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database schema initialization warning (Alembic managed in production): {e}")

    if FRONTEND_DIST.exists():
        logger.info(f"Serving frontend from: {FRONTEND_DIST}")
    else:
        logger.warning(f"Frontend dist not found at {FRONTEND_DIST}. Run 'npm run build' in the project root.")

    yield
    logger.info("Shutting down MaskIt backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Production-grade backend for MaskIt — AI-Powered Browser Fingerprint Privacy Shield. "
                "Calculates deterministic risk scores, coordinates extension masking policies, "
                "records privacy-safe telemetry, and powers the live real-time dashboard.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
origins = settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": str(exc.body)}
    )

# Generic exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please consult backend logs."}
    )

# Mount Health router at root
app.include_router(health_router)

# Mount WebSocket router at root
app.include_router(websocket_router)

# Mount API v1 Routers
api_v1_prefix = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(session_router, prefix=api_v1_prefix)
app.include_router(protection_router, prefix=api_v1_prefix)
app.include_router(extension_router, prefix=api_v1_prefix)
app.include_router(fingerprint_router, prefix=api_v1_prefix)
app.include_router(policies_router, prefix=api_v1_prefix)
app.include_router(events_router, prefix=api_v1_prefix)
app.include_router(dashboard_router, prefix=api_v1_prefix)
app.include_router(audit_router, prefix=api_v1_prefix)

# ---------------------------------------------------------------------------
# Serve the React frontend (built dist/ folder) on the SAME port
# ---------------------------------------------------------------------------
if FRONTEND_DIST.exists():
    # Mount static assets (JS, CSS, images) under /assets
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="frontend-assets")

    # Serve index.html for the root and all non-API frontend routes (SPA catch-all)
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        # Try to serve a static file first (e.g. favicon.ico, manifest.json)
        static_file = FRONTEND_DIST / full_path
        if full_path and static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        # Fall back to index.html for client-side routing
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse(
            status_code=404,
            content={"detail": "Frontend not found. Run 'npm run build'."}
        )
else:
    @app.get("/")
    def root():
        return {
            "service": "MaskIt Privacy Shield Backend",
            "status": "online",
            "docs": "/docs",
            "api_v1": api_v1_prefix,
            "note": "Frontend active and served from dist."
        }
# Reload timestamp: 2026-10-06T10:01:25

