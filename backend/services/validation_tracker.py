from datetime import date

from sqlalchemy.orm import Session

from models.system import AISystem, ValidationStatus


def is_compliant(system: AISystem) -> bool:
    if not system.iq_complete or not system.oq_complete or not system.pq_complete:
        return False
    if is_review_overdue(system):
        return False
    return True


def is_review_overdue(system: AISystem) -> bool:
    """Check if a system's review is overdue."""
    return bool(system.next_review_date and system.next_review_date < date.today())


def get_compliance_flags(db: Session) -> list[dict]:
    systems = db.query(AISystem).all()
    flags = []
    for system in systems:
        issues = []
        if not system.iq_complete:
            issues.append("IQ not complete")
        if not system.oq_complete:
            issues.append("OQ not complete")
        if not system.pq_complete:
            issues.append("PQ not complete")
        if system.next_review_date and system.next_review_date < date.today():
            issues.append("Overdue for revalidation")
        if system.validation_status == ValidationStatus.REQUIRES_REVALIDATION:
            issues.append("Requires revalidation")

        if issues:
            severity = "critical" if (not system.oq_complete and system.validation_status != ValidationStatus.NOT_STARTED) else "warning"
            flags.append({
                "id": system.id,
                "name": system.name,
                "risk_tier": system.risk_tier,
                "validation_status": system.validation_status,
                "issues": issues,
                "severity": severity,
            })
    return flags


def get_validation_summary(db: Session) -> dict:
    systems = db.query(AISystem).all()
    total = len(systems)
    summary = {
        "total_systems": total,
        "validated": 0,
        "in_progress": 0,
        "not_started": 0,
        "requires_revalidation": 0,
        "flagged": 0,
    }
    for system in systems:
        match system.validation_status:
            case ValidationStatus.VALIDATED:
                summary["validated"] += 1
            case ValidationStatus.IN_PROGRESS:
                summary["in_progress"] += 1
            case ValidationStatus.NOT_STARTED:
                summary["not_started"] += 1
            case ValidationStatus.REQUIRES_REVALIDATION:
                summary["requires_revalidation"] += 1
        if not is_compliant(system):
            summary["flagged"] += 1
    return summary