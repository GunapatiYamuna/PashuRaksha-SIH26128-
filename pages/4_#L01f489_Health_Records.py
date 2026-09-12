import streamlit as st,pandas as pd
from datetime import date
from database import conn
from auth import record
from utils import require_role,hero,form_header,section_title
require_role(["District Admin","Veterinarian","Field Worker","Farmer"])
hero("Animal health records","A longitudinal timeline for vaccination, treatment, check-ups and mortality.","💉")
c=conn()
if st.session_state.user["role"] == "Farmer":
    animals=pd.read_sql_query("SELECT * FROM animals WHERE owner=?", c, params=(st.session_state.user["username"],))
    records=pd.read_sql_query("SELECT h.* FROM health_records h JOIN animals a ON a.tag_id=h.tag_id WHERE a.owner=? ORDER BY h.record_date DESC", c, params=(st.session_state.user["username"],))
else:
    animals=pd.read_sql_query("SELECT * FROM animals",c)
    records=pd.read_sql_query("SELECT * FROM health_records ORDER BY record_date DESC",c)
c.close()
a,b,c,d=st.columns(4); a.metric("Registered animals",len(animals)); b.metric("Vaccination records",int((records.record_type=="Vaccination").sum()) if len(records) else 0); c.metric("Treatment records",int((records.record_type=="Treatment").sum()) if len(records) else 0); d.metric("Vaccination due",int((animals.health_status=="Vaccination due").sum()) if len(animals) else 0)
form_header("Health timeline","Add vaccination or treatment","Keep every important intervention attached to the animal record.","💉")
if len(animals):
    with st.form("health"):
        a,b=st.columns(2); tag=a.selectbox("Animal",animals.tag_id.tolist()); typ=b.selectbox("Type",["Vaccination","Treatment","Check-up","Mortality"])
        title=st.text_input("Event / vaccine name",placeholder="e.g. FMD vaccination"); details=st.text_area("Details",placeholder="Dose, observation, treatment notes...")
        c,d=st.columns(2); dt=c.date_input("Date",date.today()); provider=d.text_input("Provider","Veterinary Team")
        ok=st.form_submit_button("💾 Save health record",type="primary",use_container_width=True)
    if ok:
        c=conn(); c.execute("INSERT INTO health_records(tag_id,record_type,title,details,record_date,provider) VALUES(?,?,?,?,?,?)",(tag,typ,title,details,str(dt),provider)); c.commit(); c.close(); record("CREATE_HEALTH_RECORD","animal",tag); st.success("Health record saved.")
section_title("Registry snapshot","Current animal identities and health status.","🐄")
st.dataframe(animals[["tag_id","owner","village","species","breed","age_months","sex","health_status"]],use_container_width=True,hide_index=True) if len(animals) else st.markdown('<div class="notice">No animals registered yet.</div>',unsafe_allow_html=True)
section_title("Health timeline","Latest interventions across registered animals.","🕒")
st.dataframe(records,use_container_width=True,hide_index=True) if len(records) else st.markdown('<div class="notice">No health records yet.</div>',unsafe_allow_html=True)
