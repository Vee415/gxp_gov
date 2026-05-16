from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.system import AISystem, AuditLogResponse
from services.change_control import record_version_change, get_audit_log, check_and_flag_overdue_reviews

router = APIRouter()


class VersionChangeRequest(BaseModel):
    new_version: str
    changed_by: str = ""
    notes: str = ""


@router.get("/{system_id}/audit-log", response_model=list[AuditLogResponse])
def list_audit_log(system_id: int, entity_type: str = "", db: Session = Depends(get_db)):
    """Get audit trail for a system."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return get_audit_log(db, system_id, entity_type if entity_type else None)


@router.post("/{system_id}/version-change")
def version_change(system_id: int, request: VersionChangeRequest, db: Session = Depends(get_db)):
    """Record a model version change. Triggers revalidation if version changed."""
    system = record_version_change(db, system_id, request.new_version, request.changed_by, request.notes)
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return {
        "id": system.id,
        "name": system.name,
        "version": system.version,
        "previous_version": system.previous_version,
        "validation_status": system.validation_status,
    }


@router.post("/check-overdue")
def check_overdue_reviews(db: Session = Depends(get_db)):
    """Check all systems for overdue reviews and flag them as requiring revalidation."""
    flagged = check_and_flag_overdue_reviews(db)
    return {
        "flagged_count": len(flagged),
        "flagged_systems": [{"id": s.id, "name": s.name} for s in flagged],
    }