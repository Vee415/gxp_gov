import json
from datetime import datetime

from sqlalchemy.orm import Session

from models.system import AISystem, AuditLog, ValidationStatus
from services.validation_tracker import is_review_overdue


def record_version_change(db: Session, system_id: int, new_version: str,
                           changed_by: str = "", notes: str = "") -> AISystem | None:
    """Record a model version change. If version changed, trigger revalidation."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        return None

    old_version = system.version
    previous_version = system.previous_version or old_version

    # Record audit log
    audit = AuditLog(
        system_id=system_id,
        action="version_changed" if old_version != new_version else "version_recorded",
        entity_type="system",
        entity_id=system_id,
        old_value=json.dumps({"version": old_version, "previous_version": previous_version}),
        new_value=json.dumps({"version": new_version, "previous_version": old_version}),
        changed_by=changed_by,
    )
    db.add(audit)

    # Update version fields
    system.previous_version = old_version
    system.version = new_version

    # If version actually changed, trigger revalidation
    if old_version != new_version:
        system.validation_status = ValidationStatus.REQUIRES_REVALIDATION

        # Log revalidation trigger
        reval_audit = AuditLog(
            system_id=system_id,
            action="revalidation_triggered",
            entity_type="system",
            entity_id=system_id,
            old_value=json.dumps({"validation_status": system.validation_status}),
            new_value=json.dumps({"validation_status": "requires_revalidation", "reason": "version_change"}),
            changed_by=changed_by,
        )
        db.add(reval_audit)

    if notes:
        system.description = (system.description or "") + f"\n[Version change: {old_version} → {new_version}] {notes}"

    system.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(system)
    return system


def check_and_flag_overdue_reviews(db: Session) -> list[AISystem]:
    """Check all systems for overdue reviews and flag them. Returns list of flagged systems."""
    systems = db.query(AISystem).all()
    flagged = []
    for system in systems:
        if is_review_overdue(system) and system.validation_status != ValidationStatus.REQUIRES_REVALIDATION:
            old_status = system.validation_status
            system.validation_status = ValidationStatus.REQUIRES_REVALIDATION
            system.updated_at = datetime.utcnow()

            audit = AuditLog(
                system_id=system.id,
                action="revalidation_triggered",
                entity_type="system",
                entity_id=system.id,
                old_value=json.dumps({"validation_status": old_status}),
                new_value=json.dumps({"validation_status": "requires_revalidation", "reason": "overdue_review"}),
                changed_by="system",
            )
            db.add(audit)
            flagged.append(system)

    db.commit()
    return flagged


def get_audit_log(db: Session, system_id: int, entity_type: str | None = None) -> list[AuditLog]:
    """Get audit trail for a system, optionally filtered by entity type."""
    query = db.query(AuditLog).filter(AuditLog.system_id == system_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    return query.order_by(AuditLog.changed_at.desc()).all()