import streamlit as st,pandas as pd
from database import conn
from utils import require_role,hero,section_title
require_role(["District Admin","Veterinarian","Field Worker"])
hero("Surveillance command centre","See emerging clusters, vaccination gaps and priority cases at a glance.","📊")
c=conn(); df=pd.read_sql_query("SELECT * FROM reports ORDER BY created_at DESC",c); c.close()
if df.empty: st.markdown('<div class="notice">No reports yet. Start with <b>Report Case</b> to create the first surveillance signal.</div>',unsafe_allow_html=True); st.stop()
a,b,d,e=st.columns(4); a.metric("Reports",len(df)); b.metric("High / critical",int(df.risk_level.isin(["HIGH","CRITICAL"]).sum())); d.metric("Animals affected",int(df.sick_count.sum())); e.metric("Deaths",int(df.deaths.sum()))
section_title("Emerging risk map","Markers show reported events. Production can add village boundaries and cluster polygons.","🗺️")
left,right=st.columns([1.55,1])
with left:
    mapdf=df[["latitude","longitude"]].dropna().rename(columns={"latitude":"lat","longitude":"lon"}); st.map(mapdf,zoom=6)
with right:
    st.markdown('<div class="feature-card"><div class="icon-bubble">🔥</div><h3>Risk distribution</h3></div>',unsafe_allow_html=True); st.bar_chart(df["risk_level"].value_counts())
section_title("District intelligence","Average risk helps officials decide where to investigate first.","🏛️")
district=df.groupby("district").agg(reports=("id","count"),affected=("sick_count","sum"),deaths=("deaths","sum"),risk=("risk_score","mean")).sort_values("risk",ascending=False); st.dataframe(district.round(0),use_container_width=True)
section_title("Vaccination priority","Combine coverage gaps with surveillance risk to target the next field campaign.","💉")
coverage=pd.DataFrame({"Village":["Village A","Village B","Village C","Village D"],"Coverage %":[94,76,39,88],"Priority":["Low","Medium","High","Low"]})
x,y=st.columns([1.2,1]);
with x: st.dataframe(coverage,use_container_width=True,hide_index=True)
with y: st.markdown('<div class="warning-box"><b>🚨 Priority village: Village C</b><br>39% vaccination coverage. Prioritise outreach when surveillance risk is also rising.</div>',unsafe_allow_html=True)
section_title("Environmental risk context","Demo environmental signals are captured with each report.","🌦️")
st.markdown('<div class="section-card"><b>Production integration path</b><p>Authorised weather feeds can supply rainfall, temperature and humidity; historical disease incidence and livestock population can be joined to create district-level risk context.</p></div>',unsafe_allow_html=True)
section_title("Priority cases","High and critical reports requiring fast human review.","🚨")
priority=df[df.risk_level.isin(["HIGH","CRITICAL"])][["report_code","district","block","village","species","sick_count","deaths","risk_score","risk_level","status"]]; st.dataframe(priority,use_container_width=True,hide_index=True)
