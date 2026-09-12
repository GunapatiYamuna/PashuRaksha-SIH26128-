
"""PashuRaksha explainable surveillance triage + prototype ML risk predictor.

The rule engine is the transparent baseline. The ML layer is a decision-support
prototype that predicts surveillance risk level from report features; it does
not diagnose disease or replace veterinary judgement.
"""
from __future__ import annotations

import random
from typing import Any, Dict, Iterable, List, Optional, Tuple

FAMILIES = {
    "FMD-like": {"fever": 8, "oral lesions": 18, "salivation": 15, "lameness": 12},
    "Respiratory-like": {"cough": 10, "nasal discharge": 10, "breathing difficulty": 18, "fever": 8},
    "Enteric-like": {"diarrhoea": 14, "weakness": 8, "dehydration": 15, "reduced appetite": 5},
    "Skin/Vector-like": {"skin nodules": 18, "fever": 8, "swelling": 7},
}

SYMPTOMS = [
    "fever", "cough", "nasal discharge", "breathing difficulty", "oral lesions",
    "salivation", "lameness", "diarrhoea", "weakness", "dehydration",
    "reduced appetite", "skin nodules", "swelling",
]
SPECIES = ["Cattle", "Buffalo", "Goat", "Sheep", "Poultry", "Pig"]
RISK_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def safe_number(value: Any, default: float = 0.0) -> float:
    try:
        value = float(value)
        return default if value < 0 else value
    except (TypeError, ValueError):
        return default


def normalise_symptoms(symptoms: Any) -> str:
    if isinstance(symptoms, (list, tuple, set)):
        return ", ".join(str(x) for x in symptoms).lower()
    return str(symptoms or "").lower()


def calculate_herd_impact(total: Any, sick: Any) -> Tuple[float, int, Optional[str]]:
    total_n, sick_n = safe_number(total), safe_number(sick)
    ratio = min(1.0, sick_n / total_n) if total_n else 0.0
    if ratio >= 0.40:
        return ratio, 25, "≥40% of herd affected"
    if ratio >= 0.20:
        return ratio, 15, "≥20% of herd affected"
    if sick_n > 0:
        return ratio, 7, "Sick animals reported"
    return ratio, 0, None


def calculate_mortality(deaths: Any) -> Tuple[int, Optional[str]]:
    d = int(safe_number(deaths))
    if d >= 3:
        return 30, "Multiple deaths"
    if d == 2:
        return 22, "Two deaths"
    if d == 1:
        return 12, "One death"
    return 0, None


def detect_symptom_family(symptoms: Any):
    text = normalise_symptoms(symptoms)
    family_scores = {family: sum(weight for symptom, weight in weights.items() if symptom in text)
                     for family, weights in FAMILIES.items()}
    family = max(family_scores, key=family_scores.get) if family_scores else None
    score = family_scores.get(family, 0) if family else 0
    matched = [s for s in SYMPTOMS if s in text]
    if score < 15:
        family = None
    return family, score, matched, family_scores


def calculate_cluster_risk(nearby_reports: Any) -> Tuple[int, Optional[str]]:
    n = int(safe_number(nearby_reports))
    if n >= 2:
        return 10, f"{n} similar recent reports nearby"
    if n == 1:
        return 5, "Similar recent report nearby"
    return 0, None


def calculate_vaccination_risk(vaccination_coverage: Any) -> Tuple[int, Optional[str]]:
    c = safe_number(vaccination_coverage, 80)
    if c < 50:
        return 10, "Low vaccination coverage in area"
    if c < 70:
        return 5, "Vaccination coverage below target"
    return 0, None


def calculate_weather_risk(rain: Any, temp: Any, humidity: Any) -> Tuple[int, List[str]]:
    rain, temp, humidity = safe_number(rain), safe_number(temp), safe_number(humidity, 60)
    score, reasons = 0, []
    if rain >= 20:
        score += 6; reasons.append("High recent rainfall")
    if temp >= 34:
        score += 5; reasons.append("High temperature")
    if humidity >= 85:
        score += 4; reasons.append("High humidity")
    return score, reasons


def get_risk_level(score: Any) -> str:
    score = safe_number(score)
    if score >= 80: return "CRITICAL"
    if score >= 60: return "HIGH"
    if score >= 35: return "MEDIUM"
    return "LOW"


def get_recommended_action(level: str) -> str:
    return {
        "CRITICAL": "Immediate escalation; isolate affected animals; urgent veterinary and laboratory review.",
        "HIGH": "Veterinary escalation within hours; sample collection and movement precautions.",
        "MEDIUM": "Veterinary review within 24 hours; monitor nearby herds.",
        "LOW": "Monitor and provide preventive guidance.",
    }.get(level, "Monitor and provide preventive guidance.")


def triage(species, total, sick, deaths, symptoms, rain, temp, humidity=60, nearby_reports=0, vaccination_coverage=80):
    score, reasons = 0, []
    _, herd_score, herd_reason = calculate_herd_impact(total, sick)
    score += herd_score
    if herd_reason: reasons.append(herd_reason)
    mortality_score, mortality_reason = calculate_mortality(deaths)
    score += mortality_score
    if mortality_reason: reasons.append(mortality_reason)
    family, family_score, _, _ = detect_symptom_family(symptoms)
    if family:
        score += min(25, family_score)
        reasons.append(f"Pattern suggests {family} surveillance risk")
    cluster_score, cluster_reason = calculate_cluster_risk(nearby_reports)
    score += cluster_score
    if cluster_reason: reasons.append(cluster_reason)
    vaccination_score, vaccination_reason = calculate_vaccination_risk(vaccination_coverage)
    score += vaccination_score
    if vaccination_reason: reasons.append(vaccination_reason)
    weather_score, weather_reasons = calculate_weather_risk(rain, temp, humidity)
    score += weather_score; reasons.extend(weather_reasons)
    score = min(100, max(0, int(score)))
    level = get_risk_level(score)
    return score, level, get_recommended_action(level), reasons


def triage_detailed(species, total, sick, deaths, symptoms, rain, temp, humidity=60, nearby_reports=0, vaccination_coverage=80):
    score, level, action, reasons = triage(species, total, sick, deaths, symptoms, rain, temp, humidity, nearby_reports, vaccination_coverage)
    ratio, herd_score, _ = calculate_herd_impact(total, sick)
    mortality_score, _ = calculate_mortality(deaths)
    family, family_score, matched, family_scores = detect_symptom_family(symptoms)
    cluster_score, _ = calculate_cluster_risk(nearby_reports)
    vaccination_score, _ = calculate_vaccination_risk(vaccination_coverage)
    weather_score, _ = calculate_weather_risk(rain, temp, humidity)
    return {
        "engine": "PashuRaksha Explainable Rule Engine", "engine_type": "RULE_BASED",
        "species": species, "total_animals": int(safe_number(total)), "affected_animals": int(safe_number(sick)),
        "deaths": int(safe_number(deaths)), "affected_ratio": round(ratio * 100, 2), "symptom_family": family,
        "matched_symptoms": matched, "family_scores": family_scores, "risk_score": score, "risk_level": level,
        "recommended_action": action, "reasons": reasons,
        "components": {"herd_impact": herd_score, "mortality": mortality_score, "symptom_pattern": min(25, family_score),
                        "nearby_cluster": cluster_score, "vaccination_gap": vaccination_score, "weather": weather_score},
        "governance": {"diagnosis": False, "autonomous_outbreak_declaration": False, "automatic_treatment": False,
                       "veterinary_verification_required": level in ["HIGH", "CRITICAL"]},
    }


def _feature_names() -> List[str]:
    return ["affected_ratio", "deaths", "death_ratio", "rainfall", "temperature", "humidity", "nearby_reports", "vaccination_coverage", "rule_score"] + [f"symptom_{s}" for s in SYMPTOMS] + [f"species_{s}" for s in SPECIES]


def report_features(report: Any, nearby_reports: int = 0, vaccination_coverage: float = 70) -> Dict[str, float]:
    get = (lambda k, d=0: report.get(k, d)) if isinstance(report, dict) else (lambda k, d=0: getattr(report, k, d))
    total = safe_number(get("animal_count", get("total_animals", 0)))
    sick = safe_number(get("sick_count", get("affected_animals", 0)))
    deaths = safe_number(get("deaths", 0))
    symptoms = normalise_symptoms(get("symptoms", ""))
    rainfall = safe_number(get("rainfall", 0)); temperature = safe_number(get("temperature", 30)); humidity = safe_number(get("humidity", 60))
    rule_score, _, _, _ = triage(get("species", ""), total, sick, deaths, symptoms, rainfall, temperature, humidity, nearby_reports, vaccination_coverage)
    f = {"affected_ratio": min(1, sick / total) if total else 0, "deaths": deaths,
         "death_ratio": min(1, deaths / total) if total else 0,
         "rainfall": rainfall, "temperature": temperature, "humidity": humidity,
         "nearby_reports": nearby_reports, "vaccination_coverage": safe_number(vaccination_coverage, 70),
         "rule_score": rule_score}
    for s in SYMPTOMS: f[f"symptom_{s}"] = 1.0 if s in symptoms else 0.0
    species = str(get("species", ""))
    for s in SPECIES: f[f"species_{s}"] = 1.0 if species.lower() == s.lower() else 0.0
    return f


def _generate_training_data(n_per_class: int = 220):
    """Generate balanced prototype surveillance scenarios for the demo model.

    These are synthetic/rule-derived examples, not clinical training data.
    Balanced sampling prevents the model from simply favouring the most common
    risk level in a tiny prototype dataset.
    """
    rows, labels = [], []
    rng = random.Random(26128)
    target_levels = list(RISK_ORDER)
    counts = {level: 0 for level in target_levels}
    attempts = 0
    max_attempts = n_per_class * 300
    while min(counts.values()) < n_per_class and attempts < max_attempts:
        attempts += 1
        total = rng.randint(8, 120)
        sick = rng.randint(0, total)
        deaths = rng.randint(0, min(sick, 5))
        chosen = rng.sample(SYMPTOMS, rng.randint(0, min(5, len(SYMPTOMS))))
        rain = round(rng.uniform(0, 80), 1)
        temp = round(rng.uniform(18, 40), 1)
        humidity = round(rng.uniform(35, 98), 1)
        nearby = rng.randint(0, 5)
        vacc = round(rng.uniform(35, 98), 1)
        species = rng.choice(SPECIES)
        _, level, _, _ = triage(species, total, sick, deaths, chosen, rain, temp, humidity, nearby, vacc)
        if counts[level] >= n_per_class:
            continue
        counts[level] += 1
        rows.append(report_features({"animal_count": total, "sick_count": sick, "deaths": deaths,
                                      "symptoms": chosen, "rainfall": rain, "temperature": temp,
                                      "humidity": humidity, "species": species}, nearby, vacc))
        labels.append(level)

    # Guaranteed examples for any level that is difficult to hit randomly.
    presets = {
        "LOW": {"total": 50, "sick": 2, "deaths": 0, "symptoms": ["weakness"], "rain": 5, "temp": 28, "humidity": 55, "nearby": 0, "vacc": 90},
        "MEDIUM": {"total": 20, "sick": 5, "deaths": 0, "symptoms": ["cough", "nasal discharge"], "rain": 10, "temp": 30, "humidity": 65, "nearby": 0, "vacc": 80},
        "HIGH": {"total": 20, "sick": 8, "deaths": 1, "symptoms": ["fever", "cough", "nasal discharge"], "rain": 25, "temp": 34, "humidity": 85, "nearby": 1, "vacc": 60},
        "CRITICAL": {"total": 20, "sick": 12, "deaths": 3, "symptoms": ["fever", "oral lesions", "salivation"], "rain": 30, "temp": 35, "humidity": 90, "nearby": 2, "vacc": 45},
    }
    for level, preset in presets.items():
        while counts[level] < n_per_class:
            species = rng.choice(SPECIES)
            rows.append(report_features({"animal_count": preset["total"], "sick_count": preset["sick"], "deaths": preset["deaths"],
                                          "symptoms": preset["symptoms"], "rainfall": preset["rain"], "temperature": preset["temp"],
                                          "humidity": preset["humidity"], "species": species}, preset["nearby"], preset["vacc"]))
            labels.append(level)
            counts[level] += 1
    return rows, labels

def train_risk_model(reports_df=None):
    """Train a prototype Random Forest on surveillance scenarios.

    Real reports are added as examples when available. Because the bundled demo
    labels originate from the transparent triage engine, the model is explicitly
    marked prototype/decision-support rather than clinical AI.
    """
    try:
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, balanced_accuracy_score
        from sklearn.model_selection import train_test_split
    except Exception as exc:
        return None, {"available": False, "error": str(exc), "source": "Unavailable"}
    rows, labels = _generate_training_data()
    source = "Prototype synthetic surveillance scenarios"
    if reports_df is not None and len(reports_df) >= 8 and "risk_level" in reports_df.columns:
        real = reports_df.copy()
        for _, r in real.iterrows():
            vacc = 70.0
            rows.append(report_features(r, 0, vacc)); labels.append(str(r.get("risk_level", "LOW")).upper())
        source = "Prototype scenarios + stored PashuRaksha reports"
    X = pd.DataFrame(rows, columns=_feature_names()).fillna(0)
    y = pd.Series(labels)
    model = RandomForestClassifier(n_estimators=240, max_depth=9, min_samples_leaf=2, class_weight="balanced", random_state=26128)
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.22, random_state=26128, stratify=y)
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        accuracy = float(accuracy_score(y_test, pred)); balanced = float(balanced_accuracy_score(y_test, pred))
    except Exception:
        model.fit(X, y); accuracy = None; balanced = None
    return model, {"available": True, "source": source, "model": "Random Forest", "accuracy": accuracy,
                   "balanced_accuracy": balanced, "training_rows": len(X), "classes": list(model.classes_),
                   "note": "Prototype ML trained on synthetic/rule-derived surveillance labels; replace with validated labelled field data before deployment."}


def predict_report_risk(model, report: Any, nearby_reports: int = 0, vaccination_coverage: float = 70):
    if model is None:
        return {"available": False, "predicted_level": None, "confidence": 0.0, "probabilities": {}, "top_factors": []}
    import pandas as pd
    f = report_features(report, nearby_reports, vaccination_coverage)
    X = pd.DataFrame([f], columns=_feature_names()).fillna(0)
    predicted = str(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    probability_map = {str(c): float(p) for c, p in zip(model.classes_, probs)}
    importances = getattr(model, "feature_importances_", [])
    ranked = sorted(zip(_feature_names(), importances, X.iloc[0].tolist()), key=lambda x: x[1] * abs(x[2]), reverse=True)
    labels = {"affected_ratio":"Affected herd ratio", "deaths":"Deaths", "death_ratio":"Mortality ratio", "rainfall":"Rainfall",
              "temperature":"Temperature", "humidity":"Humidity", "nearby_reports":"Nearby reports", "vaccination_coverage":"Vaccination coverage", "rule_score":"Transparent rule score"}
    factors = []
    for name, imp, value in ranked:
        if value != 0 and imp > 0 and len(factors) < 5:
            factors.append({"feature": labels.get(name, name.replace("symptom_", "Symptom: ").replace("species_", "Species: ")), "importance": float(imp), "value": float(value)})
    return {"available": True, "predicted_level": predicted, "confidence": float(max(probs)), "probabilities": probability_map, "top_factors": factors}


def analyze_reports(reports_df, vaccination_map=None):
    """Return ML predictions for every stored report, including nearby-report context."""
    if reports_df is None or len(reports_df) == 0:
        return reports_df, None, {"available": False}
    import pandas as pd
    model, info = train_risk_model(reports_df)
    out = reports_df.copy()
    vaccination_map = vaccination_map or {}
    created = pd.to_datetime(out.get("created_at"), errors="coerce") if "created_at" in out.columns else pd.Series(pd.NaT, index=out.index)
    preds, confs, nearby_values = [], [], []
    for idx, r in out.iterrows():
        nearby = 0
        if "district" in out.columns and "species" in out.columns and pd.notna(created.get(idx, pd.NaT)):
            cutoff = created.get(idx) - pd.Timedelta(days=7)
            same = (out["district"].astype(str).str.lower() == str(r.get("district", "")).lower()) & \
                   (out["species"].astype(str).str.lower() == str(r.get("species", "")).lower()) & \
                   (created >= cutoff) & (created <= created.get(idx))
            nearby = max(0, int(same.sum()) - 1)
        vacc = vaccination_map.get(str(r.get("village", "")), 70)
        p = predict_report_risk(model, r, nearby, vacc)
        preds.append(p.get("predicted_level")); confs.append(p.get("confidence", 0.0)); nearby_values.append(nearby)
    out["ai_predicted_level"] = preds
    out["ai_confidence"] = confs
    out["ai_nearby_reports"] = nearby_values
    return out, model, info

def get_engine_info():
    return {"name": "PashuRaksha Explainable Triage + Prototype ML Risk Predictor", "type": "RULE_BASED + ML",
            "status": "ACTIVE", "version": "2.0", "ml_enabled": True, "purpose": "Animal-health surveillance prioritisation",
            "diagnosis": False, "human_verification": True, "explainable": True}
