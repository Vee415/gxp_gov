"""
EMA Guidance Mapping

Maps EMA (European Medicines Agency) AI guidance requirements to
validation checks. Based on:
- EMA/CHMP/CVMP/83833/2023 — Reflection Paper on AI in the Medicinal
  Product Lifecycle (adopted September 2024)
- EMA-FDA Guiding Principles of Good AI Practice in Drug Development (Jan 2026)
- EU GMP Annex 22 (Draft) — Artificial Intelligence in Manufacturing
- EU GMP Annex 11 (2025 Draft Revision) — Computerised Systems
- 21 CFR Part 11 — Electronic Records; Electronic Signatures (FDA)

The 7 lifecycle stages are from the EMA reflection paper. Each check
is tagged with its source document and article/section reference.
"""

# ---------------------------------------------------------------------------
# EMA Lifecycle Stages (from Section 2.3 of the reflection paper)
# ---------------------------------------------------------------------------

LIFECYCLE_STAGES: list[dict] = [
    {
        "id": "drug-discovery",
        "name": "Drug Discovery",
        "section": "2.3.1",
        "risk_level": "Low regulatory impact by default",
        "key_requirement": "If AI results contribute to the evidence body for regulatory review, non-clinical development principles apply. Bias review mandatory on all models/datasets — must mitigate discrimination against non-majority genotypes/phenotypes.",
    },
    {
        "id": "non-clinical",
        "name": "Non-Clinical Development",
        "section": "2.3.2",
        "risk_level": "Medium regulatory impact",
        "key_requirement": "Existing SOPs must extend to all AI/ML applications. OECD GLP Principles apply, including Advisory Document No. 17 (Computerised Systems) and No. 22 (Data Integrity). Applications affecting patient safety require prospective model performance testing.",
    },
    {
        "id": "clinical-trials",
        "name": "Clinical Trials",
        "section": "2.3.3",
        "risk_level": "High patient risk AND high regulatory impact",
        "key_requirement": "GCP compliance per ICH E6. Pivotal trials: frozen models, no incremental learning, pre-specified SAP, prospectively generated test data. High-impact use may require full model architecture, training data, and development logs.",
    },
    {
        "id": "precision-medicine",
        "name": "Precision Medicine",
        "section": "2.3.4",
        "risk_level": "High patient risk AND high regulatory impact",
        "key_requirement": "Includes patient selection, dosing, product variant design. Fall-back treatment strategies mandatory for technical failures. Prescriber guidance must be critically understandable. May be referenced in SmPC.",
    },
    {
        "id": "product-information",
        "name": "Product Information",
        "section": "2.3.5",
        "risk_level": "Medium regulatory impact",
        "key_requirement": "AI drafting/translation must operate under close human supervision. Quality review mechanisms must ensure factual and syntactic correctness before submission. Generative models acknowledged as producing plausible but erroneous output.",
    },
    {
        "id": "manufacturing",
        "name": "Manufacturing",
        "section": "2.3.6",
        "risk_level": "High regulatory impact",
        "key_requirement": "Process design, scale-up, in-process QC, and batch release must follow ICH Q8/Q9/Q10. Annex 22 (draft) addresses AI in GMP. Generative AI/LLMs prohibited as autonomous decision-makers in critical applications.",
    },
    {
        "id": "post-authorisation",
        "name": "Post-Authorisation",
        "section": "2.3.7",
        "risk_level": "Variable — depends on use",
        "key_requirement": "Pharmacovigilance allows more flexible modelling including incremental learning for signal detection. MAH remains responsible for validation/monitoring. Pivotal-level requirements may apply to PASS/PAES if they are MA conditions.",
    },
]


# ---------------------------------------------------------------------------
# GxP Validation Checks (adapted IQ/OQ/PQ for AI/ML — GMLP framework)
# ---------------------------------------------------------------------------

EMA_VALIDATION_CHECKS: dict[str, list[dict]] = {
    "data_integrity": [
        {
            "requirement": "ALCOA+ principles for electronic records",
            "source": "EU Annex 11 / 21 CFR Part 11",
            "description": "Data must be Attributable, Legible, Contemporaneous, Original, and Complete. Extended to ALCOA+ (Complete, Consistent, Enduring, Available).",
            "check": "Audit trail must capture who, what, when, and why for all data changes",
            "article": "Annex 11 §13; 21 CFR Part 11 §11.10(e)",
            "lifecycle_stages": ["clinical-trials", "manufacturing", "post-authorisation"],
        },
        {
            "requirement": "Electronic signature compliance",
            "source": "21 CFR Part 11",
            "description": "Electronic signatures must be equivalent to handwritten signatures. Must include signer identification, date/time, and meaning (e.g., review, approval).",
            "check": "System must require authentication for electronic approvals; meaning of signature must be captured",
            "article": "21 CFR Part 11 §11.50, §11.100",
            "lifecycle_stages": ["clinical-trials", "manufacturing", "post-authorisation"],
        },
        {
            "requirement": "Immutable audit trail",
            "source": "EU Annex 11 (2025 Draft Revision)",
            "description": "Audit trails must be immutable, ALCOA++ aligned, with periodic review mandated. No deletion without documented authorisation.",
            "check": "All AI system actions, inputs, outputs, and human decisions must be captured in an immutable trail with periodic review",
            "article": "Annex 11 §13; Annex 22 §9",
            "lifecycle_stages": ["clinical-trials", "manufacturing", "post-authorisation"],
        },
    ],
    "ai_specific": [
        {
            "requirement": "Model documentation and transparency",
            "source": "EMA/CHMP/CVMP/83833/2023",
            "description": "Complete documentation of AI model architecture, training data, and performance. Black-box models only acceptable if developers substantiate that interpretable models show unsatisfactory performance.",
            "check": "Model card or equivalent documentation must exist and be maintained. For black-box models: full architecture, hyperparameters, training metrics, validation/test results, and monitoring plan required.",
            "article": "Section 2.3.3; Section 2.4.2",
            "lifecycle_stages": ["clinical-trials", "precision-medicine", "manufacturing"],
        },
        {
            "requirement": "Bias and fairness assessment",
            "source": "EMA/CHMP/CVMP/83833/2023",
            "description": "Mandatory bias review on all models and datasets — must mitigate discrimination against non-majority genotypes/phenotypes. Performance metrics must be insensitive to class imbalances.",
            "check": "Documented bias analysis for demographic subgroups. Matthews Correlation Coefficient and minority-class sensitivity analysis required.",
            "article": "Section 2.3.1; Section 2.4.3",
            "lifecycle_stages": ["drug-discovery", "clinical-trials", "precision-medicine"],
        },
        {
            "requirement": "Frozen model enforcement for pivotal trials",
            "source": "EMA/CHMP/CVMP/83833/2023",
            "description": "All parameters must be set before deployment. No incremental learning in high regulatory impact settings. Data pre-processing pipeline and models must be frozen and documented in the SAP prior to database lock.",
            "check": "Model freeze checkpoint documented before database lock. No post-freeze modifications without SAP amendment. Any non-pre-specified changes treated as post hoc evidence.",
            "article": "Section 2.3.3",
            "lifecycle_stages": ["clinical-trials"],
        },
        {
            "requirement": "Continuous monitoring and drift detection",
            "source": "EMA/CHMP/CVMP/83833/2023; Annex 22 (Draft)",
            "description": "Ongoing monitoring of AI system performance and drift. Scheduled re-evaluation with defined drift thresholds and suspension/decommissioning triggers.",
            "check": "Monitoring plan with defined thresholds and escalation procedures. Drift detection alerts configured.",
            "article": "Section 2.4.4; Annex 22 §7",
            "lifecycle_stages": ["clinical-trials", "manufacturing", "post-authorisation"],
        },
        {
            "requirement": "Human oversight mechanism",
            "source": "EU AI Act Article 14; EMA Reflection Paper",
            "description": "Meaningful human control over AI-assisted decisions. HITL documentation for all GxP-relevant applications. Autonomous LLM/gen AI prohibited in critical GMP applications.",
            "check": "Documented human-in-the-loop process for all high-stakes decisions. Fall-back treatment strategies for precision medicine. No autonomous AI in critical GMP decisions.",
            "article": "Article 14; Section 2.4.1; Annex 22 §8",
            "lifecycle_stages": ["clinical-trials", "precision-medicine", "manufacturing", "post-authorisation"],
        },
        {
            "requirement": "Explainability (XAI) requirements",
            "source": "EMA/CHMP/CVMP/83833/2023; Annex 22 (Draft)",
            "description": "Three key requirements: Predictable, Auditable, Explainable. SHAP and/or LIME analyses (global and per-inference) mandatory for high-risk. Class activation/saliency/attention maps for computer vision.",
            "check": "XAI documentation available for all high-risk AI outputs. Global and local explanations generated and reviewable.",
            "article": "Section 2.4.2; Annex 22 §6",
            "lifecycle_stages": ["clinical-trials", "precision-medicine", "manufacturing"],
        },
    ],
    "gxp_validation": [
        {
            "requirement": "Installation Qualification (IQ) — adapted for AI",
            "source": "GAMP 5 / GMLP Framework",
            "description": "Verify the AI system is installed correctly, including data ingestion pipeline. Must verify training data ingested correctly without corruption.",
            "check": "IQ protocol and report documenting: correct installation, data ingestion verification, environment configuration, version control",
            "article": "GAMP 5; GMLP Framework Table",
            "lifecycle_stages": ["clinical-trials", "manufacturing"],
        },
        {
            "requirement": "Operational Qualification (OQ) — adapted for AI",
            "source": "GAMP 5 / GMLP Framework",
            "description": "Verify the AI system operates as specified. For AI: model training and validation on held-out data, demonstrating performance meets URS acceptance criteria.",
            "check": "OQ protocol and report covering: model training execution, validation-set performance, all functional requirements met",
            "article": "GAMP 5; GMLP Framework Table",
            "lifecycle_stages": ["clinical-trials", "manufacturing"],
        },
        {
            "requirement": "Performance Qualification (PQ) — adapted for AI",
            "source": "GAMP 5 / GMLP Framework",
            "description": "Verify the AI system performs consistently under real-world conditions. Final locked model tested on held-out test set. Must meet URS acceptance criteria on prospectively generated data.",
            "check": "PQ protocol and report demonstrating: consistent performance on test data, bias/fairness assessment, XAI outputs, acceptance criteria met",
            "article": "GAMP 5; GMLP Framework Table",
            "lifecycle_stages": ["clinical-trials", "manufacturing"],
        },
        {
            "requirement": "Change control for model modifications",
            "source": "EU Annex 11; Annex 22 (Draft)",
            "description": "All model modifications require formal change control with revalidation assessment. Changes must be documented with impact assessment and regulatory notification if required.",
            "check": "Change control procedure in place. All model version changes documented with revalidation assessment.",
            "article": "Annex 11 §4; Annex 22 §10",
            "lifecycle_stages": ["clinical-trials", "manufacturing", "post-authorisation"],
        },
        {
            "requirement": "Periodic re-evaluation",
            "source": "EU Annex 11 (2025 Draft); EMA Reflection Paper",
            "description": "AI models require scheduled re-evaluation for data drift and performance degradation. Define drift thresholds and suspension/decommissioning triggers.",
            "check": "Revalidation schedule defined with drift thresholds. Next review date tracked in registry.",
            "article": "Annex 11 §7; Section 2.4.4",
            "lifecycle_stages": ["clinical-trials", "manufacturing", "post-authorisation"],
        },
    ],
    "data_governance": [
        {
            "requirement": "Data provenance and traceability",
            "source": "EMA Reflection Paper; Article 10",
            "description": "Full traceability of data sources, acquisition, cleaning, transformation, imputation, annotation, normalization, and augmentation. Must comply with GxP requirements and GDPR.",
            "check": "Data lineage documentation from source to model input. GDPR compliance assessment documented.",
            "article": "Section 2.4.3; Article 10",
            "lifecycle_stages": ["drug-discovery", "clinical-trials", "manufacturing"],
        },
        {
            "requirement": "Train/test/validation splits",
            "source": "EMA Reflection Paper; Annex 22 (Draft)",
            "description": "Early split before any normalization or processing is strongly encouraged. Test data cannot be re-used; new independent dataset required if further development is needed.",
            "check": "Documented data split strategy with independence verification. Test data not used in training or hyperparameter tuning.",
            "article": "Section 2.3.3; Annex 22 §5",
            "lifecycle_stages": ["clinical-trials", "precision-medicine"],
        },
        {
            "requirement": "Subgroup analysis and class imbalance",
            "source": "EMA Reflection Paper; Annex 22 (Draft)",
            "description": "Input sample space must be divided into subgroups with performance evaluated across all. Performance metrics must be insensitive to class imbalances (e.g., Matthews Correlation Coefficient).",
            "check": "Subgroup performance documented. Minority-class sensitivity analysis completed. Class imbalance mitigation documented.",
            "article": "Section 2.4.3; Annex 22 §6",
            "lifecycle_stages": ["clinical-trials", "precision-medicine"],
        },
    ],
}


def get_ema_checks(category: str | None = None) -> list[dict]:
    """Return EMA validation checks, optionally filtered by category."""
    if category and category in EMA_VALIDATION_CHECKS:
        return EMA_VALIDATION_CHECKS[category]
    all_checks = []
    for checks in EMA_VALIDATION_CHECKS.values():
        all_checks.extend(checks)
    return all_checks


def get_relevant_checks(use_case: str) -> list[dict]:
    """Return EMA checks relevant to a given use case based on lifecycle stage matching."""
    text = use_case.lower()

    # Map keywords to lifecycle stages
    stage_keywords = {
        "drug-discovery": ["drug discovery", "target identification", "lead optimization", "screening"],
        "non-clinical": ["non-clinical", "preclinical", "toxicology", "adme", "animal model"],
        "clinical-trials": ["clinical trial", "patient stratification", "trial design", "oncology",
                           "phase i", "phase ii", "phase iii", "endpoint", "enrollment", "trial arm",
                           "dose optimization", "safety signal", "adverse event", "pharmacovigilance"],
        "precision-medicine": ["precision medicine", "companion diagnostic", "biomarker", "genomic",
                              "personalized", "patient selection", "dosing"],
        "product-information": ["label", "smplc", "product information", "regulatory submission",
                               "labeling", "package insert"],
        "manufacturing": ["manufacturing", "process control", "quality control", "batch release",
                         "in-process", "gmp", "production", "formulation"],
        "post-authorisation": ["pharmacovigilance", "post-market", "signal detection", "safety monitoring",
                              "pass", "paes", "adverse event reporting", "real-world evidence"],
    }

    matched_stages = set()
    for stage, keywords in stage_keywords.items():
        for keyword in keywords:
            if keyword in text:
                matched_stages.add(stage)

    # If no specific stage matched, default to clinical-trials and manufacturing (broadest pharma use)
    if not matched_stages:
        matched_stages = {"clinical-trials", "manufacturing"}

    # All AI systems in pharma need GxP validation
    relevant = list(EMA_VALIDATION_CHECKS["gxp_validation"])

    # Add AI-specific and data governance checks for matching stages
    for check in EMA_VALIDATION_CHECKS["ai_specific"]:
        if any(stage in check.get("lifecycle_stages", []) for stage in matched_stages):
            relevant.append(check)

    for check in EMA_VALIDATION_CHECKS["data_governance"]:
        if any(stage in check.get("lifecycle_stages", []) for stage in matched_stages):
            relevant.append(check)

    for check in EMA_VALIDATION_CHECKS["data_integrity"]:
        if any(stage in check.get("lifecycle_stages", []) for stage in matched_stages):
            relevant.append(check)

    return relevant


def get_lifecycle_stages() -> list[dict]:
    """Return all EMA lifecycle stages with their risk levels and key requirements."""
    return LIFECYCLE_STAGES