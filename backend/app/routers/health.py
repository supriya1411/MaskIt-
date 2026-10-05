from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.services.redis_service import get_redis_service, RedisService

router = APIRouter(tags=["Health & Diagnostics"])

@router.get("/health")
def health_check(
    response: Response,
    db: Session = Depends(get_db),
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Actively checks PostgreSQL database connectivity and Redis status.
    Returns 200 if database is healthy; gracefully flags redis status.
    """
    # 1. Check PostgreSQL
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"

    # 2. Check Redis
    redis_connected = redis_service.ping()
    redis_status = "connected" if redis_connected else "fallback_memory_mode"

    overall_healthy = (db_status == "connected")
    if not overall_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
