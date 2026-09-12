import pandas as pd
import streamlit as st
from datetime import datetime
from database import conn
from auth import record
from utils import require_role, hero, form_header, section_title

ROLE = st.session_state.user["role"]
require_role(["District Admin", "Veterinarian", "Field Worker", "Farmer"])

hero(
    "Alerts & multilingual advisories",
    "Farmers receive practical guidance, field teams see operational alerts, and authorised staff can publish targeted advisories.",
    "📢",
)

# Everyone can read; only Admin/Veterinarian can publish.
if ROLE in ["District Admin", "Veterinarian"]:
    templates = {
        "English": "Disease risk has increased in your area. Isolate visibly sick animals where appropriate and contact your veterinarian.",
        "Marathi": "तुमच्या परिसरात जनावरांच्या आजाराचा धोका वाढला आहे. आजारी जनावरांना योग्य ती काळजी देऊन पशुवैद्यकांशी संपर्क साधा.",
        "Hindi": "आपके क्षेत्र में पशु रोग का जोखिम बढ़ा है। बीमार पशुओं को उचित रूप से अलग रखें और पशु चिकित्सक से संपर्क करें.",
    }
    form_header("Communication centre", "Publish a targeted advisory", "Choose language, audience and severity so the right people receive the right action.", "📢")
    with st.form("ad"):
        a, b = st.columns(2)
        title = a.text_input("Alert title", "Animal health risk advisory")
        language = b.selectbox("Language", ["English", "Marathi", "Hindi"])
        c, d = st.columns(2)
        audience = c.selectbox("Audience", ["Farmers", "Field Workers", "Veterinarians", "Officials", "All"])
        severity = d.selectbox("Severity", ["Info", "Advisory", "Warning", "Emergency"])
        msg = st.text_area("Message", templates[language], height=120)
        ok = st.form_submit_button("📢 Publish advisory", type="primary", use_container_width=True)
    if ok:
        c = conn()
        c.execute("INSERT INTO advisories(title,language,audience,severity,message,issued_by,issued_at,status) VALUES(?,?,?,?,?,?,?,?)", (title, language, audience, severity, msg, st.session_state.user["username"], datetime.now().isoformat(), "Published"))
        c.commit(); c.close()
        record("PUBLISH_ADVISORY", "advisory", title, {"audience": audience, "severity": severity})
        st.success("Advisory published and added to the audit trail.")
else:
    st.markdown('<div class="notice">👀 <b>Read-only view:</b> your role can receive advisories but cannot publish them.</div>', unsafe_allow_html=True)

section_title("Published advisories", "Operational messages available to the current role.", "📚")
c = conn(); df = pd.read_sql_query("SELECT * FROM advisories ORDER BY id DESC", c); c.close()

if df.empty:
    st.markdown('<div class="notice">No advisories published yet.</div>', unsafe_allow_html=True)
else:
    for _, r in df.head(20).iterrows():
        audience = str(r.get("audience", "All"))
        visible = audience in ["All", "Officials" if ROLE == "District Admin" else "__none__", "Veterinarians" if ROLE == "Veterinarian" else "__none__", "Field Workers" if ROLE == "Field Worker" else "__none__", "Farmers" if ROLE == "Farmer" else "__none__"]
        if not visible and ROLE in ["Farmer", "Field Worker", "Veterinarian"]:
            continue
        st.markdown(f'''<div class="status-card" style="margin:10px 0"><div style="display:flex;justify-content:space-between;gap:12px"><div><b>{r.get("title", "Advisory")}</b></div><span class="pill">{r.get("language", "English")} · {audience} · {r.get("severity", "Info")}</span></div><p style="margin:.7rem 0">{r.get("message", "")}</p><div class="small-label">Issued by {r.get("issued_by", "system")} · {r.get("issued_at", "")}</div></div>''', unsafe_allow_html=True)
