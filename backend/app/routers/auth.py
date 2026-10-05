from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, enforce_rate_limit
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"], dependencies=[Depends(enforce_rate_limit)])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Registers a new user and provisions default privacy settings."""
    client_ip = request.client.host if request.client else None
    return AuthService.register_user(db=db, reg_in=user_in, ip_address=client_ip)

@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticates credentials and returns a signed JWT access token."""
    client_ip = request.client.host if request.client else None
    return AuthService.authenticate_user(db=db, login_in=login_in, ip_address=client_ip)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieves profile and authentication metadata for current user."""
    return current_user
