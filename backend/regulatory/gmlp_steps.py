"""
GMLP-Adapted Validation Steps

IQ/OQ/PQ checklist templates derived from GAMP 5 and EMA/CHMP/CVMP/83833/2023.
Step count varies by risk tier — HIGH risk systems get full validation,
LIMITED risk get reduced transparency-focused validation,
MINIMAL risk get documentation-only checklists.

UNACCEPTABLE systems are prohibited and get no validation steps.
"""

GMLP_STEPS: dict[str, dict[str, list[dict]]] = {
    "HIGH": {
        "IQ": [
            {
                "step_key": "installation_verified",
                "step_label": "Installation verified: system deployed correctly, all components present",
                "source": "GAMP 5 Category 4 / Annex 11",
                "sort_order": 1,
            },
            {
                "step_key": "environment_documented",
                "step_label": "Environment documented: infrastructure, configuration, and dependencies recorded",
                "source": "GAMP 5 / 21 CFR Part 11",
                "sort_order": 2,
            },
            {
                "step_key": "access_controls_confirmed",
                "step_label": "Access controls confirmed: role-based access and authentication verified",
                "source": "Annex 11 / 21 CFR Part 11",
                "sort_order": 3,
            },
            {
                "step_key": "data_sources_connected",
                "step_label": "Data sources connected: input pipelines verified, data integrity checks pass",
                "source": "EMA Section 2.3.2 / GAMP 5",
                "sort_order": 4,
            },
        ],
        "OQ": [
            {
                "step_key": "input_range_verified",
                "step_label": "Input range verified: boundary conditions and acceptable input ranges tested",
                "source": "EMA Section 2.3.3 / GAMP 5",
                "sort_order": 1,
            },
            {
                "step_key": "edge_cases_tested",
                "step_label": "Edge cases tested: adversarial and out-of-distribution inputs evaluated",
                "source": "EMA Section 2.3.4 / Article 15",
                "sort_order": 2,
            },
            {
                "step_key": "accuracy_benchmark_met",
                "step_label": "Accuracy benchmark met: URS acceptance criteria satisfied on validation dataset",
                "source": "EMA Section 2.3.5 / Article 15",
                "sort_order": 3,
            },
            {
                "step_key": "bias_assessment_done",
                "step_label": "Bias assessment completed: subgroup performance and fairness metrics documented",
                "source": "Article 10 / EMA Section 2.4.3",
                "sort_order": 4,
            },
            {
                "step_key": "output_interpretation_documented",
                "step_label": "Output interpretation documented: explainability method applied, results recorded",
                "source": "EMA Section 2.4.2 / Article 13",
                "sort_order": 5,
            },
        ],
        "PQ": [
            {
                "step_key": "production_performance_monitored",
                "step_label": "Production performance monitored: KPIs tracked in live environment against baseline",
                "source": "EMA Section 2.5 / GAMP 5",
                "sort_order": 1,
            },
            {
                "step_key": "human_oversight_confirmed",
                "step_label": "Human oversight confirmed: HITL process documented, fall-back strategies defined",
                "source": "Article 14 / EMA Section 2.6",
                "sort_order": 2,
            },
            {
                "step_key": "drift_detection_in_place",
                "step_label": "Drift detection in place: monitoring thresholds and alerting configured",
                "source": "EMA Section 2.5 / Article 15",
                "sort_order": 3,
            },
            {
                "step_key": "revalidation_schedule_set",
                "step_label": "Revalidation schedule set: periodic review date and trigger conditions defined",
                "source": "EMA Section 2.3.3 / GAMP 5",
                "sort_order": 4,
            },
        ],
    },
    "LIMITED": {
        "IQ": [
            {
                "step_key": "installation_verified",
                "step_label": "Installation verified: system deployed and operational",
                "source": "GAMP 5",
                "sort_order": 1,
            },
            {
                "step_key": "access_controls_confirmed",
                "step_label": "Access controls confirmed: user authentication and data access verified",
                "source": "Annex 11",
                "sort_order": 2,
            },
            {
                "step_key": "transparency_disclosures_configured",
                "step_label": "Transparency disclosures configured: AI interaction notices and content marking active",
                "source": "Article 50",
                "sort_order": 3,
            },
        ],
        "OQ": [
            {
                "step_key": "input_range_verified",
                "step_label": "Input range verified: boundary conditions tested",
                "source": "GAMP 5",
                "sort_order": 1,
            },
            {
                "step_key": "output_marking_tested",
                "step_label": "Output marking tested: synthetic content labels visible and machine-readable",
                "source": "Article 50(2)",
                "sort_order": 2,
            },
            {
                "step_key": "transparency_compliance_verified",
                "step_label": "Transparency compliance verified: users informed of AI interaction, content marking active",
                "source": "Article 50(1)(2)(3)",
                "sort_order": 3,
            },
        ],
        "PQ": [
            {
                "step_key": "monitoring_active",
                "step_label": "Monitoring active: system performance tracked in production",
                "source": "GAMP 5",
                "sort_order": 1,
            },
            {
                "step_key": "transparency_ongoing_compliance",
                "step_label": "Ongoing transparency compliance: AI disclosures remain active and accurate",
                "source": "Article 50",
                "sort_order": 2,
            },
            {
                "step_key": "review_schedule_set",
                "step_label": "Review schedule set: periodic review of transparency obligations defined",
                "source": "GAMP 5",
                "sort_order": 3,
            },
        ],
    },
    "MINIMAL": {
        "IQ": [
            {
                "step_key": "installation_documented",
                "step_label": "Installation documented: deployment details and configuration recorded",
                "source": "GAMP 5 / Article 69",
                "sort_order": 1,
            },
            {
                "step_key": "voluntary_code_conduct_acknowledged",
                "step_label": "Voluntary code of conduct acknowledged: organization aware of AI literacy and best practice guidelines",
                "source": "Article 69",
                "sort_order": 2,
            },
        ],
        "OQ": [],
        "PQ": [],
    },
    "UNACCEPTABLE": {
        "IQ": [],
        "OQ": [],
        "PQ": [],
    },
}


def get_gmlp_steps(risk_tier: str) -> dict[str, list[dict]]:
    """Return validation step templates for a risk tier."""
    return GMLP_STEPS.get(risk_tier.upper(), GMLP_STEPS["MINIMAL"])


def get_step_count(risk_tier: str) -> dict[str, int]:
    """Return count of steps per phase for a risk tier."""
    steps = get_gmlp_steps(risk_tier)
    return {phase: len(phase_steps) for phase, phase_steps in steps.items()}