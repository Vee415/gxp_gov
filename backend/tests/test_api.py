"""Tests for API endpoints using TestClient."""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from database import Base, engine, SessionLocal
    from main import app
    from models.system import AISystem, Obligation, ValidationStep, AuditLog

    Base.metadata.create_all(bind=engine)

    # Seed a test system
    db = SessionLocal()
    system = AISystem(
        name="Test System",
        vendor="TestVendor",
        version="1.0.0",
        use_case="AI-assisted diagnosis in cardiology",
        risk_tier="HIGH",
        annex="III",
    )
    db.add(system)
    db.commit()
    db.refresh(system)

    from main import app
    client = TestClient(app)
    yield client

    db.close()
    Base.metadata.drop_all(bind=engine)


class TestClassifierAPI:
    """Test classifier API endpoints."""

    def test_classify_custom(self, client):
        response = client.post("/api/classify/", json={
            "use_case": "patient stratification for oncology clinical trials"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["risk_tier"] == "HIGH"
        assert data["annex"] == "III"
        assert len(data["obligations"]) > 0

    def test_classify_prohibited(self, client):
        response = client.post("/api/classify/", json={
            "use_case": "social scoring of patients for insurance coverage decisions"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["risk_tier"] == "UNACCEPTABLE"

    def test_classify_minimal(self, client):
        response = client.post("/api/classify/", json={
            "use_case": "supply chain logistics optimization for warehouse management"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["risk_tier"] == "MINIMAL"

    def test_annex_iii_categories(self, client):
        response = client.get("/api/classify/annex-iii")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8

    def test_prohibited_practices(self, client):
        response = client.get("/api/classify/prohibited-practices")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8

    def test_behavioral_scenarios(self, client):
        response = client.get("/api/classify/behavioral-scenarios")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8

    def test_behavioral_scenarios_filtered(self, client):
        response = client.get("/api/classify/behavioral-scenarios?risk_tier=HIGH")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 8  # All scenarios are relevant to HIGH

    def test_classify_and_apply(self, client):
        # Get the test system ID
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]

        response = client.post(f"/api/classify/{system_id}/apply")
        assert response.status_code == 200
        data = response.json()
        assert "classification" in data
        assert data["obligations_created"] > 0
        assert data["validation_steps_created"] > 0


class TestValidationAPI:
    """Test validation API endpoints."""

    def test_list_validation(self, client):
        response = client.get("/api/validation/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_flags(self, client):
        response = client.get("/api/validation/flags")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_summary(self, client):
        response = client.get("/api/validation/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_systems" in data
        assert "validated" in data

    def test_ema_checks(self, client):
        response = client.get("/api/validation/ema-checks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_ema_lifecycle(self, client):
        response = client.get("/api/validation/ema-lifecycle")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 7


class TestObligationsAPI:
    """Test obligations API endpoints."""

    def test_get_obligations_empty(self, client):
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]

        response = client.get(f"/api/systems/{system_id}/obligations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Empty unless classify-and-apply was called

    def test_obligation_progress_empty(self, client):
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]

        response = client.get(f"/api/systems/{system_id}/obligations/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


class TestValidationStepsAPI:
    """Test validation steps API endpoints."""

    def test_get_validation_steps_empty(self, client):
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]

        response = client.get(f"/api/systems/{system_id}/validation-steps")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_validation_detail(self, client):
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]

        response = client.get(f"/api/systems/{system_id}/validation/detail")
        assert response.status_code == 200
        data = response.json()
        assert "system_id" in data
        assert "name" in data
        assert "risk_tier" in data


class TestChangeControlAPI:
    """Test change control API endpoints."""

    def test_version_change(self, client):
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]

        response = client.post(f"/api/systems/{system_id}/version-change", json={
            "new_version": "2.0.0",
            "changed_by": "QA Engineer",
            "notes": "Model retrained on new data"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == "2.0.0"
        assert data["previous_version"] == "1.0.0"
        assert data["validation_status"] == "requires_revalidation"

    def test_audit_log(self, client):
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]

        # First make a version change to create an audit log
        client.post(f"/api/systems/{system_id}/version-change", json={
            "new_version": "2.0.0",
            "changed_by": "QA Engineer"
        })

        response = client.get(f"/api/systems/{system_id}/audit-log")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_check_overdue(self, client):
        response = client.post("/api/systems/check-overdue")
        assert response.status_code == 200
        data = response.json()
        assert "flagged_count" in data


class TestRegistryAPI:
    """Test registry CRUD endpoints."""

    def test_list_systems(self, client):
        response = client.get("/api/systems/")
        assert response.status_code == 200

    def test_create_system(self, client):
        response = client.post("/api/systems/", json={
            "name": "New Test System",
            "vendor": "TestVendor",
            "version": "1.0.0",
            "use_case": "drug interaction checker",
        })
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test System"
        assert data["risk_tier"] == "MINIMAL"

    def test_get_system(self, client):
        systems = client.get("/api/systems/").json()
        system_id = systems[0]["id"]
        response = client.get(f"/api/systems/{system_id}")
        assert response.status_code == 200