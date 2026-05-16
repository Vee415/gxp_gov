"""
EU AI Act Risk Classification Rules

Based on Regulation (EU) 2024/1689 — the final adopted text of the EU AI Act.

Classification logic extracted from:
- Article 5: Prohibited AI practices
- Article 6: Classification rules for high-risk AI systems
- Annex III: High-risk AI system categories (8 categories)

Obligations extracted from:
- Articles 9-16: High-risk system obligations
- Article 50: Transparency obligations for limited-risk systems (final numbering)
- Article 69: Voluntary codes of conduct for minimal-risk systems

Checklist data derived from:
- AbdelStark/eu-ai-act-toolkit (MIT license)
- EMA/CHMP/CVMP/83833/2023 Reflection Paper

This is intentionally rule-based (not ML) because explainability is a hard
requirement in regulated contexts. A model that classifies AI risk cannot
itself be a black box.
"""

# ---------------------------------------------------------------------------
# Article 5 — Prohibited AI Practices
# ---------------------------------------------------------------------------

PROHIBITED_PRACTICES: list[dict] = [
    {
        "id": "art5-subliminal",
        "practice": "Subliminal manipulation",
        "description": "AI systems that deploy subliminal techniques beyond a person's consciousness to materially distort behaviour in a manner that causes or is likely to cause physical or psychological harm.",
        "article": "Article 5(1)(a)",
    },
    {
        "id": "art5-exploitation",
        "practice": "Exploitation of vulnerabilities",
        "description": "AI systems that exploit vulnerabilities of specific groups (age, disability, socioeconomic situation) to materially distort behaviour in a manner that causes or is likely to cause harm.",
        "article": "Article 5(1)(b)",
    },
    {
        "id": "art5-social-scoring",
        "practice": "Social scoring by public authorities",
        "description": "AI systems used by public authorities or on their behalf that evaluate or classify natural persons based on social behaviour or personal characteristics, leading to detrimental treatment unrelated to the original context.",
        "article": "Article 5(1)(c)",
    },
    {
        "id": "art5-prediction-criminal",
        "practice": "Individual predictive policing",
        "description": "AI systems that assess the risk of a natural person committing a criminal offence based solely on profiling or personality traits, without being based on objective, verifiable facts directly linked to the criminal activity.",
        "article": "Article 5(1)(d)",
    },
    {
        "id": "art5-facial-scraping",
        "practice": "Untargeted facial image scraping",
        "description": "AI systems that create facial recognition databases by untargeted scraping of facial images from the internet or CCTV footage.",
        "article": "Article 5(1)(e)",
    },
    {
        "id": "art5-emotion-workplace",
        "practice": "Emotion inference in workplace/education",
        "description": "AI systems that infer emotions from biometric data in workplace or educational contexts, except for medical or safety purposes.",
        "article": "Article 5(1)(f)",
    },
    {
        "id": "art5-biocategorization",
        "practice": "Biometric categorization for sensitive attributes",
        "description": "AI systems that use biometric categorization to deduce race, religion, political opinion, trade union membership, ethnic origin, health status, or sexual orientation.",
        "article": "Article 5(1)(g)",
    },
    {
        "id": "art5-realtime-biometric",
        "practice": "Real-time remote biometric identification in public spaces",
        "description": "Use of real-time remote biometric identification systems in publicly accessible spaces for law enforcement purposes, with only narrow exceptions strictly defined in Article 5(3).",
        "article": "Article 5(1)(h)",
    },
]

# Keyword matching for prohibited practices
PROHIBITED_KEYWORDS: list[dict] = [
    {"keywords": ["social scoring", "social score", "social credit"], "practice_id": "art5-social-scoring"},
    {"keywords": ["subliminal manipulation", "subliminal technique", "subconscious"], "practice_id": "art5-subliminal"},
    {"keywords": ["exploit vulnerability", "exploitation of vulnerability", "vulnerable group targeting"], "practice_id": "art5-exploitation"},
    {"keywords": ["predictive policing", "predict crime", "criminal risk prediction", "offender risk"], "practice_id": "art5-prediction-criminal"},
    {"keywords": ["facial scraping", "untargeted facial", "face scraping"], "practice_id": "art5-facial-scraping"},
    {"keywords": ["emotion recognition workplace", "emotion inference employee", "emotion detection student"], "practice_id": "art5-emotion-workplace"},
    {"keywords": ["biometric categorization sensitive", "biometric race", "biometric sexual orientation"], "practice_id": "art5-biocategorization"},
    {"keywords": ["real-time remote biometric identification", "realtime biometric", "live facial recognition public"], "practice_id": "art5-realtime-biometric"},
]


# ---------------------------------------------------------------------------
# Article 6 — Classification Rules for High-Risk AI Systems
# ---------------------------------------------------------------------------

CLASSIFICATION_RULES: list[dict] = [
    {
        "id": "art6-1a",
        "rule": "AI system is a safety component of, or is itself, a product covered by Union harmonisation legislation listed in Annex I, requiring third-party conformity assessment.",
        "article": "Article 6(1)(a)",
    },
    {
        "id": "art6-1b",
        "rule": "AI system falls within one of the areas listed in Annex III, unless it does not pose a significant risk of harm to health, safety, or fundamental rights.",
        "article": "Article 6(1)(b)",
    },
    {
        "id": "art6-3-exemption",
        "rule": "An Annex III AI system is NOT high-risk if it does not pose a significant risk of harm because it: (a) performs narrow procedural tasks, (b) improves previously completed human activity, (c) detects decision-making patterns or deviations without replacing human review, or (d) performs preparatory tasks to an assessment listed in Annex III.",
        "article": "Article 6(3)",
    },
]


# ---------------------------------------------------------------------------
# Annex III — High-Risk AI System Categories (8 categories from final text)
# ---------------------------------------------------------------------------

ANNEX_III_CATEGORIES: list[dict] = [
    {
        "category": 1,
        "id": "biometrics",
        "title": "Biometrics",
        "items": [
            "Remote biometric identification (not real-time in public spaces for law enforcement, which is prohibited)",
            "Biometric categorization based on sensitive or protected attributes",
            "Emotion recognition",
        ],
    },
    {
        "category": 2,
        "id": "critical-infrastructure",
        "title": "Critical Infrastructure",
        "items": [
            "AI systems used as safety components in the management and operation of road traffic",
            "AI systems used as safety components in the management and operation of water supply",
            "AI systems used as safety components in the management and operation of gas supply",
            "AI systems used as safety components in the management and operation of heating supply",
            "AI systems used as safety components in the management and operation of electricity supply",
        ],
    },
    {
        "category": 3,
        "id": "education",
        "title": "Education",
        "items": [
            "Determining access to or admission into educational or vocational training institutions",
            "Evaluating learning outcomes, including to steer the learning process",
            "Determining the appropriate level of education for an individual",
            "Monitoring and detecting prohibited behaviour of students during tests",
        ],
    },
    {
        "category": 4,
        "id": "employment",
        "title": "Employment",
        "items": [
            "Recruitment or selection, particularly for placing targeted job advertisements, filtering applications, and evaluating candidates",
            "Making decisions affecting terms of work-related relationships, promotion, or termination",
            "Allocating tasks based on individual behaviour, personal traits, or characteristics",
            "Monitoring and evaluating performance and behaviour of persons in work-related relationships",
        ],
    },
    {
        "category": 5,
        "id": "essential-services",
        "title": "Essential Services (including Healthcare)",
        "items": [
            "Evaluating eligibility for public assistance benefits and services, granting, reducing, revoking, or reclaiming such benefits",
            "Evaluating creditworthiness of natural persons (except for detecting financial fraud)",
            "Risk assessment and pricing in life and health insurance for natural persons",
            "Evaluating and classifying emergency calls, including for establishing dispatching priority",
        ],
    },
    {
        "category": 6,
        "id": "law-enforcement",
        "title": "Law Enforcement",
        "items": [
            "Individual risk assessment of natural persons to assess the likelihood of offending or re-offending, or of being a victim of criminal offences",
            "Use as polygraphs or similar tools to detect deception",
            "Evaluating the reliability of evidence in the course of investigation or prosecution of criminal offences",
            "Profiling of natural persons in the course of detection, investigation, or prosecution of criminal offences",
        ],
    },
    {
        "category": 7,
        "id": "migration",
        "title": "Migration, Asylum, and Border Control",
        "items": [
            "Assessing a risk of irregular migration or a health risk posed by a natural person intending to enter or having entered the territory of a Member State",
            "Examining applications for asylum, visa, or residence permits, and associated complaints regarding the eligibility of persons",
            "Detecting, recognizing, or identifying natural persons in the context of migration, asylum, and border control (except verification of travel documents)",
        ],
    },
    {
        "category": 8,
        "id": "justice-democracy",
        "title": "Justice and Democratic Processes",
        "items": [
            "Assisting judicial authorities in researching and interpreting facts and the law, and in applying the law to a concrete set of facts",
            "Influencing the outcome of an election or referendum (excluding organisational tools that do not directly influence how individuals cast votes)",
        ],
    },
]

# Keyword matching for Annex III high-risk categories
HIGH_RISK_KEYWORDS: dict[str, list[str]] = {
    "biometrics": [
        "biometric", "facial recognition", "fingerprint", "iris scan",
        "identity verification", "person identification", "emotion recognition",
    ],
    "critical_infrastructure": [
        "critical infrastructure", "energy supply", "water supply",
        "traffic management", "grid operation", "nuclear", "power plant",
        "road traffic", "gas supply", "heating supply", "electricity supply",
    ],
    "education": [
        "education", "admission", "student assessment", "learning outcome",
        "education scoring", "vocational training",
    ],
    "employment": [
        "hiring", "recruitment", "employee evaluation", "student assessment",
        "job selection", "candidate filtering", "work performance monitoring",
        "task allocation",
    ],
    "essential_services": [
        # Healthcare — AI that makes or informs decisions about patient health
        "clinical trial", "patient stratification", "medical diagnosis",
        "treatment recommendation", "patient enrollment", "trial arm",
        "clinical decision", "drug interaction", "prescription",
        "surgical", "medical imaging", "diagnostic", "pathology",
        "cancer detection", "cancer screening", "biopsy",
        "adverse event detection", "safety signal detection",
        "pharmacovigilance", "drug safety monitoring",
        "disease detection", "tumor", "lesion detection",
        "cardiac", "heart", "coronary", "arrhythmia", "ecg",
        "echocardiograph", "amyloidosis", "ejection fraction",
        "blood count", "hematology", "kidney disease",
        "blood analysis", "urine analysis",
        "digital twin", "companion diagnostic",
        # Credit/insurance — AI that determines access to services
        "public assistance eligibility", "credit scoring", "creditworthiness",
        "insurance risk assessment", "insurance pricing", "emergency dispatch",
        "emergency call classification", "life and health insurance",
    ],
    "law_enforcement": [
        "law enforcement", "polygraph", "criminal profiling", "crime prediction",
        "surveillance", "offender risk", "deception detection", "evidence evaluation",
    ],
    "migration": [
        "migration", "asylum", "visa", "border control", "deportation",
        "immigration", "irregular migration",
    ],
    "justice_democratic": [
        "court", "legal", "judicial", "democratic process", "voting",
        "election process", "legislative process", "democratic participation",
    ],
}

LIMITED_KEYWORDS: list[str] = [
    "chatbot", "customer service", "content recommendation",
    "spam filter", "search engine", "social media",
    "marketing", "advertising", "content generation",
    "translation", "sentiment analysis",
]


# ---------------------------------------------------------------------------
# Obligations per Risk Tier (from Articles 9-16, 50, 69)
# ---------------------------------------------------------------------------

OBLIGATIONS: dict[str, list[dict]] = {
    "UNACCEPTABLE": [
        {
            "article": "Article 5(1)",
            "obligation": "Prohibited — this AI system cannot be deployed in the EU",
            "required": False,
            "category": "prohibited",
        },
        {
            "article": "Article 5(1)(c)",
            "obligation": "Social scoring by public authorities is prohibited",
            "required": True,
            "category": "prohibited",
        },
        {
            "article": "Article 5(1)(h)",
            "obligation": "Real-time remote biometric identification in public spaces is prohibited (narrow exceptions in Article 5(3))",
            "required": True,
            "category": "prohibited",
        },
        {
            "article": "Article 5(1)(a)",
            "obligation": "Subliminal manipulation techniques are prohibited",
            "required": True,
            "category": "prohibited",
        },
        {
            "article": "Article 5(1)(b)",
            "obligation": "Exploitation of vulnerabilities of specific groups is prohibited",
            "required": True,
            "category": "prohibited",
        },
    ],
    "HIGH": [
        {
            "article": "Article 9",
            "obligation": "Risk management system — continuous identification, analysis, and mitigation of risks throughout the entire lifecycle",
            "required": True,
            "category": "risk-management",
        },
        {
            "article": "Article 10",
            "obligation": "Data governance — training, validation, and testing datasets must be relevant, representative, free of errors, and examined for biases",
            "required": True,
            "category": "data-governance",
        },
        {
            "article": "Article 11",
            "obligation": "Technical documentation — complete record of system design, development process, training data, monitoring mechanisms, and risk management compliance",
            "required": True,
            "category": "documentation",
        },
        {
            "article": "Article 13",
            "obligation": "Transparency — systems must be designed to enable deployers to interpret output and use it appropriately; instructions for use must include capabilities, limitations, and intended purpose",
            "required": True,
            "category": "transparency",
        },
        {
            "article": "Article 14",
            "obligation": "Human oversight — systems must allow effective oversight by natural persons, including ability to understand capacities/limitations, monitor anomalies, override output, and interrupt operation",
            "required": True,
            "category": "human-oversight",
        },
        {
            "article": "Article 15",
            "obligation": "Accuracy, robustness, and cybersecurity — appropriate accuracy levels, resilience to errors and adversarial attacks, fail-safe mechanisms, and proportionate cybersecurity measures",
            "required": True,
            "category": "accuracy-robustness",
        },
        {
            "article": "Article 16",
            "obligation": "Quality management system — systematic processes for compliance throughout the lifecycle, including conformity assessment, CE marking, and registration obligations",
            "required": True,
            "category": "documentation",
        },
    ],
    "LIMITED": [
        {
            "article": "Article 50(1)",
            "obligation": "Inform users they are interacting with an AI system (unless obvious from context)",
            "required": True,
            "category": "transparency",
        },
        {
            "article": "Article 50(2)",
            "obligation": "Mark synthetic content (deepfakes, AI-generated text/images/audio/video) as artificially generated or manipulated",
            "required": True,
            "category": "transparency",
        },
        {
            "article": "Article 50(2)",
            "obligation": "Ensure synthetic content marking is machine-readable where technically feasible",
            "required": True,
            "category": "transparency",
        },
        {
            "article": "Article 50(3)",
            "obligation": "Inform persons exposed to emotion recognition systems that the system is in operation",
            "required": True,
            "category": "transparency",
        },
        {
            "article": "Article 50(4)",
            "obligation": "Inform persons exposed to biometric categorization systems that the system is in operation",
            "required": True,
            "category": "transparency",
        },
    ],
    "MINIMAL": [
        {
            "article": "Article 69",
            "obligation": "No specific obligations under the EU AI Act for minimal-risk systems",
            "required": False,
            "category": "documentation",
        },
        {
            "article": "Article 69",
            "obligation": "Voluntary codes of conduct are encouraged",
            "required": False,
            "category": "documentation",
        },
    ],
}


# ---------------------------------------------------------------------------
# Classification Function
# ---------------------------------------------------------------------------

def classify_risk(use_case: str, description: str = "") -> dict:
    """Classify an AI system's risk tier based on its use case description.

    Uses the EU AI Act classification logic from Article 6 and Annex III.
    Every classification includes the specific article/annex that triggered it,
    making every decision explainable.
    """
    text = f"{use_case} {description}".lower()
    triggered_rules = []
    triggered_practices = []

    # Step 1: Check prohibited practices (Article 5) — highest priority
    for rule in PROHIBITED_KEYWORDS:
        for keyword in rule["keywords"]:
            if keyword in text:
                practice = next(
                    (p for p in PROHIBITED_PRACTICES if p["id"] == rule["practice_id"]), None
                )
                if practice and practice not in triggered_practices:
                    triggered_practices.append(practice)
                    triggered_rules.append(
                        f"{practice['article']}: {practice['practice']} — prohibited under EU AI Act"
                    )

    if triggered_practices:
        return {
            "risk_tier": "UNACCEPTABLE",
            "annex": "II",
            "triggered_rules": triggered_rules,
            "prohibited_practices": [
                {"id": p["id"], "practice": p["practice"], "article": p["article"]}
                for p in triggered_practices
            ],
        }

    # Step 2: Check high-risk categories (Annex III)
    for category_key, keywords in HIGH_RISK_KEYWORDS.items():
        # Normalize: keyword dict uses underscores, Annex III IDs use hyphens
        normalized_key = category_key.replace("_", "-")
        category = next(
            (c for c in ANNEX_III_CATEGORIES if c["id"] == normalized_key), None
        )
        if not category:
            continue
        for keyword in keywords:
            if keyword in text:
                triggered_rules.append(
                    f"Annex III - Category {category['category']}: {category['title']} — "
                    f"'{keyword}' matches high-risk use case"
                )

    if triggered_rules:
        return {
            "risk_tier": "HIGH",
            "annex": "III",
            "triggered_rules": triggered_rules,
        }

    # Step 3: Check limited risk (Article 50 transparency obligations)
    for keyword in LIMITED_KEYWORDS:
        if keyword in text:
            return {
                "risk_tier": "LIMITED",
                "annex": "None",
                "triggered_rules": [
                    f"Article 50: '{keyword}' triggers transparency obligations "
                    f"for limited-risk AI systems"
                ],
            }

    # Step 4: Default to minimal risk
    return {
        "risk_tier": "MINIMAL",
        "annex": "None",
        "triggered_rules": [
            "No high-risk or limited-risk triggers identified. "
            "Classified as minimal risk under EU AI Act."
        ],
    }


def get_obligations(risk_tier: str) -> list[str]:
    """Return the obligations that apply to a given risk tier.

    Based on Articles 5, 9-16, 50, and 69 of Regulation (EU) 2024/1689.
    """
    tier_obligations = OBLIGATIONS.get(risk_tier, [])
    return [o["obligation"] for o in tier_obligations]


def get_obligations_detailed(risk_tier: str) -> list[dict]:
    """Return detailed obligations with article references and categories."""
    return OBLIGATIONS.get(risk_tier, [])


def get_gap_analysis(risk_tier: str, annex: str) -> dict:
    """Return a gap analysis template for the given risk tier.

    In a production system, this would compare against actual documentation
    in the registry. For the MVP, it returns the required vs documented
    framework with documented items marked as pending.
    """
    if risk_tier == "UNACCEPTABLE":
        practices = PROHIBITED_PRACTICES
        return {
            "status": "prohibited",
            "required": ["Prohibited — no deployment possible in the EU"],
            "documented": [],
            "gaps": [
                f"{p['article']}: {p['practice']} — prohibited"
                for p in practices
            ],
        }

    if risk_tier == "HIGH":
        required_docs = [
            "Risk management system — continuous lifecycle process (Article 9)",
            "Data governance — training data relevance, representativeness, bias examination (Article 10)",
            "Technical documentation — system design, development, performance (Article 11)",
            "Transparency — deployer information and instructions for use (Article 13)",
            "Human oversight — ability to understand, monitor, override, interrupt (Article 14)",
            "Accuracy, robustness, and cybersecurity — demonstrated performance and resilience (Article 15)",
            "Quality management system — lifecycle compliance processes (Article 16)",
        ]
        return {
            "status": "action_required",
            "required": required_docs,
            "documented": [],
            "gaps": required_docs,
        }

    if risk_tier == "LIMITED":
        return {
            "status": "transparency_required",
            "required": [
                "User disclosure — inform users they are interacting with AI (Article 50(1))",
                "Synthetic content marking — mark AI-generated content as artificial (Article 50(2))",
                "Machine-readable marking — where technically feasible (Article 50(2))",
                "Emotion recognition disclosure — inform exposed persons (Article 50(3))",
                "Biometric categorization disclosure — inform exposed persons (Article 50(4))",
            ],
            "documented": [],
            "gaps": [
                "User disclosure — inform users they are interacting with AI (Article 50(1))",
                "Synthetic content marking — mark AI-generated content as artificial (Article 50(2))",
                "Machine-readable marking — where technically feasible (Article 50(2))",
                "Emotion recognition disclosure — inform exposed persons (Article 50(3))",
                "Biometric categorization disclosure — inform exposed persons (Article 50(4))",
            ],
        }

    return {
        "status": "compliant",
        "required": ["No specific obligations under the EU AI Act"],
        "documented": [],
        "gaps": [],
    }


def get_annex_iii_categories() -> list[dict]:
    """Return the full Annex III high-risk AI system categories."""
    return ANNEX_III_CATEGORIES


def get_prohibited_practices() -> list[dict]:
    """Return the full list of prohibited AI practices (Article 5)."""
    return PROHIBITED_PRACTICES