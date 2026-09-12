import os
import uuid
from datetime import date, datetime

import pandas as pd
import streamlit as st

from auth import record
from database import conn
from triage import triage
from utils import require_role, hero


# ============================================================
# ACCESS
# ============================================================

require_role([
    "District Admin",
    "Veterinarian",
    "Field Worker",
    "Farmer",
])


# ============================================================
# PAGE HEADER
# ============================================================

hero(
    "Report an animal-health event",
    "Capture field evidence, calculate an explainable surveillance risk "
    "and route the case for veterinary verification.",
    "📝",
)

user = st.session_state.get("user", {})
username = str(user.get("username", "unknown"))
user_role = str(user.get("role", "Field Worker"))


# ============================================================
# LOAD REGISTERED ANIMALS
# ============================================================

animals_db = conn()

if user_role == "Farmer":
    registered_animals = pd.read_sql_query(
        """
        SELECT
            tag_id, owner, village, species, breed,
            age_months, sex, health_status
        FROM animals
        WHERE owner = ?
        ORDER BY tag_id
        """,
        animals_db,
        params=(username,),
    )
else:
    registered_animals = pd.read_sql_query(
        """
        SELECT
            tag_id, owner, village, species, breed,
            age_months, sex, health_status
        FROM animals
        ORDER BY tag_id
        """,
        animals_db,
    )

animals_db.close()


# ============================================================
# ANIMAL SELECTION - OUTSIDE FORM
# This makes the selected animal details appear immediately.
# ============================================================

st.info(
    "⚡ Workflow: Register Animal → Select Animal Tag ID → "
    "Animal details load automatically → Report health event → "
    "Risk assessment → Veterinary review"
)

if registered_animals.empty:
    st.warning(
        "No registered animals are available for this account. "
        "Please open Animal Registry and register an animal first."
    )
    st.stop()


st.subheader("🐄 01 · Select registered animal")
st.caption(
    "The Animal Tag ID connects this report to the animal registry and health history."
)

animal_tags = [
    "Select Animal Tag ID"
] + registered_animals["tag_id"].astype(str).tolist()

selected_tag = st.selectbox(
    "Animal Tag ID *",
    animal_tags,
    key="report_animal_tag",
)


if selected_tag == "Select Animal Tag ID":
    default_village = ""
    default_species = "Cattle"
else:
    selected_animal = registered_animals[
        registered_animals["tag_id"].astype(str) == selected_tag
    ].iloc[0]

    default_village = str(selected_animal["village"])
    default_species = str(selected_animal["species"])

    st.success(
        f"✅ Animal **{selected_tag}** selected. "
        "The report will be linked to this animal."
    )

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.metric("Species", str(selected_animal["species"]))

    with d2:
        st.metric("Breed", str(selected_animal["breed"]))

    with d3:
        st.metric("Age", f"{selected_animal['age_months']} months")

    with d4:
        st.metric("Sex", str(selected_animal["sex"]))

    st.info(
        f"👤 **Owner:** {selected_animal['owner']}  |  "
        f"📍 **Village:** {selected_animal['village']}  |  "
        f"❤️ **Health status:** {selected_animal['health_status']}"
    )


# ============================================================
# INTRODUCTION
# ============================================================

st.caption(
    "Veterinary verification remains mandatory for high-risk escalation."
)


# ============================================================
# REPORT FORM
# ============================================================

st.subheader("🧭 Guided field report")
st.write(
    "Capture the important information about the animal-health event. "
    "The system calculates surveillance priority using transparent rules."
)


with st.form("animal_health_report", clear_on_submit=False):

    # --------------------------------------------------------
    # 02 LOCATION
    # --------------------------------------------------------

    st.markdown("## 📍 02 · Location & reporter")
    st.caption("Where did the event occur, and who is submitting it?")

    col1, col2 = st.columns(2)

    with col1:
        reporter = st.text_input(
            "Reporter",
            value=username,
            disabled=True,
        )

    with col2:
        district = st.selectbox(
            "District *",
            [
                "Nashik",
                "Pune",
                "Ahmednagar",
                "Chhatrapati Sambhajinagar",
                "Nagpur",
                "Kolhapur",
            ],
        )

    col1, col2 = st.columns(2)

    with col1:
        block = st.text_input(
            "Block / Taluka *",
            placeholder="Example: Igatpuri",
        )

    with col2:
        village = st.text_input(
            "Village / locality *",
            value=default_village,
            placeholder="Example: Village A",
        )

    col1, col2 = st.columns(2)

    with col1:
        latitude = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=19.0760,
            step=0.000001,
            format="%.6f",
        )

    with col2:
        longitude = st.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=73.8777,
            step=0.000001,
            format="%.6f",
        )

    # --------------------------------------------------------
    # 03 ANIMAL POPULATION & SYMPTOMS
    # --------------------------------------------------------

    st.markdown("---")
    st.markdown("## 🐄 03 · Animal population & symptoms")
    st.caption(
        "The selected Animal Tag ID is already linked above. "
        "These fields describe the health event being reported."
    )

    col1, col2 = st.columns(2)

    with col1:
        species_options = [
            "Cattle", "Buffalo", "Goat", "Sheep", "Poultry", "Pig"
        ]
        species = st.selectbox(
            "Animal species *",
            species_options,
            index=(
                species_options.index(default_species)
                if default_species in species_options
                else 0
            ),
        )

    with col2:
        total_animals = st.number_input(
            "Animals in herd / flock *",
            min_value=1,
            max_value=100000,
            value=1,
            step=1,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        sick_animals = st.number_input(
            "Affected / sick *",
            min_value=0,
            max_value=100000,
            value=1,
            step=1,
        )

    with col2:
        deaths = st.number_input(
            "Deaths",
            min_value=0,
            max_value=100000,
            value=0,
            step=1,
        )

    with col3:
        onset_date = st.date_input(
            "Symptom onset",
            value=date.today(),
        )

    symptoms = st.multiselect(
        "Observed symptoms *",
        [
            "Fever",
            "Cough",
            "Nasal discharge",
            "Breathing difficulty",
            "Oral lesions",
            "Salivation",
            "Lameness",
            "Diarrhoea",
            "Weakness",
            "Dehydration",
            "Reduced appetite",
            "Skin nodules",
            "Swelling",
        ],
        placeholder="Select one or more observed symptoms",
    )

    # --------------------------------------------------------
    # 04 ENVIRONMENT
    # --------------------------------------------------------

    st.markdown("---")
    st.markdown("## 🌦️ 04 · Environmental context")
    st.caption("Environmental values are contextual surveillance signals.")

    col1, col2, col3 = st.columns(3)

    with col1:
        rainfall = st.number_input(
            "Recent rainfall · mm",
            min_value=0.0,
            max_value=500.0,
            value=12.0,
            step=1.0,
        )

    with col2:
        temperature = st.number_input(
            "Temperature · °C",
            min_value=0.0,
            max_value=50.0,
            value=31.0,
            step=0.5,
        )

    with col3:
        humidity = st.number_input(
            "Humidity · %",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=1.0,
        )

    # --------------------------------------------------------
    # 05 EVIDENCE
    # --------------------------------------------------------

    st.markdown("---")
    st.markdown("## 📷 05 · Evidence & field notes")
    st.caption(
        "Add a photograph when it helps veterinary review. "
        "Do not upload unnecessary personal information."
    )

    photo = st.file_uploader(
        "Photo evidence (optional)",
        type=["jpg", "jpeg", "png", "webp"],
    )

    notes = st.text_area(
        "Field notes (optional)",
        placeholder=(
            "Example: 3 animals developed fever within 48 hours; "
            "one death reported this morning."
        ),
        height=120,
    )

    st.markdown("---")

    submit = st.form_submit_button(
        "🚨 Submit report & run risk assessment",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# VALIDATION
# ============================================================

if submit:

    if selected_tag == "Select Animal Tag ID":
        st.error(
            "Please select an Animal Tag ID. Register the animal first if it is not listed."
        )
        st.stop()

    if not block.strip():
        st.error("Please enter the Block / Taluka.")
        st.stop()

    if not village.strip():
        st.error("Please enter the Village / locality.")
        st.stop()

    if sick_animals > total_animals:
        st.error(
            "Affected/sick animals cannot be greater than the total number of animals."
        )
        st.stop()

    if deaths > sick_animals:
        st.error(
            "Deaths cannot be greater than the number of affected/sick animals."
        )
        st.stop()

    if not symptoms:
        st.warning("Please select at least one observed symptom.")
        st.stop()

    # ========================================================
    # GET NEARBY REPORT COUNT
    # ========================================================

    database = conn()

    try:
        nearby_result = database.execute(
            """
            SELECT COUNT(*)
            FROM reports
            WHERE district = ?
              AND species = ?
              AND created_at >= datetime('now', '-7 days')
            """,
            (district, species),
        ).fetchone()

        nearby_reports = int(nearby_result[0] if nearby_result else 0)

    except Exception:
        nearby_reports = 0

    finally:
        database.close()

    # ========================================================
    # DEMO VACCINATION CONTEXT
    # ========================================================

    vaccination_map = {
        "Village A": 94,
        "Village B": 76,
        "Village C": 39,
        "Village D": 88,
    }

    vaccination_coverage = vaccination_map.get(
        village.strip(),
        70,
    )

    # ========================================================
    # RUN TRIAGE
    # ========================================================

    symptoms_text = ", ".join(symptoms)

    score, risk_level, recommended_action, reasons = triage(
        species,
        total_animals,
        sick_animals,
        deaths,
        symptoms_text,
        rainfall,
        temperature,
        humidity,
        nearby_reports=nearby_reports,
        vaccination_coverage=vaccination_coverage,
    )

    # ========================================================
    # GENERATE REPORT CODE
    # ========================================================

    report_code = "PR-" + uuid.uuid4().hex[:7].upper()

    # ========================================================
    # SAVE PHOTO
    # ========================================================

    photo_path = ""

    if photo is not None:
        upload_folder = os.path.join("data", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        safe_filename = "".join(
            character
            if character.isalnum() or character in "._-"
            else "_"
            for character in photo.name
        )

        photo_path = os.path.join(
            upload_folder,
            f"{report_code}_{safe_filename}",
        )

        with open(photo_path, "wb") as file:
            file.write(photo.getbuffer())

    # ========================================================
    # SAVE REPORT
    # IMPORTANT: 24 columns = 24 values = 24 placeholders.
    # ========================================================

    database = conn()

    try:
        database.execute(
            """
            INSERT INTO reports (
                report_code,
                reporter,
                reporter_role,
                village,
                block,
                district,
                species,
                animal_count,
                sick_count,
                deaths,
                symptoms,
                onset_date,
                latitude,
                longitude,
                temperature,
                rainfall,
                humidity,
                risk_score,
                risk_level,
                recommended_action,
                status,
                photo_path,
                created_at,
                animal_tag_id
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
            """,
            (
                report_code,
                reporter,
                user_role,
                village.strip(),
                block.strip(),
                district,
                species,
                int(total_animals),
                int(sick_animals),
                int(deaths),
                symptoms_text,
                str(onset_date),
                float(latitude),
                float(longitude),
                float(temperature),
                float(rainfall),
                float(humidity),
                int(score),
                risk_level,
                recommended_action,
                "Escalated" if risk_level in ["HIGH", "CRITICAL"] else "New",
                photo_path,
                datetime.now().isoformat(),
                selected_tag,
            ),
        )

        database.commit()

    except Exception as error:
        database.rollback()
        st.error(f"Could not save the report: {error}")
        database.close()
        st.stop()

    finally:
        try:
            database.close()
        except Exception:
            pass

    # ========================================================
    # AUDIT LOG
    # ========================================================

    try:
        record(
            "CREATE_REPORT",
            "report",
            report_code,
            {
                "animal_tag_id": selected_tag,
                "risk_level": risk_level,
                "risk_score": score,
                "nearby_reports": nearby_reports,
            },
        )
    except Exception:
        pass

    # ========================================================
    # SHOW TRIAGE RESULT
    # ========================================================

    st.markdown("---")
    st.subheader("🧠 Explainable Risk Assessment")

    if risk_level == "CRITICAL":
        st.error(f"🚨 CRITICAL RISK — Score: {score}/100")
    elif risk_level == "HIGH":
        st.error(f"🚨 HIGH RISK — Score: {score}/100")
    elif risk_level == "MEDIUM":
        st.warning(f"⚠️ MEDIUM RISK — Score: {score}/100")
    else:
        st.success(f"✅ LOW RISK — Score: {score}/100")

    st.progress(min(max(score, 0), 100) / 100)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Risk score", f"{score}/100")

    with col2:
        st.metric("Risk level", risk_level)

    with col3:
        st.metric("Nearby reports", nearby_reports)

    # ========================================================
    # LINKED ANIMAL SUMMARY
    # ========================================================

    st.subheader("🐄 Linked animal")
    st.info(
        f"**Animal Tag ID:** {selected_tag}  |  "
        f"**Species:** {species}  |  "
        f"**Village:** {village.strip()}"
    )

    # ========================================================
    # WHY THIS RISK?
    # ========================================================

    st.subheader("🔎 Why was this risk level generated?")

    if reasons:
        for reason in reasons:
            st.write(f"✓ {reason}")
    else:
        st.write("No major risk factors were detected.")

    # ========================================================
    # RECOMMENDED ACTION
    # ========================================================

    st.subheader("📋 Recommended next step")
    st.info(recommended_action)

    # ========================================================
    # VETERINARY WORKFLOW
    # ========================================================

    if risk_level in ["HIGH", "CRITICAL"]:
        st.error(
            "👨‍⚕️ Veterinary verification is required. The case should be reviewed "
            "by a veterinarian before clinical or containment decisions are made."
        )
    else:
        st.info(
            "👨‍⚕️ The report is available for veterinary review and continued monitoring."
        )

    # ========================================================
    # REPORT DETAILS
    # ========================================================

    st.subheader("📄 Report details")

    details_col1, details_col2 = st.columns(2)

    with details_col1:
        st.write(f"**Report ID:** {report_code}")
        st.write(f"**Animal Tag ID:** {selected_tag}")
        st.write(f"**Reporter:** {reporter}")
        st.write(f"**Role:** {user_role}")
        st.write(f"**District:** {district}")
        st.write(f"**Block:** {block}")
        st.write(f"**Village:** {village}")

    with details_col2:
        st.write(f"**Species:** {species}")
        st.write(f"**Total animals:** {total_animals}")
        st.write(f"**Affected animals:** {sick_animals}")
        st.write(f"**Deaths:** {deaths}")
        st.write(f"**Symptoms:** {symptoms_text}")
        st.write(f"**Vaccination context:** {vaccination_coverage}%")

    if notes.strip():
        st.subheader("📝 Field notes")
        st.write(notes)

    if photo is not None:
        st.subheader("📷 Attached evidence")
        st.image(photo, caption="Field evidence", width=450)

    st.success(f"Report {report_code} was saved successfully.")

    st.caption(
        "Workflow: Report → Risk Assessment → Veterinary Verification → "
        "Laboratory Referral → Response → Audit"
    )
