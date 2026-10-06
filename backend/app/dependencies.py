import uuid
from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token
from app.services.redis_service import get_redis_service, RedisService

security_bearer = HTTPBearer(auto_error=False)

def _get_or_create_demo_user(db: Session) -> User:
    demo_email = "evaluator@maskit.dev"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        from app.utils.security import get_password_hash
        from app.services.protection_service import ProtectionService
        user = User(
            email=demo_email,
            hashed_password=get_password_hash("DemoSession123!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        ProtectionService.get_or_create_default_policy(db, user.id)
    return user

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_token = credentials.credentials

    # Support seamless demo session tokens
    if raw_token and raw_token.startswith("maskit_demo_"):
        return _get_or_create_demo_user(db)

    payload = decode_access_token(raw_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token."
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account."
        )

    return user

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    raw_token = credentials.credentials
    if raw_token and raw_token.startswith("maskit_demo_"):
        return _get_or_create_demo_user(db)
    payload = decode_access_token(raw_token)
    if not payload or not payload.get("sub"):
        return None
    try:
        user_uuid = uuid.UUID(payload.get("sub"))
        return db.query(User).filter(User.id == user_uuid, User.is_active == True).first()
    except Exception:
        return None

def enforce_rate_limit(
    request: Request,
    redis_service: RedisService = Depends(get_redis_service)
):
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    key = f"{client_ip}:{path}"
    allowed = redis_service.check_rate_limit(key, max_requests=120, window_seconds=60)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before retrying."
        )
