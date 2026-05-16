from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.system import AISystem, ValidationStatus
from services.validation_tracker import get_compliance_flags, get_validation_summary
from regulatory.ema_guidance import get_ema_checks, get_relevant_checks, get_lifecycle_stages

router = APIRouter()


class ValidationUpdateRequest(BaseModel):
    iq_complete: bool | None = None
    oq_complete: bool | None = None
    pq_complete: bool | None = None
    validation_status: ValidationStatus | None = None


@router.get("/")
def list_validation_status(db: Session = Depends(get_db)):
    systems = db.query(AISystem).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "validation_status": s.validation_status,
            "iq_complete": s.iq_complete,
            "oq_complete": s.oq_complete,
            "pq_complete": s.pq_complete,
            "next_review_date": s.next_review_date,
        }
        for s in systems
    ]


@router.get("/flags")
def list_flags(db: Session = Depends(get_db)):
    return get_compliance_flags(db)


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return get_validation_summary(db)


@router.put("/{system_id}")
def update_validation(system_id: int, request: ValidationUpdateRequest, db: Session = Depends(get_db)):
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="System not found")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(system, key, value)
    db.commit()
    db.refresh(system)
    return {
        "id": system.id,
        "name": system.name,
        "validation_status": system.validation_status,
        "iq_complete": system.iq_complete,
        "oq_complete": system.oq_complete,
        "pq_complete": system.pq_complete,
    }


@router.get("/ema-checks")
def ema_validation_checks(use_case: str = "", category: str = ""):
    """Return EMA/CHMP validation checks, optionally filtered by category or use case."""
    if use_case:
        return get_relevant_checks(use_case)
    return get_ema_checks(category if category else None)


@router.get("/ema-lifecycle")
def ema_lifecycle_stages():
    """Return the 7 EMA lifecycle stages for AI in medicines development."""
    return get_lifecycle_stages()