"""Seed the database with FDA-cleared AI/ML-enabled medical devices.

Based on the FDA AI/ML-Enabled Medical Devices list (1,248+ devices through 2025).
Source: https://www.fda.gov/medical-devices/software-medical-device-samd/

Selected 20 devices relevant to pharma/life sciences AI governance, spanning
Pathology, Clinical Chemistry, Hematology, Cardiovascular, and Radiology panels.

Demo scenarios preserved:
- 2 systems with incomplete OQ (TrialDesign Pro, DrugInteract) — flagged as critical
- 1 system requiring revalidation (DigitalTwin Trials) — flagged as warning
- 1 prohibited use case (SocialRisk Score) — flagged as unacceptable
- 1 not started (StabilityPredict) — flagged as warning
"""

from datetime import date

from sqlalchemy.orm import Session

from database import SessionLocal
from models.system import AISystem, RiskTier, ValidationStatus, Annex, Obligation, ObligationStatus, ValidationStep, StepStatus
from regulatory.eu_ai_act_rules import get_obligations_detailed
from regulatory.gmlp_steps import get_gmlp_steps


SEED_SYSTEMS = [
    # --- FDA-Cleared Devices (real) ---
    {
        "name": "Paige Prostate",
        "vendor": "Paige.AI",
        "version": "1.0.0",
        "use_case": "AI-assisted pathology for prostate cancer detection in digital biopsy slides",
        "description": "First FDA-authorized AI-based pathology product. Detects prostate cancer in digital pathology slides, providing pathologists with AI-assisted diagnostic support. De Novo pathway (DEN200080).",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Sarah Mueller",
        "last_review_date": date(2026, 3, 15),
        "next_review_date": date(2027, 3, 15),
    },
    {
        "name": "xT CDx",
        "vendor": "Tempus Labs, Inc.",
        "version": "1.0.0",
        "use_case": "Companion diagnostic for targeted therapy selection using genomic profiling",
        "description": "PMA-approved companion diagnostic that uses next-generation sequencing to identify patients eligible for targeted therapies. Directly influences treatment decisions in oncology. P210011.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Anika Patel",
        "last_review_date": date(2026, 1, 20),
        "next_review_date": date(2027, 1, 20),
    },
    {
        "name": "Galen Second Read",
        "vendor": "Ibex Medical Analytics Ltd.",
        "version": "2.3.1",
        "use_case": "AI-assisted pathology second read for prostate and breast cancer detection",
        "description": "AI system that provides second-read analysis of pathology slides to identify missed cancer cases. Used as quality assurance tool alongside primary pathologist review. 510(k) K241232.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Marcus Chen",
        "last_review_date": date(2026, 2, 20),
        "next_review_date": date(2027, 2, 20),
    },
    {
        "name": "Genius Digital Diagnostics System",
        "vendor": "Hologic Inc.",
        "version": "1.0.0",
        "use_case": "AI-powered cervical cancer screening in digital cytology",
        "description": "De Novo-authorized (DEN210035) AI algorithm for cervical cancer screening that uses deep learning to identify abnormal cells in Pap test slides. Directly impacts clinical decision-making for cancer screening.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Elena Rossi",
        "last_review_date": date(2026, 4, 10),
        "next_review_date": date(2027, 4, 10),
    },
    {
        "name": "KidneyIntelX.dkd",
        "vendor": "Renalytix AI, Inc.",
        "version": "1.0.0",
        "use_case": "Clinical decision support for diabetic kidney disease progression risk assessment",
        "description": "De Novo-authorized (DEN200052) AI system that integrates clinical data and biomarkers to predict kidney disease progression risk in diabetic patients. Supports treatment decisions in nephrology.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. James Okonkwo",
        "last_review_date": date(2026, 5, 5),
        "next_review_date": date(2027, 5, 5),
    },
    {
        "name": "HeartFlow Analysis",
        "vendor": "HeartFlow, Inc.",
        "version": "3.1.0",
        "use_case": "Non-invasive fractional flow reserve (FFRct) assessment for coronary artery disease",
        "description": "Uses CT scan data and computational fluid dynamics to calculate FFRct, helping cardiologists determine whether patients need stenting. 510(k) K213857.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Robert Klein",
        "last_review_date": date(2026, 4, 20),
        "next_review_date": date(2027, 4, 20),
    },
    {
        "name": "Viz HCM",
        "vendor": "Viz.ai, Inc.",
        "version": "1.0.0",
        "use_case": "AI-assisted detection of hypertrophic cardiomyopathy on cardiac CT",
        "description": "De Novo-authorized (DEN230003) AI system that detects hypertrophic cardiomyopathy on CT imaging and alerts care teams for timely intervention.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Fatima Al-Rashid",
        "last_review_date": date(2026, 3, 10),
        "next_review_date": date(2027, 3, 10),
    },
    {
        "name": "Sight OLO",
        "vendor": "Sight Diagnostics Ltd.",
        "version": "1.3.0",
        "use_case": "AI-powered complete blood count (CBC) analysis from fingerstick blood samples",
        "description": "Uses computer vision and AI to perform CBC differentials from small blood volumes. Used in clinical trial labs for monitoring patients. 510(k) K190898.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Naomi Tanaka",
        "last_review_date": date(2026, 2, 28),
        "next_review_date": date(2027, 2, 28),
    },
    {
        "name": "ProFound Detection",
        "vendor": "iCAD, Inc.",
        "version": "4.0.0",
        "use_case": "AI-assisted breast cancer detection on mammography for clinical decision support",
        "description": "Deep learning system that analyzes 3D mammography images to detect suspicious lesions and assist radiologists in breast cancer screening. 510(k) K240417.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Maria Santos",
        "last_review_date": date(2026, 5, 1),
        "next_review_date": date(2027, 5, 1),
    },
    {
        "name": "TumorSight Viz",
        "vendor": "SimBioSys, Inc.",
        "version": "1.0.0",
        "use_case": "AI-powered tumor visualization for oncology treatment planning",
        "description": "3D tumor visualization system that helps oncologists plan surgical and radiation therapy by reconstructing tumor geometry from medical imaging. 510(k) K233562.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Henrik Larsson",
        "last_review_date": date(2026, 4, 15),
        "next_review_date": date(2027, 4, 15),
    },
    {
        "name": "HepaFat-AI",
        "vendor": "Resonance Health Analysis Services Pty Ltd",
        "version": "1.0.0",
        "use_case": "AI-based liver fat quantification for NASH drug trial endpoints",
        "description": "Uses AI to quantify liver fat from MRI for non-alcoholic steatohepatitis (NASH) drug trials. Directly used as a clinical trial endpoint. 510(k) K201039.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Pierre Dubois",
        "last_review_date": date(2026, 3, 20),
        "next_review_date": date(2027, 3, 20),
    },
    # --- Systems with validation issues (demo scenarios) ---
    {
        "name": "EchoGo Amyloidosis",
        "vendor": "Ultromics Limited",
        "version": "1.0.0",
        "use_case": "AI-assisted detection of cardiac amyloidosis on echocardiography",
        "description": "AI system that analyzes echocardiogram data to detect cardiac amyloidosis, supporting earlier diagnosis. 510(k) K240860.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        # INTENTIONAL: OQ incomplete — flagged as critical compliance risk
        "validation_status": ValidationStatus.IN_PROGRESS,
        "iq_complete": True,
        "oq_complete": False,
        "pq_complete": False,
        "owner": "Dr. Thomas Weber",
        "last_review_date": date(2025, 9, 15),
        "next_review_date": date(2026, 9, 15),
    },
    {
        "name": "AUTION EYE AI-4510",
        "vendor": "Arkray Inc.",
        "version": "1.0.0",
        "use_case": "AI-powered urine particle analysis for clinical laboratory diagnostics",
        "description": "Automated urine sediment analysis using AI image recognition to identify and classify urinary particles. Used in clinical trial lab settings. 510(k) K232416.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        # INTENTIONAL: OQ incomplete — flagged as critical compliance risk
        "validation_status": ValidationStatus.IN_PROGRESS,
        "iq_complete": True,
        "oq_complete": False,
        "pq_complete": False,
        "owner": "Dr. Lisa Park",
        "last_review_date": date(2025, 11, 1),
        "next_review_date": date(2026, 11, 1),
    },
    {
        "name": "DigitalTwin Trials",
        "vendor": "Unlearn.AI",
        "version": "1.3.0",
        "use_case": "Digital twin generation for clinical trial control arm augmentation",
        "description": "Creates digital twin patients from historical data to augment control arms in clinical trials, reducing the number of patients needed for randomization. EMA qualification opinion obtained March 2025.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        # INTENTIONAL: overdue review — requires revalidation
        "validation_status": ValidationStatus.REQUIRES_REVALIDATION,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Kevin Zhao",
        "last_review_date": date(2025, 3, 1),
        "next_review_date": date(2025, 9, 1),
    },
    {
        "name": "Saige-Dx",
        "vendor": "DeepHealth, Inc.",
        "version": "3.1.0",
        "use_case": "AI-assisted breast density assessment and cancer detection on mammography",
        "description": "Deep learning system for breast density assessment and cancer detection. Used in screening programs and clinical trials. 510(k) K243688.",
        "risk_tier": RiskTier.LIMITED,
        "annex": Annex.NONE,
        # INTENTIONAL: not started — no validation at all
        "validation_status": ValidationStatus.NOT_STARTED,
        "iq_complete": False,
        "oq_complete": False,
        "pq_complete": False,
        "owner": "Dr. Anna Kowalski",
        "last_review_date": None,
        "next_review_date": None,
    },
    {
        "name": "Arterys MICA",
        "vendor": "Arterys Inc.",
        "version": "2.1.0",
        "use_case": "AI-powered cardiac and perfusion imaging analysis for clinical diagnosis",
        "description": "Cloud-based AI platform for cardiovascular MRI analysis. One of the first FDA-cleared cloud-based AI diagnostic tools. 510(k) K182034.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Raj Sharma",
        "last_review_date": date(2026, 5, 10),
        "next_review_date": date(2027, 5, 10),
    },
    {
        "name": "Low EF AI-ECG Algorithm",
        "vendor": "Anumana, Inc.",
        "version": "1.0.0",
        "use_case": "AI detection of low ejection fraction from ECG for early heart failure screening",
        "description": "AI algorithm that analyzes ECG signals to detect low ejection fraction, enabling earlier identification of heart failure. Used in remote patient monitoring and clinical trials. 510(k) K232699.",
        "risk_tier": RiskTier.HIGH,
        "annex": Annex.III,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Sophie Martin",
        "last_review_date": date(2026, 2, 15),
        "next_review_date": date(2027, 2, 15),
    },
    {
        "name": "IRNF App",
        "vendor": "Apple Inc.",
        "version": "1.0.0",
        "use_case": "AI-powered atrial fibrillation detection from Apple Watch ECG recordings",
        "description": "Software as a medical device (SaMD) that uses AI to detect irregular heart rhythm from wrist-worn ECG. 510(k) K212516. Represents consumer health AI with medical device classification.",
        "risk_tier": RiskTier.LIMITED,
        "annex": Annex.NONE,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Pierre Dubois",
        "last_review_date": date(2026, 5, 20),
        "next_review_date": date(2027, 5, 20),
    },
    {
        "name": "MedChat Assist",
        "vendor": "DialogAI Health",
        "version": "2.0.0",
        "use_case": "Chatbot for patient-facing drug information queries",
        "description": "AI chatbot that answers patient questions about drug indications, side effects, and dosing. Not used for clinical decisions. Limited risk under Article 50 transparency obligations.",
        "risk_tier": RiskTier.LIMITED,
        "annex": Annex.NONE,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Sophie Martin",
        "last_review_date": date(2026, 2, 15),
        "next_review_date": date(2027, 2, 15),
    },
    {
        "name": "SupplyChain Predictor",
        "vendor": "LogiPharma AI",
        "version": "1.0.3",
        "use_case": "Pharmaceutical supply chain demand forecasting",
        "description": "Forecasts demand for pharmaceutical products based on historical sales, seasonal patterns, and market dynamics. Minimal risk under EU AI Act — no direct patient impact.",
        "risk_tier": RiskTier.MINIMAL,
        "annex": Annex.NONE,
        "validation_status": ValidationStatus.VALIDATED,
        "iq_complete": True,
        "oq_complete": True,
        "pq_complete": True,
        "owner": "Dr. Pierre Dubois",
        "last_review_date": date(2026, 5, 10),
        "next_review_date": date(2027, 5, 10),
    },
    # --- Prohibited use case (demo) ---
    {
        "name": "SocialRisk Score",
        "vendor": "DataProfiling Inc.",
        "version": "0.9.0",
        "use_case": "Social scoring of patients for insurance coverage decisions",
        "description": "Aggregates social media and behavioral data to score patients for insurance coverage eligibility. THIS IS AN EXAMPLE OF AN UNACCEPTABLE USE CASE UNDER EU AI ACT ARTICLE 5(1)(C) — social scoring by public authorities is prohibited.",
        "risk_tier": RiskTier.UNACCEPTABLE,
        "annex": Annex.II,
        "validation_status": ValidationStatus.NOT_STARTED,
        "iq_complete": False,
        "oq_complete": False,
        "pq_complete": False,
        "owner": "",
        "last_review_date": None,
        "next_review_date": None,
    },
]


def seed_db():
    """Seed the database with FDA-cleared AI/ML device entries, obligations, and validation steps."""
    db: Session = SessionLocal()
    try:
        existing = db.query(AISystem).first()
        if existing:
            return

        systems = []
        for system_data in SEED_SYSTEMS:
            system = AISystem(**system_data)
            db.add(system)
            systems.append(system)
        db.commit()

        # Refresh to get IDs
        for s in systems:
            db.refresh(s)

        # Create obligations and validation steps for each system
        obligation_count = 0
        step_count = 0
        for system in systems:
            risk_tier = system.risk_tier

            # Skip obligations/steps for UNACCEPTABLE systems
            if risk_tier == "UNACCEPTABLE":
                continue

            # Create obligations
            obl_defs = get_obligations_detailed(risk_tier)
            for obl_def in obl_defs:
                # Set realistic status based on validation status
                if system.validation_status == ValidationStatus.VALIDATED:
                    status = ObligationStatus.COMPLETE
                elif system.validation_status == ValidationStatus.IN_PROGRESS:
                    status = ObligationStatus.IN_PROGRESS if obl_def.get("category") in ["risk-management", "documentation"] else ObligationStatus.NOT_STARTED
                else:
                    status = ObligationStatus.NOT_STARTED

                obl = Obligation(
                    system_id=system.id,
                    article=obl_def["article"],
                    obligation=obl_def["obligation"],
                    category=obl_def.get("category", ""),
                    required=obl_def.get("required", True),
                    status=status,
                )
                db.add(obl)
                obligation_count += 1

            # Create validation steps
            step_templates = get_gmlp_steps(risk_tier)
            for phase, steps in step_templates.items():
                for step_def in steps:
                    # Set realistic status based on system validation status
                    if system.validation_status == ValidationStatus.VALIDATED:
                        step_status = StepStatus.COMPLETE
                    elif system.validation_status == ValidationStatus.IN_PROGRESS:
                        if phase == "IQ" and system.iq_complete:
                            step_status = StepStatus.COMPLETE
                        elif phase == "OQ" and not system.oq_complete:
                            step_status = StepStatus.IN_PROGRESS if step_def.get("sort_order", 0) <= 2 else StepStatus.NOT_STARTED
                        elif phase == "PQ":
                            step_status = StepStatus.NOT_STARTED
                        else:
                            step_status = StepStatus.NOT_STARTED
                    elif system.validation_status == ValidationStatus.REQUIRES_REVALIDATION:
                        step_status = StepStatus.COMPLETE  # Was validated, now needs revalidation
                    else:
                        step_status = StepStatus.NOT_STARTED

                    vs = ValidationStep(
                        system_id=system.id,
                        phase=phase,
                        step_key=step_def["step_key"],
                        step_label=step_def["step_label"],
                        source=step_def.get("source", ""),
                        sort_order=step_def.get("sort_order", 0),
                        status=step_status,
                    )
                    db.add(vs)
                    step_count += 1

        db.commit()
        print(f"Seeded {len(SEED_SYSTEMS)} AI systems, {obligation_count} obligations, {step_count} validation steps")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()