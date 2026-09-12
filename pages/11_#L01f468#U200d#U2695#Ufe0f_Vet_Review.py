import pandas as pd
import streamlit as st

from database import conn
from auth import record
from triage import train_risk_model, predict_report_risk
from utils import require_role, hero, section_title, risk_badge


# ============================================================
# ACCESS
# ============================================================

require_role(["Veterinarian"])

hero(
    "Veterinary case review",
    "Review surveillance signals, inspect the linked animal and record the human veterinary decision.",
    "👨‍⚕️",
)

username = str(st.session_state.user.get("username", "unknown"))


# ============================================================
# LOAD REPORTS
# ============================================================

c = conn()
reports = pd.read_sql_query(
    "SELECT * FROM reports ORDER BY id DESC",
    c,
)
c.close()

if reports.empty:
    st.info("No reports are available for veterinary review yet.")
    st.stop()


# ============================================================
# MODEL
# ============================================================

model, model_info = train_risk_model(reports)


# ============================================================
# PRIORITY QUEUE
# ============================================================

section_title(
    "Priority review queue",
    "High and critical cases should be reviewed first. AI is advisory; verification is human-controlled.",
    "🚨",
)

priority = reports[
    reports["risk_level"].astype(str).str.upper().isin(["HIGH", "CRITICAL"])
].copy()

if priority.empty:
    st.success("No high/critical reports are waiting in the current dataset.")
else:
    cols = [
        "report_code",
        "animal_tag_id",
        "district",
        "block",
        "village",
        "species",
        "sick_count",
        "deaths",
        "risk_score",
        "risk_level",
        "status",
        "verified_by",
    ]
    cols = [col for col in cols if col in priority.columns]
    st.dataframe(
        priority[cols],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# SELECT CASE
# ============================================================

section_title(
    "Review a case",
    "Select a report to inspect its linked animal, health history and surveillance evidence.",
    "🔎",
)

code = st.selectbox(
    "Report",
    reports["report_code"].astype(str).tolist(),
)

selected = reports[
    reports["report_code"].astype(str) == code
].iloc[0]


# ============================================================
# NEARBY CONTEXT
# ============================================================

created = pd.to_datetime(
    reports["created_at"],
    errors="coerce",
)
selected_time = pd.to_datetime(
    selected["created_at"],
    errors="coerce",
)

nearby = 0

if pd.notna(selected_time):
    mask = (
        reports["district"].astype(str).str.lower()
        == str(selected["district"]).lower()
    ) & (
        reports["species"].astype(str).str.lower()
        == str(selected["species"]).lower()
    ) & (
        created >= selected_time - pd.Timedelta(days=7)
    ) & (
        created <= selected_time
    )

    nearby = max(0, int(mask.sum()) - 1)

vacc = {
    "Village A": 94,
    "Village B": 76,
    "Village C": 39,
    "Village D": 88,
}.get(
    str(selected.get("village", "")),
    70,
)

pred = predict_report_risk(
    model,
    selected,
    nearby,
    vacc,
)


# ============================================================
# DECISION SUPPORT + ANIMAL DETAILS
# ============================================================

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("### 🧠 Decision-support summary")

        st.markdown(
            f"**Rule risk:** "
            f"{risk_badge(str(selected.get('risk_level', 'UNKNOWN')).upper())}"
        )

        st.markdown(
            f"**AI prediction:** "
            f"{risk_badge(pred.get('predicted_level') or 'UNKNOWN')}"
        )

        st.metric(
            "AI confidence",
            f"{pred.get('confidence', 0):.0%}",
        )

        st.caption(
            "AI predicts surveillance priority only; it does not diagnose disease."
        )

        if pred.get("predicted_level") == str(
            selected.get("risk_level", "")
        ).upper():
            st.success("AI and rule engine agree.")
        else:
            st.warning("AI and rule engine disagree. Review evidence carefully.")

with right:
    with st.container(border=True):
        st.markdown("### 🐄 Linked animal details")

        tag = selected.get("animal_tag_id")

        if pd.notna(tag) and str(tag).strip():
            tag = str(tag).strip()

            st.success(f"**Animal Tag ID:** {tag}")

            ac = conn()

            animal = pd.read_sql_query(
                """
                SELECT
                    tag_id,
                    owner,
                    village,
                    species,
                    breed,
                    age_months,
                    sex,
                    health_status
                FROM animals
                WHERE tag_id = ?
                LIMIT 1
                """,
                ac,
                params=(tag,),
            )

            history = pd.read_sql_query(
                """
                SELECT
                    record_type,
                    title,
                    details,
                    record_date,
                    provider
                FROM health_records
                WHERE tag_id = ?
                ORDER BY record_date DESC
                """,
                ac,
                params=(tag,),
            )

            ac.close()

            if not animal.empty:
                ar = animal.iloc[0]

                st.write(f"**Owner:** {ar['owner']}")
                st.write(f"**Village:** {ar['village']}")
                st.write(f"**Species:** {ar['species']}")
                st.write(f"**Breed:** {ar['breed']}")
                st.write(f"**Age:** {ar['age_months']} months")
                st.write(f"**Sex:** {ar['sex']}")
                st.write(f"**Current health status:** {ar['health_status']}")

            if not history.empty:
                with st.expander("💉 View previous health records", expanded=True):
                    st.dataframe(
                        history,
                        use_container_width=True,
                        hide_index=True,
                    )
        else:
            st.warning("This report has no Animal Tag ID linked to it.")


# ============================================================
# CASE EVIDENCE
# ============================================================

with st.container(border=True):
    st.markdown("### 📋 Case evidence")
    st.write(
        f"**Location:** {selected.get('village')} · "
        f"{selected.get('block')} · {selected.get('district')}"
    )
    st.write(
        f"**Animals:** {selected.get('animal_count')} · "
        f"**Affected:** {selected.get('sick_count')} · "
        f"**Deaths:** {selected.get('deaths')}"
    )
    st.write(f"**Symptoms:** {selected.get('symptoms')}")
    st.write(
        f"**Environment:** {selected.get('rainfall')} mm rain · "
        f"{selected.get('temperature')} °C · "
        f"{selected.get('humidity')}% humidity"
    )
    st.write(f"**Nearby similar reports:** {nearby} · **Vaccination:** {vacc}%")
    st.write(f"**Current workflow status:** {selected.get('status')}")


# ============================================================
# AI EXPLANATION
# ============================================================

factors = pred.get("top_factors", [])

if factors:
    section_title(
        "AI explanation",
        "The model's strongest non-zero signals for this case.",
        "💡",
    )

    for factor in factors:
        st.write(
            f"• **{factor['feature']}** · "
            f"model importance {factor['importance']:.2f}"
        )


# ============================================================
# VETERINARY VERIFICATION
# ============================================================

section_title(
    "Veterinary verification",
    "Record the veterinary review outcome and notes. The result is saved to the report and the animal health timeline.",
    "✅",
)

current_status = str(selected.get("status", "New"))
current_verified_by = selected.get("verified_by")

if (
    pd.notna(current_verified_by)
    and str(current_verified_by).strip()
):
    st.success(
        f"Previously verified by: {current_verified_by} · Status: {current_status}"
    )

with st.form("vet_verify"):

    outcome = st.selectbox(
        "Verification outcome",
        [
            "Verified - monitor",
            "Verified - escalate",
            "Needs more evidence",
            "Not verified",
        ],
    )

    notes = st.text_area(
        "Veterinarian notes",
        placeholder=(
            "Clinical observations, recommended follow-up, "
            "sample decision, treatment observations, etc."
        ),
        height=140,
    )

    ok = st.form_submit_button(
        "👨‍⚕️ Save veterinary review",
        type="primary",
        use_container_width=True,
    )


if ok:

    if not notes.strip():
        st.warning("Please enter veterinarian notes before saving the review.")
        st.stop()

    if outcome == "Verified - monitor":
        new_status = "Verified"
        new_verified_by = username

    elif outcome == "Verified - escalate":
        new_status = "Escalated"
        new_verified_by = username

    elif outcome == "Needs more evidence":
        new_status = "Under review"
        new_verified_by = None

    else:
        new_status = "Not verified"
        new_verified_by = None

    c = conn()

    try:
        # Save the actual veterinary review on the report.
        c.execute(
            """
            UPDATE reports
            SET
                status = ?,
                verified_by = ?,
                review_outcome = ?,
                review_notes = ?,
                reviewed_by = ?,
                reviewed_at = datetime('now')
            WHERE report_code = ?
            """,
            (
                new_status,
                new_verified_by,
                outcome,
                notes.strip(),
                username,
                code,
            ),
        )

        # Also add the review to the linked animal's longitudinal health history.
        tag = selected.get("animal_tag_id")

        if pd.notna(tag) and str(tag).strip():
            c.execute(
                """
                INSERT INTO health_records(
                    tag_id,
                    record_type,
                    title,
                    details,
                    record_date,
                    provider
                )
                VALUES(?,?,?,?,datetime('now'),?)
                """,
                (
                    str(tag).strip(),
                    "Vet Review",
                    outcome,
                    f"Report {code}: {notes.strip()}",
                    username,
                ),
            )

        c.commit()

    except Exception as error:
        c.rollback()
        st.error(f"Could not save veterinary review: {error}")
        c.close()
        st.stop()

    finally:
        try:
            c.close()
        except Exception:
            pass

    try:
        record(
            "VERIFY_REPORT",
            "report",
            code,
            {
                "outcome": outcome,
                "status": new_status,
                "reviewed_by": username,
                "notes": notes[:300],
            },
        )
    except Exception:
        pass

    st.success(
        f"✅ {code} veterinary review saved successfully. "
        f"Status: {new_status}."
    )

    st.rerun()
