from datetime import date, datetime
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Date, Text, Integer, ForeignKey, Text as SqlText
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class RiskTier(str, Enum):
    UNACCEPTABLE = "UNACCEPTABLE"
    HIGH = "HIGH"
    LIMITED = "LIMITED"
    MINIMAL = "MINIMAL"


class ValidationStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VALIDATED = "validated"
    REQUIRES_REVALIDATION = "requires_revalidation"


class Annex(str, Enum):
    I = "I"
    II = "II"
    III = "III"
    NONE = "None"


class ObligationStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class StepStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"


class AISystem(Base):
    __tablename__ = "ai_systems"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    vendor: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    use_case: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    risk_tier: Mapped[RiskTier] = mapped_column(String(20), default=RiskTier.MINIMAL)
    annex: Mapped[Annex] = mapped_column(String(5), default=Annex.NONE)
    validation_status: Mapped[ValidationStatus] = mapped_column(
        String(30), default=ValidationStatus.NOT_STARTED
    )
    iq_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    oq_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    pq_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    owner: Mapped[str] = mapped_column(String(200), default="")
    last_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    previous_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    obligations_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    obligations: Mapped[list["Obligation"]] = relationship(back_populates="system", cascade="all, delete-orphan")
    validation_steps: Mapped[list["ValidationStep"]] = relationship(back_populates="system", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="system", cascade="all, delete-orphan")


class Obligation(Base):
    __tablename__ = "obligations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    system_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    article: Mapped[str] = mapped_column(String(30), nullable=False)
    obligation: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[ObligationStatus] = mapped_column(String(20), default=ObligationStatus.NOT_STARTED)
    evidence_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    system: Mapped["AISystem"] = relationship(back_populates="obligations")


class ValidationStep(Base):
    __tablename__ = "validation_steps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    system_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    phase: Mapped[str] = mapped_column(String(5), nullable=False)  # IQ, OQ, PQ
    step_key: Mapped[str] = mapped_column(String(80), nullable=False)
    step_label: Mapped[str] = mapped_column(String(200), nullable=False)
    source: Mapped[str] = mapped_column(String(100), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[StepStatus] = mapped_column(String(20), default=StepStatus.NOT_STARTED)
    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    system: Mapped["AISystem"] = relationship(back_populates="validation_steps")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    system_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_systems.id", ondelete="CASCADE"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)  # obligation, validation_step, system
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str] = mapped_column(String(200), default="")
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    system: Mapped["AISystem"] = relationship(back_populates="audit_logs")


from pydantic import BaseModel, ConfigDict


class AISystemBase(BaseModel):
    name: str
    vendor: str
    version: str
    use_case: str
    description: str = ""
    risk_tier: RiskTier = RiskTier.MINIMAL
    annex: Annex = Annex.NONE
    validation_status: ValidationStatus = ValidationStatus.NOT_STARTED
    iq_complete: bool = False
    oq_complete: bool = False
    pq_complete: bool = False
    owner: str = ""
    last_review_date: date | None = None
    next_review_date: date | None = None


class AISystemCreate(AISystemBase):
    pass


class AISystemUpdate(BaseModel):
    name: str | None = None
    vendor: str | None = None
    version: str | None = None
    use_case: str | None = None
    description: str | None = None
    risk_tier: RiskTier | None = None
    annex: Annex | None = None
    validation_status: ValidationStatus | None = None
    iq_complete: bool | None = None
    oq_complete: bool | None = None
    pq_complete: bool | None = None
    owner: str | None = None
    last_review_date: date | None = None
    next_review_date: date | None = None


class AISystemResponse(AISystemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# --- Obligation schemas ---

class ObligationUpdate(BaseModel):
    status: ObligationStatus | None = None
    evidence_ref: str | None = None
    notes: str | None = None


class ObligationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_id: int
    article: str
    obligation: str
    category: str
    required: bool
    status: ObligationStatus
    evidence_ref: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ObligationProgressResponse(BaseModel):
    total: int
    complete: int
    in_progress: int
    not_started: int
    percentage: float


# --- Validation Step schemas ---

class ValidationStepUpdate(BaseModel):
    status: StepStatus | None = None
    completed_by: str | None = None
    notes: str | None = None


class ValidationStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_id: int
    phase: str
    step_key: str
    step_label: str
    source: str
    sort_order: int
    status: StepStatus
    completed_at: date | None
    completed_by: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


# --- Audit Log schemas ---

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    system_id: int
    action: str
    entity_type: str
    entity_id: int | None
    old_value: str | None
    new_value: str | None
    changed_by: str
    changed_at: datetime