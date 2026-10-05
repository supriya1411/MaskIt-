import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.protection import (
    SiteProtectRequest, SiteUpdateRequest, SiteResponse,
    ProtectionSummary, SiteAnalytics
)
from app.services.protection_service import ProtectionService
from app.services.audit_service import AuditService
from app.routers.websocket import broadcast_dashboard_event

router = APIRouter(prefix="/protection", tags=["Protect My Data"])

def _to_site_response(site) -> SiteResponse:
    return SiteResponse(
        id=site.id,
        domain=site.domain,
        enabled=site.enabled,
        status="ACTIVE" if site.enabled else "PAUSED",
        policy_id=site.policy_id,
        created_at=site.created_at,
        updated_at=site.updated_at,
        last_activity_at=site.last_activity_at
    )

@router.post("/sites", response_model=SiteResponse, status_code=201)
async def protect_site(
    payload: SiteProtectRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🛡️ PROTECT MY DATA: Registers a domain (e.g. youtube.com) for fingerprint protection.
    Creates a real rule stored in PostgreSQL and broadcasts real-time event.
    """
    try:
        site = ProtectionService.add_site(
            db=db,
            user_id=current_user.id,
            raw_domain=payload.domain,
            policy_id=payload.policy_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    AuditService.log(
        db=db,
        action="SITE_PROTECTED",
        resource_type="SITE",
        resource_id=str(site.id),
        user_id=current_user.id,
        details={"domain": site.domain},
        ip_address=request.client.host if request.client else None
    )

    # Real-time WebSocket broadcast to live dashboard
    await broadcast_dashboard_event({
        "event": "SITE_PROTECTED",
        "domain": site.domain,
        "site_id": str(site.id),
        "status": "ACTIVE",
        "action": "SHIELD_ENABLED",
        "user_id": str(current_user.id)
    })

    return _to_site_response(site)

@router.get("/sites", response_model=List[SiteResponse])
def get_protected_sites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns only the authenticated user's registered protected domains."""
    sites = ProtectionService.get_user_sites(db=db, user_id=current_user.id)
    return [_to_site_response(s) for s in sites]

@router.put("/sites/{site_id}", response_model=SiteResponse)
async def update_protected_site(
    site_id: uuid.UUID,
    payload: SiteUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates status (pause/resume) or policy association for a protected site."""
    updated = ProtectionService.update_site(
        db=db,
        user_id=current_user.id,
        site_id=site_id,
        enabled=payload.enabled,
        policy_id=payload.policy_id
    )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found.")

    AuditService.log(
        db=db,
        action="SITE_UPDATED",
        resource_type="SITE",
        resource_id=str(updated.id),
        user_id=current_user.id,
        details={"domain": updated.domain, "enabled": updated.enabled}
    )

    await broadcast_dashboard_event({
        "event": "SITE_STATUS_CHANGED",
        "domain": updated.domain,
        "site_id": str(updated.id),
        "status": "ACTIVE" if updated.enabled else "PAUSED",
        "user_id": str(current_user.id)
    })

    return _to_site_response(updated)

@router.delete("/sites/{site_id}", status_code=204)
async def delete_protected_site(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Removes a domain from the user's protection shield."""
    site = ProtectionService.get_site(db=db, user_id=current_user.id, site_id=site_id)
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found.")

    domain = site.domain
    deleted = ProtectionService.delete_site(db=db, user_id=current_user.id, site_id=site_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found.")

    AuditService.log(
        db=db,
        action="SITE_UNPROTECTED",
        resource_type="SITE",
        resource_id=str(site_id),
        user_id=current_user.id,
        details={"domain": domain}
    )

    await broadcast_dashboard_event({
        "event": "SITE_UNPROTECTED",
        "domain": domain,
        "site_id": str(site_id),
        "action": "SHIELD_REMOVED",
        "user_id": str(current_user.id)
    })

    return None

@router.get("/summary", response_model=ProtectionSummary)
def get_protection_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculates real-time protection summary metrics from PostgreSQL."""
    return ProtectionService.get_summary(db=db, user_id=current_user.id)

@router.get("/sites/{site_id}/analytics", response_model=SiteAnalytics)
def get_site_analytics(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns granular signal interception and risk analytics for a specific site."""
    analytics = ProtectionService.get_site_analytics(db=db, user_id=current_user.id, site_id=site_id)
    if not analytics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found.")
    return analytics
