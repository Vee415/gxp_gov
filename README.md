# GxP-Gov

AI Governance-as-a-Service for Regulated Pharma & Life Sciences

## What It Does

GxP-Gov is an AI governance platform for pharmaceutical companies using AI in regulated workflows. It makes AI systems **classifiable, validated, auditable, and defensible** to EMA, FDA, and national competent authorities.

When EMA asks if your AI is validated and compliant, GxP-Gov means the answer is yes — and you can prove it in 30 seconds.

### Features

| Feature | Description |
|---------|-------------|
| **AI System Registry** | Structured catalogue of every AI system in regulated workflows — name, vendor, use case, risk tier, validation status |
| **EU AI Act Risk Classifier** | Rule-based classification of AI use cases against EU AI Act criteria — returns risk tier, applicable annex, obligations, and gap analysis |
| **Validation Tracker** | Tracks IQ/OQ/PQ validation lifecycle for each AI system — flags systems running in production without completed validation |
| **Trackable Obligations** | Mark each EU AI Act obligation as not-started/in-progress/complete with evidence references and compliance progress bars |
| **GMLP-Adapted Validation Steps** | IQ/OQ/PQ checklists derived from GAMP 5 and EMA guidance — 13 steps for HIGH risk, 9 for LIMITED, 2 for MINIMAL |
| **Classifier → Validation Auto-Link** | Classify a system and apply obligations + validation steps in one action |
| **Change Control Detection** | Model version changes automatically trigger revalidation flags |
| **Audit Trail** | Every obligation update, step completion, and version change is logged with timestamps |
| **Behavioral Assessment Scenarios** | 8 scenarios to help users question whether vendor claims match what the AI actually does |

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                React + Recharts Frontend                  │
│  Registry | Risk Classifier | Validation Tracker         │
└───────────────────────┬───────────────────────────────────┘
                        │ REST API
┌───────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────┐  ┌──────────┐  ┌─────────────┐             │
│  │ Registry  │  │ Classifier│  │  Validation │             │
│  │  CRUD     │  │ + Apply   │  │  Tracker    │             │
│  └─────┬────┘  └────┬─────┘  └──────┬──────┘             │
│        └─────────────┼──────────────┘                    │
│  ┌──────────┐  ┌─────┴──────┐  ┌──────────────┐          │
│  │Obligations│  │Validation  │  │   Change     │          │
│  │ Manager   │  │Steps Mgr  │  │   Control    │          │
│  └──────────┘  └────────────┘  └──────────────┘          │
│  ┌──────────────────────────────────────────────┐         │
│  │  EU AI Act Rules + EMA Guidance + GMLP Steps  │         │
│  └──────────────────────────────────────────────┘         │
└───────────────────────┬───────────────────────────────────┘
                        │
┌───────────────────────▼───────────────────────────────────┐
│                     SQLite DB                              │
│  ai_systems | obligations | validation_steps | audit_log   │
│  (21 seeded demo systems + 129 obligations + 237 steps)    │
└───────────────────────────────────────────────────┘
```

## Real Data Sources

GxP-Gov uses real regulatory and device data — not synthetic approximations:

| Component | Source | Details |
|-----------|--------|---------|
| EU AI Act rules | Regulation (EU) 2024/1689 | Articles 5, 6, 9-16, 50, 69; Annex III categories; prohibited practices from Article 5 |
| AI system registry | FDA AI/ML-Enabled Medical Devices list | 1,248+ FDA-cleared devices; 21 selected for demo spanning Pathology, Clinical Chemistry, Hematology, Cardiovascular, Radiology |
| EMA guidance | EMA/CHMP/CVMP/83833/2023 | 7 lifecycle stages, GMLP-adapted IQ/OQ/PQ framework, frozen model requirements, XAI mandates |
| GxP validation | GAMP 5, Annex 11, 21 CFR Part 11 | Adapted IQ/OQ/PQ for AI/ML, ALCOA+ data integrity, change control |
| Prohibited practices | EU AI Act Article 5 | 8 prohibited practices including social scoring, subliminal manipulation, real-time biometric ID |

## Quick Start

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000

## Demo Scenarios

### Demo 1: Classify and Apply
1. Open the Risk Classifier page
2. Enter "Patient stratification for oncology clinical trials"
3. See it classified as **HIGH risk** under **Annex III Category 5**
4. Switch to "Classify existing system" and select a system
5. Click **"Apply to System"** — creates 7 obligations and 13 validation steps
6. Go to Validation Tracker → click the system row → see obligations and checklist

### Demo 2: Track Validation Progress
1. Open Validation Tracker
2. Click on a system row to expand it
3. Check off validation steps — IQ/OQ/PQ booleans update automatically
4. Change obligation status from "Not Started" → "In Progress" → "Complete"
5. See the compliance progress bar update

### Demo 3: Compliance Flags
1. Open the Validation Tracker page
2. See 6 systems flagged — 2 critical (incomplete OQ), 4 warnings
3. See DigitalTwin Trials flagged for **overdue revalidation**

### Demo 4: Change Control
```bash
# Record a model version change → triggers revalidation
curl -X POST http://localhost:8000/api/systems/1/version-change \
  -H "Content-Type: application/json" \
  -d '{"new_version":"2.1.0","changed_by":"CTO","notes":"Model retrained"}'
# Check audit log
curl http://localhost:8000/api/systems/1/audit-log
```

### Demo 5: Prohibited Use Case
1. Enter "Social scoring of patients for insurance coverage decisions"
2. See it classified as **UNACCEPTABLE** — prohibited under Article 5(1)(c)

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

77 tests covering classifier edge cases, validation recalculation, obligation syncing, change control, and API endpoints.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI |
| Database | SQLite + SQLAlchemy |
| Risk Classifier | Rule-based (no ML — explainability is a hard requirement) |
| Frontend | React + Recharts + Vite |
| Containerization | Docker Compose |

## Project Structure

```
gxp-gov/
├── backend/
│   ├── main.py                  FastAPI app entry point
│   ├── database.py              SQLite + SQLAlchemy setup
│   ├── models/system.py         Pydantic schemas + SQLAlchemy models
│   ├── routers/
│   │   ├── registry.py          AI system CRUD endpoints
│   │   ├── classifier.py        EU AI Act risk classification
│   │   └── validation.py        Validation tracker endpoints
│   ├── services/
│   │   ├── risk_classifier.py   Classification logic
│   │   └── validation_tracker.py Compliance flagging
│   ├── regulatory/
│   │   ├── eu_ai_act_rules.py   Extracted EU AI Act classification criteria
│   │   └── ema_guidance.py      EMA requirements mapped to checks
│   ├── db/seed.py               18 realistic pharma AI systems
│   └── tests/
├── frontend/
│   └── src/
│       ├── pages/               Registry, RiskClassifier, ValidationTracker
│       ├── components/          RiskBadge, ValidationStatus, SystemCard
│       └── api/client.js        Backend API wrapper
├── docker-compose.yml
├── GxP-Gov_guide.md             Full project guide with roadmap
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/systems/` | List all AI systems (filter by risk_tier, validation_status) |
| GET | `/api/systems/{id}` | Get a specific system |
| POST | `/api/systems/` | Create a new system |
| PUT | `/api/systems/{id}` | Update a system |
| DELETE | `/api/systems/{id}` | Delete a system |
| POST | `/api/classify/` | Classify a use case by description |
| POST | `/api/classify/{id}` | Classify an existing registry system |
| POST | `/api/classify/{id}/apply` | Classify AND persist obligations + validation steps |
| GET | `/api/classify/annex-iii` | Get the 8 EU AI Act Annex III high-risk categories |
| GET | `/api/classify/prohibited-practices` | Get the 8 prohibited AI practices (Article 5) |
| GET | `/api/classify/behavioral-scenarios` | Get behavioral assessment scenarios (filter by risk_tier) |
| GET | `/api/validation/` | List validation status for all systems |
| GET | `/api/validation/flags` | Get systems with compliance issues |
| GET | `/api/validation/summary` | Get validation summary counts |
| PUT | `/api/validation/{id}` | Update validation status for a system |
| GET | `/api/validation/ema-checks` | Get EMA validation checks |
| GET | `/api/validation/ema-lifecycle` | Get the 7 EMA lifecycle stages |
| GET | `/api/systems/{id}/obligations` | List obligations for a system |
| PUT | `/api/systems/{id}/obligations/{ob_id}` | Update obligation status/evidence/notes |
| GET | `/api/systems/{id}/obligations/progress` | Get obligation completion progress |
| GET | `/api/systems/{id}/validation-steps` | List validation steps (filter by phase) |
| PUT | `/api/systems/{id}/validation-steps/{step_id}` | Update step status |
| POST | `/api/systems/{id}/validation-steps/recalculate` | Recalculate IQ/OQ/PQ from steps |
| GET | `/api/systems/{id}/validation/detail` | Full detail: system + obligations + steps + progress |
| GET | `/api/systems/{id}/audit-log` | Get audit trail for a system |
| POST | `/api/systems/{id}/version-change` | Record version change (triggers revalidation) |
| POST | `/api/systems/check-overdue` | Check all systems for overdue reviews |

## Roadmap

- **v0.1** — Registry, Risk Classifier, Validation Tracker, Behavioral Scenarios
- **v0.1.5** — Trackable Obligations, GMLP Validation Steps, Classifier Auto-Link, Change Control, Audit Trail
- **v0.2** — Bias Auditor (chi-square demographic analysis, Synthea patient data)
- **v0.3** — Audit Trail Generator (EMA-ready PDF exports)
- **v1.0** — Multi-tenant SaaS architecture, authentication, billing
- **v1.x** — Integrations (Medidata, Veeva), automated revalidation triggers

See [GxP-Gov_guide.md](./GxP-Gov_guide.md) for the full roadmap and changelog.

## License

MIT