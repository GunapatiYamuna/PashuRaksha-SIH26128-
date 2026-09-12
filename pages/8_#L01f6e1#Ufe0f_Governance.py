
import json
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from database import conn
from triage import analyze_reports, predict_report_risk, train_risk_model, get_engine_info
from utils import require_role, hero, section_title, risk_badge

require_role(["District Admin", "Veterinarian"])

# ------------------------------------------------------------
# Page styling: keep governance on the same visual system as the
# rest of PashuRaksha. No raw HTML cards are used here; this avoids
# the literal <div> rendering problem seen in the previous version.
# ------------------------------------------------------------
st.markdown("""
<style>
.gov-note{padding:16px 18px;border-radius:16px;border:1px solid #d5e9df;background:linear-gradient(135deg,#f7fcf9,#eef9f3);margin:8px 0 18px}
.gov-note strong{color:#124c39}
.ai-panel{padding:18px;border-radius:18px;border:1px solid #cfe7da;background:linear-gradient(135deg,#f7fffb,#ffffff);box-shadow:0 10px 26px rgba(18,73,51,.06)}
.ai-score{font-size:2.45rem;font-weight:900;color:#117452;line-height:1}
.ai-chip{display:inline-block;padding:6px 10px;border-radius:999px;background:#e9f7ef;border:1px solid #cfe8da;color:#176d4b;font-weight:800;font-size:.78rem;margin:3px}
</style>
""", unsafe_allow_html=True)

hero(
    "Trust, Audit & AI Governance",
    "AI-assisted surveillance risk analysis with transparent rules, report-level predictions, veterinary oversight and a complete audit trail.",
    "🛡️",
)

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
try:
    db = conn()
    logs = pd.read_sql_query("""
        SELECT id, username, role, action, entity_type, entity_id, metadata, created_at
        FROM audit_logs ORDER BY id DESC LIMIT 500
    """, db)
    reports = pd.read_sql_query("""
        SELECT id, report_code, reporter, reporter_role, village, block, district, species,
               animal_count, sick_count, deaths, symptoms, onset_date, latitude, longitude,
               temperature, rainfall, humidity, risk_score, risk_level, recommended_action,
               status, verified_by, created_at
        FROM reports ORDER BY created_at DESC LIMIT 1000
    """, db)
    db.close()
except Exception as exc:
    logs = pd.DataFrame()
    reports = pd.DataFrame()
    st.error(f"Could not load governance data: {exc}")

# ------------------------------------------------------------
# Prototype ML risk analysis
# ------------------------------------------------------------
vaccination_map = {"Village A": 94, "Village B": 76, "Village C": 39, "Village D": 88}
model, model_info = None, {"available": False}
analysis_df = reports.copy()

if not reports.empty:
    analysis_df, model, model_info = analyze_reports(reports, vaccination_map)

# ------------------------------------------------------------
# KPI row
# ------------------------------------------------------------
audit_count = int(len(logs))
verified_count = 0 if reports.empty else int(reports["verified_by"].fillna("").astype(str).str.strip().ne("").sum())
high_count = 0 if reports.empty else int(reports["risk_level"].fillna("").astype(str).str.upper().isin(["HIGH", "CRITICAL"]).sum())
ai_high_count = 0 if analysis_df.empty or "ai_predicted_level" not in analysis_df else int(analysis_df["ai_predicted_level"].isin(["HIGH", "CRITICAL"]).sum())

k1, k2, k3, k4 = st.columns(4)
with k1:
    with st.container(border=True):
        st.metric("📜 Audit Events", audit_count)
with k2:
    with st.container(border=True):
        st.metric("👨‍⚕️ Vet Verified", verified_count)
with k3:
    with st.container(border=True):
        st.metric("🚨 Rule High / Critical", high_count)
with k4:
    with st.container(border=True):
        st.metric("🧠 AI High / Critical", ai_high_count)

st.markdown('<div class="gov-note"><strong>What the AI does:</strong> it reads the structured surveillance reports already stored in PashuRaksha — herd impact, deaths, symptoms, environment, vaccination context and nearby-report signals — and predicts a surveillance risk level. It is <b>not a disease diagnosis</b>.</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# Governance status
# ------------------------------------------------------------
section_title("Governance status", "The controls that keep surveillance intelligence explainable and human-controlled.", "🛡️")
g1, g2, g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown("### 👨‍⚕️ Human verification")
        st.success("REQUIRED")
        st.write("High and critical surveillance signals remain subject to veterinary review. The system cannot approve treatment or declare an outbreak by itself.")
with g2:
    with st.container(border=True):
        st.markdown("### 🧠 Risk intelligence")
        st.success("RULES + ML")
        st.write("The transparent triage engine produces the baseline risk score. A Random Forest prototype provides a second risk-level prediction from the same structured report evidence.")
with g3:
    with st.container(border=True):
        st.markdown("### 🔐 Role-based access")
        st.success("ENABLED")
        st.write("Governance is restricted to District Admin and Veterinarian roles. Operational permissions remain separated across the platform.")

# ------------------------------------------------------------
# AI engine status
# ------------------------------------------------------------
section_title("AI risk engine", "Live analysis of the reports currently stored in the PashuRaksha database.", "🧠")

if not model_info.get("available"):
    st.warning("The ML dependency is unavailable. Install the requirements and restart Streamlit.")
else:
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Model", "Random Forest")
    with a2:
        acc = model_info.get("accuracy")
        st.metric("Validation", f"{acc:.1%}" if isinstance(acc, (float, int)) else "N/A")
    with a3:
        st.metric("Training scenarios", int(model_info.get("training_rows", 0)))
    with a4:
        avg_conf = float(analysis_df["ai_confidence"].mean()) if not analysis_df.empty else 0
        st.metric("Avg AI confidence", f"{avg_conf:.0%}")

    st.info("Prototype note: the bundled model is trained on synthetic surveillance scenarios generated from the transparent triage rules, and stored reports are incorporated when enough examples exist. This demonstrates the AI workflow without pretending that a clinically validated disease dataset exists. Replace the training source with validated, labelled field data before production deployment.")

    if not analysis_df.empty:
        view = analysis_df[["report_code", "district", "village", "species", "risk_score", "risk_level", "ai_predicted_level", "ai_confidence", "status"]].copy()
        view["ai_confidence"] = (view["ai_confidence"] * 100).round(0).astype(int).astype(str) + "%"
        view.columns = ["Report", "District", "Village", "Species", "Rule score", "Rule risk", "AI prediction", "AI confidence", "Status"]
        st.dataframe(view, use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# Individual report AI analysis
# ------------------------------------------------------------
section_title("AI report analysis", "Select a stored report to see the prediction, confidence, agreement with the rule engine and the strongest contributing signals.", "🔎")

if analysis_df.empty:
    st.info("No reports are available yet. Submit a case from Report Case to activate the AI analysis.")
else:
    report_options = analysis_df["report_code"].astype(str).tolist()
    selected_code = st.selectbox("Report to analyze", report_options)
    selected = analysis_df[analysis_df["report_code"].astype(str) == selected_code].iloc[0]
    pred = predict_report_risk(model, selected, int(selected.get("ai_nearby_reports", 0)), vaccination_map.get(str(selected.get("village", "")), 70))

    p1, p2 = st.columns([1, 1.35])
    with p1:
        with st.container(border=True):
            st.markdown("### 🧠 AI prediction")
            st.markdown(f'<div class="ai-score">{pred.get("confidence", 0):.0%}</div>', unsafe_allow_html=True)
            st.caption("Model confidence in the predicted surveillance level")
            level = pred.get("predicted_level") or "UNKNOWN"
            st.markdown(f"**Predicted risk:** {risk_badge(level)}")
            st.markdown(f"**Rule-engine risk:** {risk_badge(str(selected.get('risk_level', 'UNKNOWN')).upper())}")
            agreement = level == str(selected.get("risk_level", "")).upper()
            st.success("AI and rule engine agree" if agreement else "AI and rule engine disagree — veterinary review recommended")
    with p2:
        with st.container(border=True):
            st.markdown("### 📌 Why the model is focusing on this report")
            factors = pred.get("top_factors", [])
            if factors:
                for factor in factors:
                    st.write(f"• **{factor['feature']}** · model importance {factor['importance']:.2f}")
            else:
                st.write("No dominant non-zero factors were identified.")
            probs = pred.get("probabilities", {})
            if probs:
                st.markdown("**Risk-level probabilities**")
                for lvl in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                    if lvl in probs:
                        st.progress(float(probs[lvl]), text=f"{lvl} · {probs[lvl]:.0%}")

    with st.expander("View report evidence used by the risk engine"):
        evidence = {
            "Report": selected.get("report_code"), "Species": selected.get("species"),
            "Animals": selected.get("animal_count"), "Affected": selected.get("sick_count"),
            "Deaths": selected.get("deaths"), "Symptoms": selected.get("symptoms"),
            "Rainfall (mm)": selected.get("rainfall"), "Temperature (°C)": selected.get("temperature"),
            "Humidity (%)": selected.get("humidity"), "Nearby similar reports (7d)": selected.get("ai_nearby_reports", 0), "Vaccination coverage (%)": vaccination_map.get(str(selected.get("village", "")), 70),
            "Rule score": selected.get("risk_score"), "Recommended action": selected.get("recommended_action"),
        }
        st.dataframe(pd.DataFrame(list(evidence.items()), columns=["Signal", "Value"]), use_container_width=True, hide_index=True)

# ------------------------------------------------------------
# AI distribution
# ------------------------------------------------------------
section_title("AI risk distribution", "How the current stored reports are being classified by the prototype model.", "📈")
if not analysis_df.empty:
    dist = analysis_df["ai_predicted_level"].value_counts().reindex(["LOW", "MEDIUM", "HIGH", "CRITICAL"], fill_value=0)
    total = max(int(dist.sum()), 1)
    for level, count in dist.items():
        st.write(f"**{level}** · {int(count)} report(s)")
        st.progress(int(count) / total)
else:
    st.info("AI distribution will appear after reports are submitted.")

# ------------------------------------------------------------
# Audit trail
# ------------------------------------------------------------
section_title("Recent audit trail", "Chronological activity recorded by the PashuRaksha workflow.", "📜")
if logs.empty:
    st.info("No audit events yet.")
else:
    f1, f2, f3 = st.columns(3)
    with f1:
        roles = ["All"] + sorted(logs["role"].dropna().astype(str).unique().tolist())
        selected_role = st.selectbox("Filter by role", roles)
    with f2:
        actions = ["All"] + sorted(logs["action"].dropna().astype(str).unique().tolist())
        selected_action = st.selectbox("Filter by action", actions)
    with f3:
        query = st.text_input("Search audit trail", placeholder="User, action or record...")

    filtered = logs.copy()
    if selected_role != "All": filtered = filtered[filtered["role"].astype(str) == selected_role]
    if selected_action != "All": filtered = filtered[filtered["action"].astype(str) == selected_action]
    if query.strip():
        q = query.strip().lower()
        mask = False
        for col in ["username", "action", "entity_id", "entity_type"]:
            mask = mask | filtered[col].fillna("").astype(str).str.lower().str.contains(q, regex=False)
        filtered = filtered[mask]

    for _, row in filtered.head(30).iterrows():
        with st.container(border=True):
            top1, top2 = st.columns([4, 1])
            with top1:
                st.markdown(f"### 📜 {row.get('action', 'UNKNOWN')}")
                st.caption(f"👤 {row.get('username', 'Unknown')} · {row.get('role', 'Unknown')}")
            with top2:
                st.metric("Event", int(row.get("id", 0)))
            entity = f"{row.get('entity_type', '')} · {row.get('entity_id', '')}".strip(" ·")
            st.write(f"**Record:** {entity or '—'}")
            st.caption(f"🕒 {row.get('created_at', '')}")
            raw = row.get("metadata")
            if raw:
                try:
                    meta = json.loads(str(raw))
                    if isinstance(meta, dict) and meta:
                        st.write(" · ".join(f"{k}: {v}" for k, v in meta.items()))
                except Exception:
                    st.write(str(raw))

# ------------------------------------------------------------
# Responsible AI
# ------------------------------------------------------------
section_title("Responsible AI controls", "The prototype's safety boundary is explicit and reviewable.", "⚖️")
r1, r2, r3 = st.columns(3)
with r1:
    with st.container(border=True):
        st.markdown("### 🎯 Performance monitoring")
        st.write("Track precision, recall, false-positive rate, false-negative rate, calibration, and performance by species and district once validated labels exist.")
with r2:
    with st.container(border=True):
        st.markdown("### 🔎 Explainability")
        st.write("Every report keeps the rule score, reasons, AI prediction and confidence visible so reviewers can understand disagreements.")
with r3:
    with st.container(border=True):
        st.markdown("### 🛡️ Human control")
        st.write("AI does not diagnose, prescribe treatment, declare outbreaks or execute containment. Veterinary professionals remain responsible for clinical decisions.")

st.markdown("---")
st.success("🛡️ PashuRaksha principle: Report → Risk Assessment → AI/Rule Explanation → Veterinary Verification → Laboratory → Response → Audit")
