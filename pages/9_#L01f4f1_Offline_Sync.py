import streamlit as st,pandas as pd,json,uuid
from datetime import datetime
from database import conn
from auth import record
from utils import require_role,hero,form_header,section_title
require_role(["District Admin","Veterinarian","Field Worker","Farmer"])
hero("Offline-first field operations","Capture now, synchronise later. Designed for villages with unreliable connectivity.","📱")
a,b,c=st.columns(3)
a.metric("Queue mode","Offline ready"); b.metric("GPS / timestamp","Captured"); c.metric("Sync strategy","Automatic")
section_title("How offline mode works","The same field workflow remains usable when the network disappears.","📶")
st.markdown('<div class="timeline"><div class="timeline-step active">1️⃣ Capture report</div><div class="timeline-step active">2️⃣ Save locally</div><div class="timeline-step active">3️⃣ Add GPS + time</div><div class="timeline-step">4️⃣ Network returns</div><div class="timeline-step">5️⃣ Auto-sync</div></div>',unsafe_allow_html=True)
form_header("Sync queue","Queue a field event","This demo mirrors the server-side queue used by an offline mobile/PWA client.","📲")
with st.form("sync"):
    a,b=st.columns(2); device=a.text_input("Device ID","FIELD-DEVICE-01"); event_type=b.selectbox("Event type",["Health report","Vaccination","Treatment visit","Sample collection"])
    payload=st.text_area("Event payload",json.dumps({"type":"health_report","village":"Demo","sick":3,"deaths":0,"gps":{"lat":19.076,"lon":73.878}},indent=2),height=160)
    ok=st.form_submit_button("📥 Save to offline queue",type="primary",use_container_width=True)
if ok:
    eid="EVT-"+uuid.uuid4().hex[:10].upper(); c=conn(); c.execute("INSERT INTO sync_queue(device_id,event_id,payload,created_at,synced) VALUES(?,?,?,?,0)",(device,eid,payload,datetime.now().isoformat())); c.commit(); c.close(); record("QUEUE_OFFLINE_EVENT","sync",eid,{"event_type":event_type}); st.success(f"Queued successfully: {eid}")
c=conn(); q=pd.read_sql_query("SELECT * FROM sync_queue ORDER BY id DESC",c); c.close()
section_title("Synchronisation queue","Pending field events waiting for connectivity.","🔄")
if len(q):
    p=q[q.synced==0] if "synced" in q else q
    x,y=st.columns(2); x.metric("Pending events",len(p)); y.metric("Queue health","Ready")
    st.dataframe(q,use_container_width=True,hide_index=True)
else: st.markdown('<div class="notice">✨ Your offline queue is empty. New field events will appear here.</div>',unsafe_allow_html=True)
