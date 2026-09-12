import pandas as pd
import streamlit as st

from database import conn
from auth import record
from utils import require_role, hero, section_title, risk_badge


# ============================================================
# ACCESS
# ============================================================

require_role([
    "District Admin"
])


# ============================================================
# HEADER
# ============================================================

hero(
    "Surveillance Reports",
    "District-level monitoring of animal-health reports and surveillance risk.",
    "📋",
)


# ============================================================
# LOAD REPORTS
# ============================================================

c = conn()

reports = pd.read_sql_query(
    """
    SELECT
        id,
        report_code,
        animal_tag_id,
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
        verified_by
    FROM reports
    ORDER BY id DESC
    LIMIT 1000
    """,
    c,
)

c.close()


# ============================================================
# EMPTY STATE
# ============================================================

if reports.empty:

    st.markdown(
        '<div class="notice">'
        '📭 <b>No surveillance reports available.</b>'
        '<br><br>'
        'Reports submitted through the '
        '<b>Report Case</b> module will appear here.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# STATISTICS
# ============================================================

risk_series = (
    reports["risk_level"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
)

total = len(reports)

critical = int(
    (risk_series == "CRITICAL").sum()
)

high = int(
    (risk_series == "HIGH").sum()
)

medium = int(
    (risk_series == "MEDIUM").sum()
)

low = int(
    (risk_series == "LOW").sum()
)

verified = int(
    reports["verified_by"]
    .fillna("")
    .astype(str)
    .str.strip()
    .ne("")
    .sum()
)


# ============================================================
# KPI CARDS
# ============================================================

a, b, c, d, e = st.columns(5)

with a:

    st.metric(
        "📋 Total Reports",
        total,
    )

with b:

    st.metric(
        "🔴 Critical",
        critical,
    )

with c:

    st.metric(
        "🟠 High",
        high,
    )

with d:

    st.metric(
        "👨‍⚕️ Verified",
        verified,
    )

with e:

    st.metric(
        "🟢 Low",
        low,
    )


# ============================================================
# MONITORING MESSAGE
# ============================================================

st.markdown(
    '<div style="'
    'background:#e8f7ef;'
    'border:1px solid #b8dfcc;'
    'border-radius:16px;'
    'padding:20px;'
    'margin-top:15px;'
    'color:#173f32;'
    '">'
    '<div style="font-weight:800;font-size:1rem;">'
    '🏛️ District Admin monitoring role'
    '</div>'
    '<div style="margin-top:12px;line-height:1.6;">'
    'The District Admin monitors submitted surveillance reports, '
    'identifies high and critical cases, tracks verification status '
    'and monitors district-level disease-risk patterns.'
    '</div>'
    '<div style="margin-top:12px;font-weight:800;">'
    'Admin monitors → Veterinarian verifies → '
    'Laboratory investigates when required'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# FILTERS
# ============================================================

section_title(
    "Filter surveillance reports",
    "Use the filters to monitor reports by district, risk and workflow status.",
    "🔎",
)


f1, f2, f3, f4 = st.columns(4)


# ============================================================
# DISTRICT FILTER
# ============================================================

with f1:

    district_options = ["All"] + sorted(
        reports["district"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_district = st.selectbox(
        "District",
        district_options,
    )


# ============================================================
# RISK FILTER
# ============================================================

with f2:

    risk_options = [
        "All",
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
    ]

    selected_risk = st.selectbox(
        "Risk level",
        risk_options,
    )


# ============================================================
# STATUS FILTER
# ============================================================

with f3:

    status_options = ["All"] + sorted(
        reports["status"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_status = st.selectbox(
        "Status",
        status_options,
    )


# ============================================================
# SEARCH
# ============================================================

with f4:

    search = st.text_input(
        "Search",
        placeholder="Report ID / village / reporter",
    )


# ============================================================
# FILTER DATA
# ============================================================

filtered = reports.copy()


# ------------------------------------------------------------
# DISTRICT
# ------------------------------------------------------------

if selected_district != "All":

    filtered = filtered[
        filtered["district"]
        .fillna("")
        .astype(str)
        .eq(selected_district)
    ]


# ------------------------------------------------------------
# RISK
# ------------------------------------------------------------

if selected_risk != "All":

    filtered = filtered[
        filtered["risk_level"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .eq(selected_risk)
    ]


# ------------------------------------------------------------
# STATUS
# ------------------------------------------------------------

if selected_status != "All":

    filtered = filtered[
        filtered["status"]
        .fillna("")
        .astype(str)
        .eq(selected_status)
    ]


# ------------------------------------------------------------
# SEARCH
# ------------------------------------------------------------

if search.strip():

    q = search.strip().lower()

    report_mask = (
        filtered["report_code"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            q,
            regex=False,
        )
    )

    village_mask = (
        filtered["village"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            q,
            regex=False,
        )
    )

    reporter_mask = (
        filtered["reporter"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            q,
            regex=False,
        )
    )

    animal_mask = (
        filtered["animal_tag_id"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(q, regex=False)
    )

    species_mask = (
        filtered["species"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            q,
            regex=False,
        )
    )

    mask = (
        report_mask
        | village_mask
        | reporter_mask
        | animal_mask
        | species_mask
    )

    filtered = filtered[mask]


# ============================================================
# REPORT TABLE
# ============================================================

section_title(
    "Submitted surveillance reports",
    f"{len(filtered)} report(s) found.",
    "📑",
)


if filtered.empty:

    st.info(
        "No reports match the selected filters."
    )

else:

    display = filtered[
        [
            "report_code",
            "animal_tag_id",
            "reporter",
            "reporter_role",
            "district",
            "village",
            "species",
            "sick_count",
            "deaths",
            "risk_score",
            "risk_level",
            "status",
            "verified_by",
            "created_at",
        ]
    ].copy()

    display.columns = [
        "Report ID",
        "Animal Tag ID",
        "Reporter",
        "Role",
        "District",
        "Village",
        "Species",
        "Affected",
        "Deaths",
        "Risk Score",
        "Risk Level",
        "Status",
        "Verified By",
        "Created At",
    ]

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# REPORT DETAILS
# ============================================================

section_title(
    "Inspect a report",
    "District Admin can inspect the complete surveillance record.",
    "🔍",
)


report_codes = (
    filtered["report_code"]
    .dropna()
    .astype(str)
    .tolist()
)


if report_codes:

    selected_code = st.selectbox(
        "Select report",
        report_codes,
        key="admin_report_selector",
    )


    selected_rows = filtered[
        filtered["report_code"].astype(str)
        == selected_code
    ]


    if not selected_rows.empty:

        row = selected_rows.iloc[0]


        # ====================================================
        # CASE INFORMATION + RISK
        # ====================================================

        left, right = st.columns(2)


        # ====================================================
        # CASE INFORMATION
        # ====================================================

        with left:

            st.markdown(
                '<div class="feature-card">'
                '<div class="icon-bubble">📋</div>'
                '<h3>Case information</h3>'
                '</div>',
                unsafe_allow_html=True,
            )


            st.write(
                f"**Report ID:** {row['report_code']}"
            )

            tag = row.get("animal_tag_id")
            if pd.notna(tag) and str(tag).strip():
                st.success(f"**Animal Tag ID:** {tag}")

                animal_c = conn()
                animal = pd.read_sql_query(
                    "SELECT tag_id, owner, village, species, breed, age_months, sex, health_status FROM animals WHERE tag_id=? LIMIT 1",
                    animal_c, params=(str(tag),)
                )
                animal_c.close()
                if not animal.empty:
                    ar = animal.iloc[0]
                    st.write(f"**Owner:** {ar['owner']} · **Breed:** {ar['breed']} · **Age:** {ar['age_months']} months · **Health:** {ar['health_status']}")
            else:
                st.caption("This is a herd/location report without an individual Animal Tag ID.")

            st.write(
                f"**Reporter:** {row['reporter']}"
            )

            st.write(
                f"**Reporter role:** {row['reporter_role']}"
            )

            st.write(
                f"**District:** {row['district']}"
            )

            st.write(
                f"**Block:** {row['block']}"
            )

            st.write(
                f"**Village:** {row['village']}"
            )

            st.write(
                f"**Species:** {row['species']}"
            )

            st.write(
                f"**Animals in herd/flock:** "
                f"{row['animal_count']}"
            )

            st.write(
                f"**Affected / sick:** "
                f"{row['sick_count']}"
            )

            st.write(
                f"**Deaths:** {row['deaths']}"
            )

            st.write(
                f"**Symptoms:** {row['symptoms']}"
            )

            st.write(
                f"**Symptom onset:** {row['onset_date']}"
            )


        # ====================================================
        # RISK INFORMATION
        # ====================================================

        with right:

            st.markdown(
                '<div class="feature-card">'
                '<div class="icon-bubble">🧠</div>'
                '<h3>Risk assessment</h3>'
                '</div>',
                unsafe_allow_html=True,
            )


            score = row["risk_score"]


            if pd.notna(score):

                try:

                    score_value = float(score)

                    st.metric(
                        "Surveillance Risk Score",
                        f"{score_value:.0f}/100",
                    )

                    st.progress(
                        min(
                            max(
                                score_value / 100,
                                0,
                            ),
                            1,
                        )
                    )

                except (
                    ValueError,
                    TypeError,
                ):

                    st.info(
                        "Risk score is not numeric."
                    )

            else:

                st.info(
                    "Risk score is not available for this report."
                )


            # ------------------------------------------------
            # RISK BADGE
            # ------------------------------------------------

            level = (
                str(row["risk_level"])
                .strip()
                .upper()
            )


            try:

                badge = risk_badge(level)

                st.markdown(
                    badge,
                    unsafe_allow_html=True,
                )

            except Exception:

                st.markdown(
                    f"### Risk level: {level}"
                )


            st.write(
                f"**Recommended action:** "
                f"{row['recommended_action']}"
            )

            st.write(
                f"**Workflow status:** "
                f"{row['status']}"
            )


            # ------------------------------------------------
            # VERIFICATION
            # ------------------------------------------------

            verified_by = row["verified_by"]


            if (
                pd.isna(verified_by)
                or str(verified_by).strip() == ""
            ):

                st.warning(
                    "⏳ Veterinary verification is pending."
                )

            else:

                st.success(
                    f"✅ Verified by: {verified_by}"
                )


        # ====================================================
        # LOCATION / GPS
        # ====================================================

        section_title(
            "Location information",
            "Location captured when the surveillance report was submitted.",
            "📍",
        )


        loc1, loc2, loc3 = st.columns(3)


        with loc1:

            district_value = row["district"]

            st.metric(
                "District",
                str(district_value)
                if pd.notna(district_value)
                else "Not recorded",
            )


        with loc2:

            latitude = row["latitude"]

            st.metric(
                "Latitude",
                str(latitude)
                if pd.notna(latitude)
                else "Not recorded",
            )


        with loc3:

            longitude = row["longitude"]

            st.metric(
                "Longitude",
                str(longitude)
                if pd.notna(longitude)
                else "Not recorded",
            )


        # ====================================================
        # ENVIRONMENT
        # ====================================================

        section_title(
            "Environmental context",
            "Environmental values captured with the original report.",
            "🌦️",
        )


        e1, e2, e3 = st.columns(3)


        with e1:

            rainfall = row["rainfall"]

            st.metric(
                "Rainfall",
                f"{rainfall} mm"
                if pd.notna(rainfall)
                else "Not recorded",
            )


        with e2:

            temperature = row["temperature"]

            st.metric(
                "Temperature",
                f"{temperature} °C"
                if pd.notna(temperature)
                else "Not recorded",
            )


        with e3:

            humidity = row["humidity"]

            st.metric(
                "Humidity",
                f"{humidity}%"
                if pd.notna(humidity)
                else "Not recorded",
            )


        # ====================================================
        # EVIDENCE
        # ====================================================

        section_title(
            "Evidence & notes",
            "Additional information captured with the report.",
            "📷",
        )


        photo_path = row["photo_path"]


        if (
            pd.notna(photo_path)
            and str(photo_path).strip()
        ):

            st.success(
                f"📷 Photo evidence available: "
                f"{photo_path}"
            )

        else:

            st.info(
                "📷 No photo evidence was attached to this report."
            )


        # ====================================================
        # CASE WORKFLOW
        # ====================================================

        section_title(
            "Case workflow",
            "The current position of this report in the response pipeline.",
            "🔄",
        )


        status = (
            str(row["status"])
            .strip()
            .lower()
        )


        # ====================================================
        # WORKFLOW LOGIC
        # ====================================================

        report_done = True


        risk_done = (
            pd.notna(row["risk_score"])
        )


        verification_done = (
            pd.notna(row["verified_by"])
            and
            str(row["verified_by"]).strip() != ""
        )


        lab_done = status in {
            "lab referred",
            "laboratory",
            "sample collected",
            "under laboratory investigation",
            "laboratory investigation",
        }


        response_done = status in {
            "resolved",
            "closed",
            "response completed",
            "response complete",
        }


        steps = [
            (
                "📝",
                "Report submitted",
                report_done,
            ),
            (
                "🧠",
                "Risk assessed",
                risk_done,
            ),
            (
                "👨‍⚕️",
                "Veterinary verification",
                verification_done,
            ),
            (
                "🧪",
                "Laboratory referral",
                lab_done,
            ),
            (
                "🚑",
                "Response",
                response_done,
            ),
        ]


        # ====================================================
        # WORKFLOW CARDS
        # ====================================================

        cols = st.columns(
            5,
            gap="medium",
        )


        for col, (icon, label, done) in zip(
            cols,
            steps,
        ):

            with col:

                if done:

                    background = "#e8f7ef"
                    border = "#9ed8bb"
                    status_color = "#198754"
                    status_text = "✓ Completed"

                else:

                    background = "#ffffff"
                    border = "#d7e3df"
                    status_color = "#777777"
                    status_text = "Pending"


                st.markdown(
                    f'<div style="'
                    f'background:{background};'
                    f'border:1px solid {border};'
                    f'border-radius:16px;'
                    f'padding:20px 12px;'
                    f'text-align:center;'
                    f'min-height:180px;'
                    f'display:flex;'
                    f'flex-direction:column;'
                    f'justify-content:center;'
                    f'align-items:center;'
                    f'box-sizing:border-box;'
                    f'">'
                    f'<div style="'
                    f'font-size:2rem;'
                    f'margin-bottom:12px;'
                    f'">{icon}</div>'
                    f'<div style="'
                    f'font-weight:800;'
                    f'color:#173f32;'
                    f'font-size:0.95rem;'
                    f'line-height:1.3;'
                    f'">{label}</div>'
                    f'<div style="'
                    f'font-size:0.8rem;'
                    f'color:{status_color};'
                    f'font-weight:700;'
                    f'margin-top:12px;'
                    f'">{status_text}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )


        # ====================================================
        # CURRENT WORKFLOW MESSAGE
        # ====================================================

        if response_done:

            st.success(
                "🚑 Response completed. "
                "This surveillance case has reached the response stage."
            )

        elif lab_done:

            st.info(
                "🧪 Laboratory investigation is currently in progress."
            )

        elif verification_done:

            st.info(
                "👨‍⚕️ Veterinary verification is complete."
            )

        elif risk_done:

            st.warning(
                "⏳ Veterinary verification is pending."
            )

        else:

            st.warning(
                "⏳ Risk assessment is pending."
            )


        # ====================================================
        # AUDIT EVENT
        # ====================================================

        try:

            record(
                "VIEW_REPORT",
                "report",
                selected_code,
                {
                    "viewer": st.session_state.user["username"],
                    "risk_level": level,
                },
            )

        except Exception:

            pass


else:

    st.info(
        "No reports are available for inspection "
        "with the current filters."
    )


# ============================================================
# FOOTER MESSAGE
# ============================================================

st.markdown(
    '<div style="'
    'background:#e8f7ef;'
    'border:1px solid #b8dfcc;'
    'border-radius:16px;'
    'padding:22px;'
    'margin-top:20px;'
    'color:#173f32;'
    '">'
    '<div style="'
    'font-size:1rem;'
    'font-weight:800;'
    '">'
    '🛡️ Admin monitoring principle'
    '</div>'
    '<div style="'
    'margin-top:14px;'
    'line-height:1.6;'
    '">'
    'District Admin monitors the surveillance situation '
    'and operational status. Clinical verification remains '
    'the responsibility of the veterinarian.'
    '</div>'
    '<div style="'
    'margin-top:14px;'
    'font-weight:800;'
    '">'
    'Report → AI/Rule Risk → Admin Monitoring → '
    'Veterinary Verification → Laboratory Referral → '
    'Response → Audit'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)
