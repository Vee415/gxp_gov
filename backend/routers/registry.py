from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models.system import AISystem, AISystemCreate, AISystemUpdate, AISystemResponse, RiskTier, ValidationStatus

router = APIRouter()


@router.get("/", response_model=list[AISystemResponse])
def list_systems(
    risk_tier: Optional[RiskTier] = None,
    validation_status: Optional[ValidationStatus] = None,
    db: Session = Depends(get_db),
):
    query = db.query(AISystem)
    if risk_tier:
        query = query.filter(AISystem.risk_tier == risk_tier)
    if validation_status:
        query = query.filter(AISystem.validation_status == validation_status)
    return query.all()


@router.get("/{system_id}", response_model=AISystemResponse)
def get_system(system_id: int, db: Session = Depends(get_db)):
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="System not found")
    return system


@router.post("/", response_model=AISystemResponse, status_code=201)
def create_system(system: AISystemCreate, db: Session = Depends(get_db)):
    db_system = AISystem(**system.model_dump())
    db.add(db_system)
    db.commit()
    db.refresh(db_system)
    return db_system


@router.put("/{system_id}", response_model=AISystemResponse)
def update_system(system_id: int, system: AISystemUpdate, db: Session = Depends(get_db)):
    db_system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not db_system:
        raise HTTPException(status_code=404, detail="System not found")
    update_data = system.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_system, key, value)
    db.commit()
    db.refresh(db_system)
    return db_system


@router.delete("/{system_id}", status_code=204)
def delete_system(system_id: int, db: Session = Depends(get_db)):
    db_system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not db_system:
        raise HTTPException(status_code=404, detail="System not found")
    db.delete(db_system)
    db.commit()