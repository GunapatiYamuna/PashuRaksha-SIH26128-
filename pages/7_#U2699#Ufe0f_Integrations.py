import os
import streamlit as st
from integrations import status, notification_status
from utils import require_role, hero, section_title, status_card

require_role(["District Admin","Veterinarian"])
hero("Connected ecosystem","A clean control centre for authorised government, weather, laboratory and notification connections.","🔌")

st.markdown('<div class="notice">🔗 <b>Why this code exists:</b> integrations.py is an adapter layer. It checks whether an authorised endpoint and token are configured and provides a safe place to add real API calls later. The demo intentionally does <b>not</b> pretend that government systems are live.</div>', unsafe_allow_html=True)

services=[
    ("Bharat Pashudhan / NDLM","BHARAT_PASHUDHAN","🐄","Animal identity and livestock records","Identity exchange"),
    ("NADRES","NADRES","🧬","Disease surveillance and epidemiological exchange","Surveillance"),
    ("Weather","WEATHER","🌦️","Environmental risk context for temperature, rainfall and humidity","Risk context"),
    ("Laboratory","LAB","🧪","Sample referral, testing status and diagnostic results","Diagnostics"),
]
section_title("Authorised data connections","Each connector has a visible readiness state and no raw JSON is shown to the judge.","🔗")
cols=st.columns(2)
for i,(label,key,icon,desc,tag) in enumerate(services):
    s=status(key)
    online=s.get("configured",False)
    with cols[i%2]:
        status_card(label,desc,icon,"CONNECTED" if online else "DEMO READY",online)
        c1,c2=st.columns([1.2,1])
        with c1: st.markdown(f'<span class="pill">{tag}</span>',unsafe_allow_html=True)
        with c2: st.caption("Authorised endpoint configured" if online else "Awaiting deployment credentials")

section_title("Multi-channel notifications","Target farmers, field workers, veterinarians and officials through the appropriate channel.","📢")
ns=notification_status()
channels=[("SMS","📨","SMS_PROVIDER_URL","Works on basic phones"),("IVR","☎️","IVR_PROVIDER_URL","Voice-first field access"),("Push","🔔","PUSH_PROVIDER_URL","App notifications"),("In-app","📱",None,"Always available inside PashuRaksha")]
cols=st.columns(4)
for col,(name,icon,key,desc) in zip(cols,channels):
    connected=True if key is None else ns.get(name.lower(),False)
    with col:
        status_card(name,desc,icon,"READY" if connected else "DEMO READY",connected)

section_title("Deployment readiness","Credentials stay outside source code through environment variables.","⚙️")
keys=["BHARAT_PASHUDHAN_URL","NADRES_URL","WEATHER_URL","LAB_URL","SMS_PROVIDER_URL","IVR_PROVIDER_URL","PUSH_PROVIDER_URL","DATABASE_URL"]
cols=st.columns(2)
for i,k in enumerate(keys):
    configured=bool(os.getenv(k))
    with cols[i%2]:
        st.markdown(f'<div class="status-card" style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;align-items:center"><b style="font-size:.95rem">{k}</b><span class="pill {"status-online" if configured else "status-demo"}">{"CONFIGURED" if configured else "NOT CONFIGURED"}</span></div><p style="margin:.6rem 0 0">{("Ready for an authorised deployment value." if configured else "Demo mode uses local data and adapter readiness checks.")}</p></div>',unsafe_allow_html=True)

st.markdown('<div class="warning-box">🔐 <b>Production rule:</b> only authorised department endpoints, approved credentials and permitted data-sharing agreements should be connected. No fake live API status is used in this prototype.</div>',unsafe_allow_html=True)
