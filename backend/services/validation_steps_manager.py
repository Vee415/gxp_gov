import json
from datetime import date, datetime

from sqlalchemy.orm import Session

from models.system import AISystem, ValidationStep, StepStatus, AuditLog, ValidationStatus
from regulatory.gmlp_steps import get_gmlp_steps


def get_validation_steps(db: Session, system_id: int, phase: str | None = None) -> list[ValidationStep]:
    """Get validation steps for a system, optionally filtered by phase."""
    query = db.query(ValidationStep).filter(ValidationStep.system_id == system_id)
    if phase:
        query = query.filter(ValidationStep.phase == phase.upper())
    return query.order_by(ValidationStep.phase, ValidationStep.sort_order).all()


def update_validation_step(db: Session, system_id: int, step_id: int,
                            status: str | None = None, completed_by: str | None = None,
                            notes: str | None = None, changed_by: str = "") -> ValidationStep | None:
    """Update a validation step's status. Auto-sets completed_at and writes audit log."""
    step = db.query(ValidationStep).filter(
        ValidationStep.id == step_id, ValidationStep.system_id == system_id
    ).first()
    if not step:
        return None

    old_status = step.status

    if status is not None:
        step.status = status
        if status == StepStatus.COMPLETE and not step.completed_at:
            step.completed_at = date.today()
            step.completed_by = completed_by or ""
        elif status != StepStatus.COMPLETE:
            step.completed_at = None
            step.completed_by = None

    if notes is not None:
        step.notes = notes

    step.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(step)

    audit = AuditLog(
        system_id=system_id,
        action="step_updated",
        entity_type="validation_step",
        entity_id=step_id,
        old_value=json.dumps({"status": old_status}),
        new_value=json.dumps({"status": step.status, "completed_by": step.completed_by}),
        changed_by=changed_by,
    )
    db.add(audit)
    db.commit()

    # Recalculate phase booleans on AISystem
    recalculate_phase_status(db, system_id)

    return step


def recalculate_phase_status(db: Session, system_id: int) -> dict:
    """Recalculate iq_complete, oq_complete, pq_complete from validation_steps.
    Also updates validation_status on AISystem."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        return {}

    steps = db.query(ValidationStep).filter(ValidationStep.system_id == system_id).all()

    phases = {"IQ": [], "OQ": [], "PQ": []}
    for step in steps:
        if step.phase in phases:
            phases[step.phase].append(step.status == StepStatus.COMPLETE)

    iq_complete = all(phases["IQ"]) if phases["IQ"] else system.iq_complete
    oq_complete = all(phases["OQ"]) if phases["OQ"] else system.oq_complete
    pq_complete = all(phases["PQ"]) if phases["PQ"] else system.pq_complete

    system.iq_complete = iq_complete
    system.oq_complete = oq_complete
    system.pq_complete = pq_complete

    # Determine validation_status based on step progress
    total_steps = len(steps)
    completed_steps = sum(1 for s in steps if s.status == StepStatus.COMPLETE)

    if total_steps == 0:
        pass  # Keep existing status
    elif completed_steps == 0:
        system.validation_status = ValidationStatus.NOT_STARTED
    elif completed_steps == total_steps:
        from services.validation_tracker import is_review_overdue
        if is_review_overdue(system):
            system.validation_status = ValidationStatus.REQUIRES_REVALIDATION
        else:
            system.validation_status = ValidationStatus.VALIDATED
    else:
        system.validation_status = ValidationStatus.IN_PROGRESS

    system.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(system)

    return {
        "iq_complete": iq_complete,
        "oq_complete": oq_complete,
        "pq_complete": pq_complete,
        "validation_status": system.validation_status,
    }


def create_validation_steps_from_tier(db: Session, system_id: int, risk_tier: str) -> list[ValidationStep]:
    """Create validation step rows from GMLP_STEPS for the given risk tier.
    Deletes existing steps first (re-sync on re-classification)."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        return []

    # Delete existing steps for this system
    db.query(ValidationStep).filter(ValidationStep.system_id == system_id).delete()
    db.flush()

    step_templates = get_gmlp_steps(risk_tier)
    new_steps = []
    for phase, steps in step_templates.items():
        for step_def in steps:
            vs = ValidationStep(
                system_id=system_id,
                phase=phase,
                step_key=step_def["step_key"],
                step_label=step_def["step_label"],
                source=step_def.get("source", ""),
                sort_order=step_def.get("sort_order", 0),
                status=StepStatus.NOT_STARTED,
            )
            db.add(vs)
            new_steps.append(vs)

    db.commit()
    for vs in new_steps:
        db.refresh(vs)

    # Recalculate phase booleans
    recalculate_phase_status(db, system_id)

    return new_steps


def get_validation_detail(db: Session, system_id: int) -> dict | None:
    """Return full validation detail: system + obligations + steps + progress."""
    from services.obligation_manager import get_obligations, get_obligation_progress

    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        return None

    steps = get_validation_steps(db, system_id)
    obligations = get_obligations(db, system_id)
    obligation_progress = get_obligation_progress(db, system_id)

    phases = {"IQ": [], "OQ": [], "PQ": []}
    for step in steps:
        if step.phase in phases:
            phases[step.phase].append({
                "id": step.id,
                "step_key": step.step_key,
                "step_label": step.step_label,
                "source": step.source,
                "sort_order": step.sort_order,
                "status": step.status,
                "completed_at": str(step.completed_at) if step.completed_at else None,
                "completed_by": step.completed_by,
            })

    return {
        "system_id": system.id,
        "name": system.name,
        "risk_tier": system.risk_tier,
        "validation_status": system.validation_status,
        "iq_complete": system.iq_complete,
        "oq_complete": system.oq_complete,
        "pq_complete": system.pq_complete,
        "obligation_progress": obligation_progress,
        "phases": phases,
    }