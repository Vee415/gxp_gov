import json
from datetime import datetime

from sqlalchemy.orm import Session

from models.system import AISystem, Obligation, ObligationStatus, AuditLog
from regulatory.eu_ai_act_rules import get_obligations_detailed


def get_obligations(db: Session, system_id: int) -> list[Obligation]:
    """Get all obligations for a system."""
    return db.query(Obligation).filter(Obligation.system_id == system_id).order_by(Obligation.id).all()


def get_obligation_progress(db: Session, system_id: int) -> dict:
    """Return obligation completion progress for a system."""
    obligations = get_obligations(db, system_id)
    total = len(obligations)
    if total == 0:
        return {"total": 0, "complete": 0, "in_progress": 0, "not_started": 0, "percentage": 0.0}
    complete = sum(1 for o in obligations if o.status == ObligationStatus.COMPLETE)
    in_progress = sum(1 for o in obligations if o.status == ObligationStatus.IN_PROGRESS)
    not_started = sum(1 for o in obligations if o.status == ObligationStatus.NOT_STARTED)
    return {
        "total": total,
        "complete": complete,
        "in_progress": in_progress,
        "not_started": not_started,
        "percentage": round(complete / total * 100, 1),
    }


def update_obligation(db: Session, system_id: int, obligation_id: int,
                       status: str | None = None, evidence_ref: str | None = None,
                       notes: str | None = None, changed_by: str = "") -> Obligation | None:
    """Update an obligation's status, evidence, or notes. Writes to audit log."""
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id, Obligation.system_id == system_id
    ).first()
    if not obligation:
        return None

    old_values = {"status": obligation.status, "evidence_ref": obligation.evidence_ref, "notes": obligation.notes}

    if status is not None:
        obligation.status = status
    if evidence_ref is not None:
        obligation.evidence_ref = evidence_ref
    if notes is not None:
        obligation.notes = notes

    obligation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obligation)

    new_values = {"status": obligation.status, "evidence_ref": obligation.evidence_ref, "notes": obligation.notes}

    audit = AuditLog(
        system_id=system_id,
        action="obligation_updated",
        entity_type="obligation",
        entity_id=obligation_id,
        old_value=json.dumps(old_values),
        new_value=json.dumps(new_values),
        changed_by=changed_by,
    )
    db.add(audit)
    db.commit()

    return obligation


def sync_obligations_from_classification(db: Session, system_id: int, risk_tier: str) -> list[Obligation]:
    """Create obligation rows for a system based on its risk tier.
    Deletes existing obligations first (re-sync on re-classification)."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        return []

    # Delete existing obligations for this system
    db.query(Obligation).filter(Obligation.system_id == system_id).delete()
    db.flush()

    # Get obligation definitions for this risk tier
    obligation_defs = get_obligations_detailed(risk_tier)
    new_obligations = []
    for obl_def in obligation_defs:
        obl = Obligation(
            system_id=system_id,
            article=obl_def["article"],
            obligation=obl_def["obligation"],
            category=obl_def.get("category", ""),
            required=obl_def.get("required", True),
            status=ObligationStatus.NOT_STARTED,
        )
        db.add(obl)
        new_obligations.append(obl)

    # Update obligations_synced_at on the system
    system.obligations_synced_at = datetime.utcnow()
    db.commit()

    for obl in new_obligations:
        db.refresh(obl)

    return new_obligations