from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.system import ValidationStepResponse, ValidationStepUpdate
from services.validation_steps_manager import (
    get_validation_steps,
    update_validation_step,
    recalculate_phase_status,
    get_validation_detail,
)

router = APIRouter()


@router.get("/{system_id}/validation-steps", response_model=list[ValidationStepResponse])
def list_validation_steps(system_id: int, phase: str = "", db: Session = Depends(get_db)):
    """List validation steps for a system, optionally filtered by phase (IQ/OQ/PQ)."""
    return get_validation_steps(db, system_id, phase if phase else None)


@router.put("/{system_id}/validation-steps/{step_id}", response_model=ValidationStepResponse)
def update_step(system_id: int, step_id: int, request: ValidationStepUpdate,
                db: Session = Depends(get_db)):
    """Update a validation step's status."""
    step = update_validation_step(
        db, system_id, step_id,
        status=request.status.value if request.status else None,
        completed_by=request.completed_by,
        notes=request.notes,
    )
    if not step:
        raise HTTPException(status_code=404, detail="Validation step not found")
    return step


@router.post("/{system_id}/validation-steps/recalculate")
def recalculate(system_id: int, db: Session = Depends(get_db)):
    """Recalculate iq_complete/oq_complete/pq_complete from validation steps."""
    result = recalculate_phase_status(db, system_id)
    if not result:
        raise HTTPException(status_code=404, detail="System not found")
    return result


@router.get("/{system_id}/validation/detail")
def validation_detail(system_id: int, db: Session = Depends(get_db)):
    """Get full validation detail: system + obligations + steps + progress."""
    detail = get_validation_detail(db, system_id)
    if not detail:
        raise HTTPException(status_code=404, detail="System not found")
    return detail