import uuid
import pandas as pd
import streamlit as st

from database import conn
from auth import record
from utils import require_role, hero, form_header, section_title

require_role(["District Admin", "Veterinarian", "Field Worker", "Farmer"])

user = st.session_state.get("user", {})
role = user.get("role", "")
username = user.get("username", "")

hero(
    "Animal registry",
    "Register animals once, then use their Animal Tag ID to connect reports and health history.",
    "🐄",
)

# ============================================================
# LOAD CURRENT ANIMALS
# ============================================================
c = conn()
if role == "Farmer":
    df = pd.read_sql_query(
        "SELECT * FROM animals WHERE owner=? ORDER BY id DESC",
        c,
        params=(username,),
    )
else:
    df = pd.read_sql_query(
        "SELECT * FROM animals ORDER BY id DESC",
        c,
    )
c.close()

# ============================================================
# KPIs
# ============================================================
a, b, c = st.columns(3)
a.metric("Registered animals", len(df))
b.metric("Under observation", int((df["health_status"] == "Under observation").sum()) if len(df) else 0)
c.metric("Vaccination due", int((df["health_status"] == "Vaccination due").sum()) if len(df) else 0)

# ============================================================
# REGISTRATION FORM - FARMER IS NOW INCLUDED
# ============================================================
section_title(
    "Register an animal",
    "Create the animal identity first. The generated Animal Tag ID is used later in Report Case and Health Records.",
    "➕",
)

with st.form("animal_registration"):
    col1, col2 = st.columns(2)

    with col1:
        if role == "Farmer":
            owner = st.text_input("Owner", value=username, disabled=True)
        else:
            owner = st.text_input(
                "Owner username",
                value=username if role == "Farmer" else "",
                placeholder="Enter farmer username",
            )

        village = st.text_input("Village", placeholder="Example: Village A")
        species = st.selectbox("Species", ["Cattle", "Buffalo", "Goat", "Sheep", "Poultry", "Pig"])
        breed = st.text_input("Breed", placeholder="Example: Gir / Murrah / Osmanabadi")

    with col2:
        age = st.number_input("Age (months)", min_value=1, max_value=240, value=36, step=1)
        sex = st.selectbox("Sex", ["Female", "Male"])
        health = st.selectbox("Initial health status", ["Healthy", "Under observation", "Under treatment", "Vaccination due"])

    st.info("The system generates a unique Animal Tag ID automatically. Save this ID for future reports.")
    ok = st.form_submit_button("🐄 Register animal", type="primary", use_container_width=True)

if ok:
    if not owner.strip():
        st.error("Please enter the owner username.")
        st.stop()
    if not village.strip():
        st.error("Please enter the village.")
        st.stop()
    if not breed.strip():
        st.error("Please enter the breed.")
        st.stop()

    tag = "PR-" + uuid.uuid4().hex[:8].upper()
    c = conn()
    try:
        c.execute(
            "INSERT INTO animals(tag_id,owner,village,species,breed,age_months,sex,health_status,created_at) VALUES(?,?,?,?,?,?,?,?,datetime('now'))",
            (tag, owner.strip(), village.strip(), species, breed.strip(), int(age), sex, health),
        )
        c.commit()
        try:
            record("CREATE_ANIMAL", "animal", tag, {"owner": owner.strip(), "species": species})
        except Exception:
            pass
        st.success(f"✅ Animal registered successfully. Animal Tag ID: {tag}")
        st.code(tag)
        st.info("Next step: open Report Case and select this Animal Tag ID.")
    except Exception as ex:
        c.rollback()
        st.error(f"Could not save animal: {ex}")
    finally:
        c.close()

# ============================================================
# ANIMAL LIST
# ============================================================
section_title(
    "My animals" if role == "Farmer" else "Registered animals",
    "These identities can be selected when creating a surveillance report.",
    "🪪",
)

if df.empty:
    st.info("No animals registered yet. Use the registration form above.")
else:
    display = df.copy()
    display.columns = [
        "ID", "Animal Tag ID", "Owner", "Village", "Species", "Breed",
        "Age (months)", "Sex", "Health Status", "Registered"
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)
