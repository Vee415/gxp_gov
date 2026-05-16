from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from models.system import AISystem, Obligation, ValidationStep, AuditLog  # noqa: F401 — ensure models are registered
from routers import registry, classifier, validation, obligations, validation_steps, change_control

app = FastAPI(
    title="GxP-Gov API",
    description="AI Governance-as-a-Service for Regulated Pharma & Life Sciences",
    version="0.1.5",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    return {"status": "ok", "version": "0.1.5"}

# Serve frontend static files (for production deployment)
static_dir = Path(__file__).parent / "static"
if static_dir.is_dir():
    # SPA catch-all: serve index.html for any non-API, non-static path
    @app.get("/{path:path}")
    async def spa_fallback(request: Request, path: str):
        file_path = static_dir / path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(static_dir / "index.html")

    # Mount static assets (js, css, images)
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="static-assets")