"""
Behavioral Assessment Scenarios

These are not automated features — they are questions and scenarios that
users should consider when registering and classifying AI systems.

Vendors often describe their systems conservatively on paper ("clinical
decision support tool") while the system actually performs higher-risk
functions (generating treatment plans, triggering automated actions).

These scenarios help users identify discrepancies between what a vendor
says and what the system actually does — the gap where hidden risk lives.
"""

BEHAVIORAL_SCENARIOS: list[dict] = [
    {
        "id": "hidden-decision-making",
        "title": "Hidden Decision-Making",
        "scenario": "Vendor calls it 'decision support' but the system generates orders that enter the EHR as pending actions. A doctor clicks 'approve' without reading because there are 200 AI outputs per shift.",
        "questions": [
            "Where does the system's output go after it's generated?",
            "Does the output enter the EHR as a pending order or action?",
            "How many AI outputs does a reviewer process per shift?",
            "How much time does a reviewer spend on each output?",
        ],
        "risk_indicator": "If output enters EHR as pending order + reviewer processes >50/shift = human oversight theatre, not real oversight",
        "likely_misclassification": "Vendor says LIMITED (decision support). Actually HIGH (clinical decision-making).",
    },
    {
        "id": "autonomous-actions",
        "title": "Autonomous Actions Hidden in Workflows",
        "scenario": "System is called 'workflow optimization' but it decides which pharmacist reviews which prescription, or which nurse is assigned to which patient. The routing decisions affect patient care but are buried in workflow logic.",
        "questions": [
            "Does the system make routing, assignment, or prioritization decisions?",
            "Can the system trigger actions without human initiation?",
            "What happens if nobody reviews the output for 24 hours?",
            "Can you turn the AI off and still perform the same workflow?",
        ],
        "risk_indicator": "If system triggers actions automatically or workflow breaks without it = embedded in clinical pathway = HIGH risk",
        "likely_misclassification": "Vendor says MINIMAL (workflow tool). Actually HIGH (clinical pathway control).",
    },
    {
        "id": "llm-treatment-plans",
        "title": "LLM Generating Treatment Plans",
        "scenario": "System is marketed as 'documentation assistant' but uses an LLM to generate treatment plan text that doctors sign off on with minimal editing. The treatment plan influences actual clinical decisions.",
        "questions": [
            "Does the system use an LLM or foundation model?",
            "Does the system generate clinical text (treatment plans, diagnoses, prescriptions)?",
            "Does a doctor review the generated text before it becomes part of the patient record?",
            "Can the system generate content that is factually wrong but looks plausible?",
        ],
        "risk_indicator": "LLM generating clinical content + doctor signs off without thorough review = EMA explicitly warns about 'plausible but erroneous output' in reflection paper Section 2.3.5",
        "likely_misclassification": "Vendor says LIMITED (documentation assistant). Actually HIGH (clinical decision-making).",
    },
    {
        "id": "patient-exclusion",
        "title": "AI-Driven Patient Exclusion",
        "scenario": "System is called 'analytics platform' but it flags which patients to exclude from clinical trials based on AI risk predictions. The exclusion directly affects which patients get access to experimental treatments.",
        "questions": [
            "Does the system recommend including or excluding patients from trials?",
            "Does the system score or rank patients by likelihood of success?",
            "Are the system's recommendations used to determine trial eligibility?",
            "Is there a process for patients to appeal AI-driven exclusion decisions?",
        ],
        "risk_indicator": "AI determining who gets access to treatment = Annex III Category 5 (access to essential services) = HIGH risk",
        "likely_misclassification": "Vendor says MINIMAL (analytics). Actually HIGH (patient access to essential services).",
    },
    {
        "id": "continuous-learning-hidden",
        "title": "Continuous Learning Disguised as Updates",
        "scenario": "Vendor says the model is 'frozen' but releases frequent 'software updates' that include model retraining on new data. Each update changes the model's behavior without triggering revalidation.",
        "questions": [
            "Is the model frozen in deployment, or does it learn from new data?",
            "How often does the vendor release 'updates' or 'patches'?",
            "Do updates include changes to the model weights, or only to the surrounding software?",
            "Is each model change treated as a new version requiring revalidation?",
        ],
        "risk_indicator": "Continuous learning in production without revalidation = EMA explicitly prohibits this for pivotal trials (Section 2.3.3). Each model change should trigger IQ/OQ/PQ re-qualification.",
        "likely_misclassification": "Vendor says validated (frozen model). Actually REQUIRES REVALIDATION (model changed).",
    },
    {
        "id": "black-box-explainability",
        "title": "Black Box with No Explainability",
        "scenario": "Vendor says the system is 'explainable' but can only show confidence scores, not why a specific recommendation was made. When asked 'why did you recommend drug X for this patient?' the system cannot produce an answer.",
        "questions": [
            "Can the system explain why it made a specific recommendation for a specific patient?",
            "Does the system produce SHAP values, LIME explanations, or attention maps?",
            "When a doctor disagrees with the AI, can the system show what factors drove the recommendation?",
            "Is the model a deep neural network with no interpretable intermediate outputs?",
        ],
        "risk_indicator": "No explainability for individual decisions = EMA requires XAI for high-risk (Section 2.4.2). Annex 22 draft: system must be Predictable, Auditable, and Explainable. Black box fails all three.",
        "likely_misclassification": "Vendor says 'transparent' (shows confidence scores). Actually non-explainable (cannot show reasoning).",
    },
    {
        "id": "oversight-theatre",
        "title": "Human Oversight Theatre",
        "scenario": "System requires 'doctor approval' but the approval step is a single click with no requirement to review. The doctor processes 200 AI outputs per shift with 30 seconds each. No override documentation is collected.",
        "questions": [
            "What does the reviewer actually do when approving — read the full output or click approve?",
            "How many seconds does a reviewer spend on each AI output?",
            "Is override documentation collected when a reviewer disagrees?",
            "Is there a process for escalating uncertain AI outputs?",
        ],
        "risk_indicator": "Article 14 requires 'effective oversight' — meaning ability to understand, monitor anomalies, override output, and interrupt operation. Rubber-stamp approval is not effective oversight.",
        "likely_misclassification": "Vendor says 'human-in-the-loop'. Actually autonomous with ceremonial approval step.",
    },
    {
        "id": "cross-border-data",
        "title": "Cross-Border Data and Model Training",
        "scenario": "AI system trained on patient data from one country, deployed in another. Training data demographics don't match deployment population. No bias assessment across populations.",
        "questions": [
            "Where was the training data collected (country, hospital, population)?",
            "Does the deployment population match the training population demographically?",
            "Has the system been validated on data from the deployment region?",
            "Are there known performance differences across ethnic or demographic groups?",
        ],
        "risk_indicator": "Training-deployment population mismatch = bias risk. EMA requires subgroup analysis (Section 2.4.3). EU AI Act Article 10 requires examination for biases affecting health or fundamental rights.",
        "likely_misclassification": "Vendor says 'validated' (on original population). Actually REQUIRES LOCAL VALIDATION for deployment population.",
    },
]


def get_behavioral_scenarios() -> list[dict]:
    """Return all behavioral assessment scenarios."""
    return BEHAVIORAL_SCENARIOS


def get_scenarios_for_risk_tier(risk_tier: str) -> list[dict]:
    """Return scenarios most relevant to a given risk tier."""
    tier_map = {
        "HIGH": ["hidden-decision-making", "autonomous-actions", "llm-treatment-plans",
                 "patient-exclusion", "continuous-learning-hidden", "black-box-explainability",
                 "oversight-theatre", "cross-border-data"],
        "LIMITED": ["llm-treatment-plans", "oversight-theatre"],
        "MINIMAL": ["continuous-learning-hidden", "cross-border-data"],
        "UNACCEPTABLE": [],
    }
    relevant_ids = tier_map.get(risk_tier, [])
    return [s for s in BEHAVIORAL_SCENARIOS if s["id"] in relevant_ids]