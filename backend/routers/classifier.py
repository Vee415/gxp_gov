from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.system import AISystem
from services.risk_classifier import classify_use_case, classify_system
from services.obligation_manager import sync_obligations_from_classification
from services.validation_steps_manager import create_validation_steps_from_tier
from regulatory.eu_ai_act_rules import get_annex_iii_categories, get_prohibited_practices
from regulatory.behavioral_scenarios import get_behavioral_scenarios, get_scenarios_for_risk_tier

router = APIRouter()


class ClassifyRequest(BaseModel):
    use_case: str
    description: str = ""


class ClassifyResponse(BaseModel):
    system_name: str | None = None
    use_case: str
    risk_tier: str
    annex: str
    obligations: list[str]
    triggered_rules: list[str]
    gap_analysis: dict


@router.post("/", response_model=ClassifyResponse)
def classify(request: ClassifyRequest):
    result = classify_use_case(request.use_case, request.description)
    return ClassifyResponse(**result)


@router.post("/{system_id}", response_model=ClassifyResponse)
def classify_existing_system(system_id: int, db: Session = Depends(get_db)):
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    result = classify_system(system)
    return ClassifyResponse(**result)


@router.get("/annex-iii")
def list_annex_iii_categories():
    """Return the 8 high-risk AI system categories from EU AI Act Annex III."""
    return get_annex_iii_categories()


@router.get("/prohibited-practices")
def list_prohibited_practices():
    """Return the prohibited AI practices under EU AI Act Article 5."""
    return get_prohibited_practices()


@router.get("/behavioral-scenarios")
def list_behavioral_scenarios(risk_tier: str = ""):
    """Return behavioral assessment scenarios to help users question vendor claims."""
    if risk_tier:
        return get_scenarios_for_risk_tier(risk_tier.upper())
    return get_behavioral_scenarios()


class ClassifyAndApplyResponse(BaseModel):
    classification: dict
    obligations_created: int
    validation_steps_created: int


@router.post("/{system_id}/apply", response_model=ClassifyAndApplyResponse)
def classify_and_apply(system_id: int, db: Session = Depends(get_db)):
    """Classify an existing system AND persist obligations + validation steps.
    This is the 'auto-link' endpoint that bridges classification to tracking."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")

    # Run classification
    result = classify_system(system)

    # Update system's risk_tier and annex from classification
    from models.system import RiskTier, Annex
    system.risk_tier = result["risk_tier"]
    system.annex = result["annex"]
    db.commit()

    # Create obligations from classification
    obligations = sync_obligations_from_classification(db, system_id, result["risk_tier"])

    # Create validation steps from GMLP templates
    steps = create_validation_steps_from_tier(db, system_id, result["risk_tier"])

    return ClassifyAndApplyResponse(
        classification=result,
        obligations_created=len(obligations),
        validation_steps_created=len(steps),
    )