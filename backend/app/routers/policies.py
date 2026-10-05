import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/policies", tags=["Masking Policies"])

@router.get("", response_model=List[PolicyResponse])
def list_policies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists all custom and default masking policies available to the user."""
    return db.query(Policy).filter(
        (Policy.user_id == current_user.id) | (Policy.user_id == None)
    ).all()

@router.post("", response_model=PolicyResponse, status_code=201)
def create_policy(
    payload: PolicyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a custom masking policy (STATIC, DISTRIBUTION_SAMPLED, or AI_GENERATED)."""
    policy = Policy(
        user_id=current_user.id,
        name=payload.name,
        enabled=payload.enabled,
        masking_strength=payload.masking_strength,
        protected_signals=payload.protected_signals,
        strategy=payload.strategy,
        session_persistence=payload.session_persistence,
        rules_json=payload.rules_json
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)

    AuditService.log(
        db=db,
        action="POLICY_CREATED",
        resource_type="POLICY",
        resource_id=str(policy.id),
        user_id=current_user.id,
        details={"name": policy.name, "strategy": policy.strategy}
    )

    return policy

@router.put("/{policy_id}", response_model=PolicyResponse)
def update_policy(
    policy_id: uuid.UUID,
    payload: PolicyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates an existing masking policy's rules and parameters."""
    policy = db.query(Policy).filter(
        Policy.id == policy_id,
        Policy.user_id == current_user.id
    ).first()

    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found or unauthorized to modify."
        )

    if payload.name is not None:
        policy.name = payload.name
    if payload.enabled is not None:
        policy.enabled = payload.enabled
    if payload.masking_strength is not None:
        policy.masking_strength = payload.masking_strength
    if payload.protected_signals is not None:
        policy.protected_signals = payload.protected_signals
    if payload.strategy is not None:
        policy.strategy = payload.strategy
    if payload.session_persistence is not None:
        policy.session_persistence = payload.session_persistence
    if payload.rules_json is not None:
        policy.rules_json = payload.rules_json

    db.commit()
    db.refresh(policy)

    AuditService.log(
        db=db,
        action="POLICY_UPDATED",
        resource_type="POLICY",
        resource_id=str(policy.id),
        user_id=current_user.id,
        details={"name": policy.name}
    )

    return policy
