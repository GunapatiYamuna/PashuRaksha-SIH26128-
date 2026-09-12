import streamlit as st,pandas as pd,uuid
from datetime import date
from database import conn
from auth import record
from utils import require_role,hero,form_header,section_title
require_role(["District Admin","Veterinarian","Field Worker"])
hero("Laboratory referral","Track sample collection, dispatch, testing and result-driven escalation with a traceable hand-off.","🧪")
c=conn(); reports=pd.read_sql_query("SELECT report_code,risk_level,species,symptoms FROM reports ORDER BY id DESC",c); refs=pd.read_sql_query("SELECT * FROM lab_referrals ORDER BY id DESC",c); c.close()
if len(reports):
    form_header("Diagnostic workflow","Create a laboratory referral","Move a suspected case from field investigation to sample testing without losing traceability.","🧪")
    with st.form("lab"):
        a,b,c=st.columns(3); report=a.selectbox("Surveillance report",reports.report_code.tolist()); sample=b.selectbox("Sample type",["Blood","Swab","Serum","Milk","Tissue","Other"]); priority=c.selectbox("Priority",["Routine","Urgent","Emergency"])
        suspected=st.text_input("Suspected syndrome / disease","Under investigation"); lab=st.selectbox("Laboratory",["District Veterinary Laboratory","Regional Animal Disease Diagnostic Laboratory","Authorised Reference Laboratory"]); notes=st.text_area("Collection notes")
        ok=st.form_submit_button("🧪 Create referral",type="primary",use_container_width=True)
    if ok:
        code="LAB-"+uuid.uuid4().hex[:8].upper(); c=conn(); c.execute("INSERT INTO lab_referrals(referral_code,report_code,sample_type,suspected_disease,lab_name,collected_by,collection_date,priority,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?)",(code,report,sample,suspected,lab,st.session_state.user["username"],str(date.today()),priority,"Sample Collected",notes)); c.commit(); c.close(); record("CREATE_LAB_REFERRAL","lab",code); st.success(f"Referral {code} created.")
section_title("Referral pipeline","Every sample moves through the same visible diagnostic chain.","🔬")
st.markdown('<div class="timeline"><div class="timeline-step active">🧴 Sample collected</div><div class="timeline-step">🚚 Dispatched</div><div class="timeline-step">🔬 Testing</div><div class="timeline-step">📄 Result</div><div class="timeline-step">🚨 Escalate / monitor</div></div>',unsafe_allow_html=True)
if len(refs):
    for _,r in refs.iterrows():
        st.markdown(f'<div class="status-card" style="margin:10px 0"><div style="display:flex;justify-content:space-between;gap:12px"><div><b>{r.referral_code}</b> · {r.report_code}</div><span class="pill">{r.priority}</span></div><p style="margin:.6rem 0"><b>🧪 {r.status}</b> · {r.lab_name} · {r.result or "Result pending"}</p></div>',unsafe_allow_html=True)
        if st.session_state.user["role"] in ["District Admin","Veterinarian"]:
            with st.expander(f"Update {r.referral_code}"):
                with st.form(f"update_{r.referral_code}"):
                    statuses=["Sample Collected","Dispatched","Testing","Result Available","Closed"]; status=st.selectbox("Status",statuses,index=statuses.index(r.status) if r.status in statuses else 0); result=st.selectbox("Result",["","Positive","Negative","Inconclusive"])
                    if st.form_submit_button("Save status"):
                        c=conn(); c.execute("UPDATE lab_referrals SET status=?,result=? WHERE referral_code=?",(status,result,r.referral_code)); c.commit(); c.close(); record("UPDATE_LAB_REFERRAL","lab",r.referral_code,{"status":status,"result":result}); st.rerun()
else: st.markdown('<div class="notice">No referrals yet. High-risk reports can be routed here for sample collection.</div>',unsafe_allow_html=True)
