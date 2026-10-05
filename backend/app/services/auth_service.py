import uuid
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, TokenResponse
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.services.protection_service import ProtectionService
from app.services.audit_service import AuditService

class AuthService:
    @staticmethod
    def register_user(db: Session, reg_in: UserRegister, ip_address: Optional[str] = None) -> User:
        existing = db.query(User).filter(User.email == reg_in.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists."
            )

        new_user = User(
            email=reg_in.email.lower(),
            hashed_password=get_password_hash(reg_in.password),
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Initialize default privacy policy
        ProtectionService.get_or_create_default_policy(db, new_user.id)

        # Log audit entry
        AuditService.log(
            db=db,
            action="REGISTER",
            resource_type="USER",
            resource_id=str(new_user.id),
            user_id=new_user.id,
            details={"email": new_user.email},
            ip_address=ip_address
        )

        return new_user

    @staticmethod
    def authenticate_user(db: Session, login_in: UserLogin, ip_address: Optional[str] = None) -> TokenResponse:
        user = db.query(User).filter(User.email == login_in.email.lower()).first()
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account."
            )

        token = create_access_token(data={"sub": str(user.id), "email": user.email})

        # Log audit entry
        AuditService.log(
            db=db,
            action="LOGIN",
            resource_type="USER",
            resource_id=str(user.id),
            user_id=user.id,
            details={"email": user.email},
            ip_address=ip_address
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=3600,
            user_id=user.id
        )
