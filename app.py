import streamlit as st
from pathlib import Path
import runpy
from database import init_db, seed_demo_data
from utils import inject_css, nav

st.set_page_config(page_title="PashuRaksha | Home", page_icon="🐾", layout="wide", initial_sidebar_state="collapsed")
init_db(); seed_demo_data(); inject_css()

if "user" not in st.session_state: st.session_state.user=None
if "page" not in st.session_state: st.session_state.page="home"

if not st.session_state.user:
    st.markdown('<div style="height:5vh"></div>', unsafe_allow_html=True)
    a,b,c=st.columns([1,1.15,1])
    with b:
        st.markdown('''<div class="home-hero" style="text-align:center;padding:32px 28px"><div style="font-size:3rem">🐾</div><h1 style="font-size:2.35rem!important">PashuRaksha</h1><p style="margin:auto!important">Animal Health Intelligence & Response Platform</p></div>''',unsafe_allow_html=True)
        with st.form("login"):
            st.markdown('<div class="section-kicker">🔐 Secure demo access</div><div class="form-title">Welcome back</div>',unsafe_allow_html=True)
            u=st.text_input("Username", "admin")
            p=st.text_input("Password", "admin123", type="password")
            if st.form_submit_button("Enter PashuRaksha →",type="primary",use_container_width=True):
                users={"admin":("admin123","District Admin"),"vet":("vet123","Veterinarian"),"field":("field123","Field Worker"),"farmer":("farmer123","Farmer")}
                if u in users and p==users[u][0]: st.session_state.user={"username":u,"role":users[u][1]}; st.session_state.page="home"; st.rerun()
                st.error("Invalid demo credentials.")
        st.markdown('<div class="notice" style="margin-top:12px;text-align:center">Demo users: <b>admin</b> · <b>vet</b> · <b>field</b> · <b>farmer</b></div>',unsafe_allow_html=True)
    st.stop()

nav()
page=st.session_state.page

if page=="home":
    role = st.session_state.user["role"]
    role_copy = {
        "Farmer": ("Your animals. Your first alert.", "Report symptoms quickly, keep health history in one place, and receive local advisories."),
        "Field Worker": ("Capture field signals without slowing down.", "Record cases, samples and offline events in the field, then synchronise when connectivity returns."),
        "Veterinarian": ("Turn reports into verified action.", "Review risk signals, verify cases, refer samples, publish advisories and maintain clinical oversight."),
        "District Admin": ("See the district before the outbreak sees you.", "Monitor emerging risk, vaccination gaps, response workflows, governance and operational accountability."),
    }
    title, subtitle = role_copy[role]
    st.markdown(f'''<div class="home-hero"><span class="hero-badge">🐾 {role} workspace</span><h1>{title}</h1><p>{subtitle}</p></div>''', unsafe_allow_html=True)
    a, b = st.columns([1.2, 1])
    with a:
        st.image("assets/hero-livestock.svg", use_container_width=True)
    with b:
        st.markdown('<div class="section-kicker">YOUR WORKSPACE</div><h2 style="margin:.1rem 0 .7rem;color:#123c2d!important">What you can do</h2>', unsafe_allow_html=True)
        role_cards = {
            "Farmer": [("📝", "Report", "Submit a sick/dead animal report."), ("🐄", "My animals", "Keep animal identity and health history."), ("🔔", "Alerts", "Read local health advisories."), ("📱", "Offline", "Queue reports when connectivity is poor.")],
            "Field Worker": [("📝", "Field reports", "Capture symptoms, deaths and location."), ("🧪", "Samples", "Create laboratory collection records."), ("🐄", "Animal records", "Update field animal information."), ("📱", "Offline sync", "Store events and synchronise later.")],
            "Veterinarian": [("🧠", "Risk review", "Compare rule and AI surveillance signals."), ("👨‍⚕️", "Vet review", "Verify cases and record clinical review."), ("🧪", "Laboratory", "Refer samples and track results."), ("📢", "Advisories", "Publish targeted guidance.")],
            "District Admin": [("📊", "Command centre", "Monitor district risk and trends."), ("🗺️", "Risk map", "See geographic concentration of reports."), ("🛡️", "Governance", "Audit AI and operational actions."), ("📤", "Exports", "Download authorised datasets.")],
        }
        for icon, heading, desc in role_cards[role]:
            st.markdown(f'''<div class="feature-card" style="margin-bottom:10px;min-height:0;padding:16px!important"><div style="display:flex;gap:12px;align-items:center"><div class="icon-bubble">{icon}</div><div><h3 style="margin:0!important">{heading}</h3><p style="margin:2px 0 0">{desc}</p></div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div style="margin-top:22px"><div class="section-kicker">END-TO-END RESPONSE</div><h2 style="margin:.2rem 0">One workflow, with different responsibilities.</h2></div>', unsafe_allow_html=True)
    cols = st.columns(7)
    for col, label in zip(cols, ["📝 Report", "🧠 Risk", "👨‍⚕️ Verify", "🧪 Lab", "📢 Alert", "💉 Treat", "🚧 Contain"]):
        with col: st.markdown(f'''<div class="flow">{label}</div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-card" style="margin-top:22px!important"><div class="section-kicker">PLATFORM SAFETY</div><div style="display:flex;flex-wrap:wrap;gap:9px;margin-top:9px"><span class="pill">🤖 AI decision support</span><span class="pill">👨‍⚕️ Human verification</span><span class="pill">🔐 Role-based access</span><span class="pill">📱 Offline-first</span><span class="pill">🇮🇳 English · Marathi · Hindi</span><span class="pill">📜 Audit trail</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="warning-box" style="margin-top:12px">⚠️ <b>Safety boundary:</b> PashuRaksha predicts surveillance priority; it does not diagnose disease, prescribe treatment or autonomously declare an outbreak.</div>', unsafe_allow_html=True)

else:
    from auth import role_allowed
    if not role_allowed({
    "report": "Report Case",
    "reports": "Reports",
    "dashboard": "Dashboard",
    "animals": "Animal Registry",
    "health": "Health Records",
    "vetreview": "Vet Review",
    "lab": "Lab Referral",
    "alerts": "Alerts",
    "integrations": "Integrations",
    "governance": "Governance",
    "offline": "Offline Sync",
    "exports": "Exports",
}.get(page, "Home")):
        st.error("This workspace is not available for your role.")
        st.stop()
    mapping = {
    # IMPORTANT: use the actual filenames stored in pages/.
    # The ZIP was created with encoded Unicode filenames, so do not use
    # emoji filenames here.
    "report": "1_#L01f4dd_Report_Case.py",
    "reports": "reports.py",
    "dashboard": "2_#L01f4ca_Dashboard.py",
    "animals": "3_#L01f404_Animal_Registry.py",
    "health": "4_#L01f489_Health_Records.py",
    "vetreview": "11_#L01f468#U200d#U2695#Ufe0f_Vet_Review.py",
    "lab": "5_#L01f9ea_Lab_Referral.py",
    "alerts": "6_#L01f514_Alerts.py",
    "integrations": "7_#U2699#Ufe0f_Integrations.py",
    "governance": "8_#L01f6e1#Ufe0f_Governance.py",
    "offline": "9_#L01f4f1_Offline_Sync.py",
    "exports": "10_#L01f4e4_Exports.py",
}
    runpy.run_path(str(Path(__file__).parent/"pages"/mapping[page]),run_name="__main__")

st.markdown('<div class="page-footer">🐾 PashuRaksha · Government of Maharashtra concept prototype</div>',unsafe_allow_html=True)
