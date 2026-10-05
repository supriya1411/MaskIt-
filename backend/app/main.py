import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist (graceful initial bootstrap)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database schema initialization warning (Alembic managed in production): {e}")
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

@app.get("/")
def root():
    return {
        "service": "MaskIt Privacy Shield Backend",
        "status": "online",
        "docs": "/docs",
        "api_v1": api_v1_prefix
    }
