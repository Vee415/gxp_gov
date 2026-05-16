from regulatory.eu_ai_act_rules import classify_risk, get_obligations, get_gap_analysis


def classify_use_case(use_case: str, description: str = "") -> dict:
    result = classify_risk(use_case, description)
    obligations = get_obligations(result["risk_tier"])
    gap_analysis = get_gap_analysis(result["risk_tier"], result["annex"])

    return {
        "system_name": None,
        "use_case": use_case,
        "risk_tier": result["risk_tier"],
        "annex": result["annex"],
        "obligations": obligations,
        "triggered_rules": result["triggered_rules"],
        "gap_analysis": gap_analysis,
    }


def classify_system(system) -> dict:
    result = classify_use_case(system.use_case, system.description)
    result["system_name"] = system.name
    return result