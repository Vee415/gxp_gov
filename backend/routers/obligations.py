from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.system import ObligationResponse, ObligationUpdate, ObligationProgressResponse
from services.obligation_manager import get_obligations, get_obligation_progress, update_obligation

router = APIRouter()


@router.get("/{system_id}/obligations", response_model=list[ObligationResponse])
def list_obligations(system_id: int, db: Session = Depends(get_db)):
    """List all obligations for a system."""
    obligations = get_obligations(db, system_id)
    return obligations


@router.put("/{system_id}/obligations/{obligation_id}", response_model=ObligationResponse)
def update_obligation_status(system_id: int, obligation_id: int, request: ObligationUpdate,
                              db: Session = Depends(get_db)):
    """Update an obligation's status, evidence reference, or notes."""
    obligation = update_obligation(
        db, system_id, obligation_id,
        status=request.status.value if request.status else None,
        evidence_ref=request.evidence_ref,
        notes=request.notes,
    )
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return obligation


@router.get("/{system_id}/obligations/progress", response_model=ObligationProgressResponse)
def obligation_progress(system_id: int, db: Session = Depends(get_db)):
    """Get obligation completion progress for a system."""
    return get_obligation_progress(db, system_id)