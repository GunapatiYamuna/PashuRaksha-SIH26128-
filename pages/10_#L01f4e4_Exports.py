import streamlit as st,pandas as pd
from database import conn
from utils import require_role,hero,section_title
require_role(["District Admin","Veterinarian"])
hero("Operational reports & exports","Download clean datasets for authorised analysis, review and planning.","📤")
tables=[("reports","Surveillance reports","Case-level events, risk scores and locations","📊","Operational intelligence"),("animals","Animal registry","Tagged animal and herd identity records","🐄","Population records"),("lab_referrals","Laboratory referrals","Sample movement and diagnostic status","🧪","Diagnostic workflow"),("audit_logs","Audit trail","Governance and accountability events","🛡️","Accountability")]
section_title("Choose a dataset","Each export is presented as an operational action instead of raw database output.","📦")
cols=st.columns(2)
for i,(table,title,desc,icon,tag) in enumerate(tables):
    c=conn(); df=pd.read_sql_query(f"SELECT * FROM {table}",c); c.close();
    with cols[i%2]:
        st.markdown(f'<div class="feature-card" style="margin-bottom:16px"><div style="display:flex;justify-content:space-between;align-items:center"><div class="icon-bubble">{icon}</div><span class="pill">{tag}</span></div><h3>{title}</h3><p>{desc}</p><div style="font-size:1.65rem;font-weight:950;color:#123c2d!important">{len(df):,}</div><div class="small-label">records available</div></div>',unsafe_allow_html=True)
        st.download_button(f"⬇️ Download {table}.csv",df.to_csv(index=False),f"{table}.csv","text/csv",use_container_width=True,key=f"dl_{table}")
section_title("Safe export checklist","The production process should protect personal data and preserve accountability.","✅")
checks=[("Role permission","Only authorised roles can export operational datasets."),("Data minimisation","Remove unnecessary personal information before sharing."),("Audit trail","Record who exported what and when."),("Retention policy","Use approved government retention and sharing rules.")]
cols=st.columns(4)
for col,(t,d) in zip(cols,checks):
    with col: st.markdown(f'<div class="status-card"><div class="icon-bubble">✓</div><h4>{t}</h4><p>{d}</p></div>',unsafe_allow_html=True)
