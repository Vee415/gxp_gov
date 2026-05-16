"""Tests for validation tracker, validation steps, obligations, and change control."""
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

from models.system import (
    AISystem, Obligation, ObligationStatus, ValidationStep, StepStatus,
    ValidationStatus, RiskTier, AuditLog,
)
from services.validation_tracker import is_compliant, is_review_overdue, get_compliance_flags
from services.validation_steps_manager import (
    create_validation_steps_from_tier,
    recalculate_phase_status,
    get_validation_steps,
    update_validation_step,
)
from services.obligation_manager import (
    sync_obligations_from_classification,
    get_obligation_progress,
    update_obligation,
)
from services.change_control import record_version_change, check_and_flag_overdue_reviews


@pytest.fixture
def db():
    """Create a fresh in-memory database session for each test."""
    from database import Base, engine, SessionLocal
    from models.system import AISystem  # ensure models are imported
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def make_system(db, **kwargs):
    """Helper to create a test AISystem."""
    defaults = {
        "name": "Test System",
        "vendor": "TestVendor",
        "version": "1.0.0",
        "use_case": "AI-assisted diagnosis in cardiology",
        "risk_tier": RiskTier.HIGH,
        "annex": "III",
        "validation_status": ValidationStatus.NOT_STARTED,
        "iq_complete": False,
        "oq_complete": False,
        "pq_complete": False,
    }
    defaults.update(kwargs)
    system = AISystem(**defaults)
    db.add(system)
    db.commit()
    db.refresh(system)
    return system


class TestValidationTracker:
    """Test compliance checking and flagging."""

    def test_fully_compliant_system(self, db):
        system = make_system(db, iq_complete=True, oq_complete=True, pq_complete=True,
                             next_review_date=date.today() + timedelta(days=365))
        assert is_compliant(system) is True

    def test_missing_oq_not_compliant(self, db):
        system = make_system(db, iq_complete=True, oq_complete=False, pq_complete=True)
        assert is_compliant(system) is False

    def test_overdue_review_not_compliant(self, db):
        system = make_system(db, iq_complete=True, oq_complete=True, pq_complete=True,
                             next_review_date=date.today() - timedelta(days=30))
        assert is_compliant(system) is False

    def test_is_review_overdue(self, db):
        system = make_system(db, next_review_date=date.today() - timedelta(days=1))
        assert is_review_overdue(system) is True

    def test_is_review_not_overdue(self, db):
        system = make_system(db, next_review_date=date.today() + timedelta(days=30))
        assert is_review_overdue(system) is False

    def test_no_review_date_not_overdue(self, db):
        system = make_system(db, next_review_date=None)
        assert is_review_overdue(system) is False

    def test_compliance_flags_critical_severity(self, db):
        """OQ incomplete on a system that's not NOT_STARTED should be critical."""
        system = make_system(db, validation_status=ValidationStatus.IN_PROGRESS,
                             iq_complete=True, oq_complete=False, pq_complete=False)
        flags = get_compliance_flags(db)
        assert any(f["id"] == system.id and f["severity"] == "critical" for f in flags)

    def test_compliance_flags_warning_severity(self, db):
        """NOT_STARTED systems with incomplete IQ should be warning, not critical."""
        system = make_system(db, validation_status=ValidationStatus.NOT_STARTED)
        flags = get_compliance_flags(db)
        flag = next((f for f in flags if f["id"] == system.id), None)
        if flag:
            assert flag["severity"] == "warning"


class TestValidationSteps:
    """Test GMLP validation step creation and recalculation."""

    def test_create_high_risk_steps(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        steps = create_validation_steps_from_tier(db, system.id, "HIGH")
        assert len(steps) == 13  # 4 IQ + 5 OQ + 4 PQ

    def test_create_limited_risk_steps(self, db):
        system = make_system(db, risk_tier=RiskTier.LIMITED)
        steps = create_validation_steps_from_tier(db, system.id, "LIMITED")
        assert len(steps) == 9  # 3 IQ + 3 OQ + 3 PQ

    def test_create_minimal_risk_steps(self, db):
        system = make_system(db, risk_tier=RiskTier.MINIMAL)
        steps = create_validation_steps_from_tier(db, system.id, "MINIMAL")
        assert len(steps) == 2  # Only IQ steps

    def test_create_unacceptable_no_steps(self, db):
        system = make_system(db, risk_tier=RiskTier.UNACCEPTABLE)
        steps = create_validation_steps_from_tier(db, system.id, "UNACCEPTABLE")
        assert len(steps) == 0

    def test_complete_all_iq_sets_iq_complete(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        steps = create_validation_steps_from_tier(db, system.id, "HIGH")
        iq_steps = [s for s in steps if s.phase == "IQ"]

        for step in iq_steps:
            update_validation_step(db, system.id, step.id, status=StepStatus.COMPLETE)

        db.refresh(system)
        assert system.iq_complete is True
        assert system.oq_complete is False

    def test_complete_all_steps_sets_validated(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH,
                             next_review_date=date.today() + timedelta(days=365))
        steps = create_validation_steps_from_tier(db, system.id, "HIGH")

        for step in steps:
            update_validation_step(db, system.id, step.id, status=StepStatus.COMPLETE)

        db.refresh(system)
        assert system.iq_complete is True
        assert system.oq_complete is True
        assert system.pq_complete is True
        assert system.validation_status == ValidationStatus.VALIDATED

    def test_partial_steps_sets_in_progress(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        steps = create_validation_steps_from_tier(db, system.id, "HIGH")
        iq_steps = [s for s in steps if s.phase == "IQ"]

        # Complete only IQ steps
        for step in iq_steps:
            update_validation_step(db, system.id, step.id, status=StepStatus.COMPLETE)

        db.refresh(system)
        assert system.validation_status == ValidationStatus.IN_PROGRESS

    def test_recalculate_after_uncompleting_step(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH,
                             next_review_date=date.today() + timedelta(days=365))
        steps = create_validation_steps_from_tier(db, system.id, "HIGH")

        # Complete all steps
        for step in steps:
            update_validation_step(db, system.id, step.id, status=StepStatus.COMPLETE)

        db.refresh(system)
        assert system.validation_status == ValidationStatus.VALIDATED

        # Un-complete one IQ step
        update_validation_step(db, system.id, steps[0].id, status=StepStatus.NOT_STARTED)

        db.refresh(system)
        assert system.iq_complete is False
        assert system.validation_status == ValidationStatus.IN_PROGRESS


class TestObligations:
    """Test obligation creation and tracking."""

    def test_sync_creates_obligations(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        obligations = sync_obligations_from_classification(db, system.id, "HIGH")
        assert len(obligations) == 7  # 7 HIGH risk obligations
        assert all(o.system_id == system.id for o in obligations)

    def test_all_obligations_start_not_started(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        obligations = sync_obligations_from_classification(db, system.id, "HIGH")
        assert all(o.status == ObligationStatus.NOT_STARTED for o in obligations)

    def test_update_obligation_status(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        obligations = sync_obligations_from_classification(db, system.id, "HIGH")

        updated = update_obligation(db, system.id, obligations[0].id, status="complete")
        assert updated.status == ObligationStatus.COMPLETE

    def test_obligation_progress(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        obligations = sync_obligations_from_classification(db, system.id, "HIGH")

        progress = get_obligation_progress(db, system.id)
        assert progress["total"] == 7
        assert progress["complete"] == 0
        assert progress["not_started"] == 7

        # Complete one obligation
        update_obligation(db, system.id, obligations[0].id, status="complete")
        progress = get_obligation_progress(db, system.id)
        assert progress["complete"] == 1
        assert progress["percentage"] == pytest.approx(14.3, rel=0.1)

    def test_resync_replaces_obligations(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        sync_obligations_from_classification(db, system.id, "HIGH")

        # Re-sync should replace existing obligations
        new_obligations = sync_obligations_from_classification(db, system.id, "HIGH")
        assert len(new_obligations) == 7

        # Should still only have 7 total (not 14)
        progress = get_obligation_progress(db, system.id)
        assert progress["total"] == 7

    def test_obligation_update_creates_audit_log(self, db):
        system = make_system(db, risk_tier=RiskTier.HIGH)
        obligations = sync_obligations_from_classification(db, system.id, "HIGH")

        update_obligation(db, system.id, obligations[0].id, status="complete", changed_by="QA_Engineer")

        logs = db.query(AuditLog).filter(AuditLog.system_id == system.id).all()
        assert any(log.action == "obligation_updated" for log in logs)

    def test_limited_risk_obligations(self, db):
        system = make_system(db, risk_tier=RiskTier.LIMITED)
        obligations = sync_obligations_from_classification(db, system.id, "LIMITED")
        assert len(obligations) >= 3  # At least Article 50 obligations


class TestChangeControl:
    """Test version change detection and review enforcement."""

    def test_version_change_triggers_revalidation(self, db):
        system = make_system(db, validation_status=ValidationStatus.VALIDATED,
                             iq_complete=True, oq_complete=True, pq_complete=True)
        updated = record_version_change(db, system.id, "2.0.0", changed_by="CTO")

        assert updated.validation_status == ValidationStatus.REQUIRES_REVALIDATION
        assert updated.version == "2.0.0"
        assert updated.previous_version == "1.0.0"

    def test_same_version_no_revalidation(self, db):
        system = make_system(db, validation_status=ValidationStatus.VALIDATED)
        updated = record_version_change(db, system.id, "1.0.0", changed_by="CTO")

        assert updated.validation_status == ValidationStatus.VALIDATED  # No change

    def test_version_change_creates_audit_log(self, db):
        system = make_system(db)
        record_version_change(db, system.id, "2.0.0", changed_by="CTO")

        logs = db.query(AuditLog).filter(AuditLog.system_id == system.id).all()
        assert len(logs) >= 2  # version_changed + revalidation_triggered
        actions = [log.action for log in logs]
        assert "version_changed" in actions
        assert "revalidation_triggered" in actions

    def test_overdue_review_auto_flagged(self, db):
        make_system(db, validation_status=ValidationStatus.VALIDATED,
                    iq_complete=True, oq_complete=True, pq_complete=True,
                    next_review_date=date.today() - timedelta(days=30))

        flagged = check_and_flag_overdue_reviews(db)
        assert len(flagged) == 1
        assert flagged[0].validation_status == ValidationStatus.REQUIRES_REVALIDATION

    def test_not_overdue_not_flagged(self, db):
        make_system(db, validation_status=ValidationStatus.VALIDATED,
                    iq_complete=True, oq_complete=True, pq_complete=True,
                    next_review_date=date.today() + timedelta(days=365))

        flagged = check_and_flag_overdue_reviews(db)
        assert len(flagged) == 0