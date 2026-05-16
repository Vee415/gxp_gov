from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from models.system import AISystem, Obligation, ValidationStep, AuditLog  # noqa: F401 — ensure models are registered
from routers import registry, classifier, validation, obligations, validation_steps, change_control

app = FastAPI(
    title="GxP-Gov API",
    description="AI Governance-as-a-Service for Regulated Pharma & Life Sciences",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(registry.router, prefix="/api/systems", tags=["Registry"])
app.include_router(classifier.router, prefix="/api/classify", tags=["Classifier"])
app.include_router(validation.router, prefix="/api/validation", tags=["Validation"])
app.include_router(obligations.router, prefix="/api/systems", tags=["Obligations"])
app.include_router(validation_steps.router, prefix="/api/systems", tags=["Validation Steps"])
app.include_router(change_control.router, prefix="/api/systems", tags=["Change Control"])


@app.on_event("startup")
def startup():
    init_db()
    from db.seed import seed_db
    seed_db()


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}