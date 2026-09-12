import sqlite3,hashlib,json
from pathlib import Path
from datetime import datetime, timedelta
DB_PATH=Path(__file__).parent/"data"/"pashuraksha.db"
SCHEMA="""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE,password_hash TEXT,role TEXT,active INTEGER DEFAULT 1,created_at TEXT);
CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT,report_code TEXT UNIQUE,reporter TEXT,reporter_role TEXT,village TEXT,block TEXT,district TEXT,species TEXT,animal_count INTEGER,sick_count INTEGER,deaths INTEGER,symptoms TEXT,onset_date TEXT,latitude REAL,longitude REAL,temperature REAL,rainfall REAL,humidity REAL,risk_score INTEGER,risk_level TEXT,recommended_action TEXT,status TEXT,photo_path TEXT,created_at TEXT,verified_by TEXT,animal_tag_id TEXT,review_outcome TEXT,review_notes TEXT,reviewed_by TEXT,reviewed_at TEXT);
CREATE TABLE IF NOT EXISTS animals(id INTEGER PRIMARY KEY AUTOINCREMENT,tag_id TEXT UNIQUE,owner TEXT,village TEXT,species TEXT,breed TEXT,age_months INTEGER,sex TEXT,health_status TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS health_records(id INTEGER PRIMARY KEY AUTOINCREMENT,tag_id TEXT,record_type TEXT,title TEXT,details TEXT,record_date TEXT,provider TEXT);
CREATE TABLE IF NOT EXISTS lab_referrals(id INTEGER PRIMARY KEY AUTOINCREMENT,referral_code TEXT UNIQUE,report_code TEXT,sample_type TEXT,suspected_disease TEXT,lab_name TEXT,collected_by TEXT,collection_date TEXT,priority TEXT,status TEXT,result TEXT,notes TEXT);
CREATE TABLE IF NOT EXISTS advisories(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,language TEXT,audience TEXT,severity TEXT,message TEXT,issued_by TEXT,issued_at TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS audit_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT,role TEXT,action TEXT,entity_type TEXT,entity_id TEXT,metadata TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS sync_queue(id INTEGER PRIMARY KEY AUTOINCREMENT,device_id TEXT,event_id TEXT UNIQUE,payload TEXT,created_at TEXT,synced INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS integration_events(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,event_type TEXT,external_id TEXT,payload TEXT,received_at TEXT,status TEXT);"""
def conn():
    DB_PATH.parent.mkdir(exist_ok=True); c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row
    try: c.execute("ALTER TABLE reports ADD COLUMN photo_path TEXT")
    except sqlite3.OperationalError: pass
    try: c.execute("ALTER TABLE reports ADD COLUMN animal_tag_id TEXT")
    except sqlite3.OperationalError: pass
    try: c.execute("ALTER TABLE reports ADD COLUMN review_outcome TEXT")
    except sqlite3.OperationalError: pass
    try: c.execute("ALTER TABLE reports ADD COLUMN review_notes TEXT")
    except sqlite3.OperationalError: pass
    try: c.execute("ALTER TABLE reports ADD COLUMN reviewed_by TEXT")
    except sqlite3.OperationalError: pass
    try: c.execute("ALTER TABLE reports ADD COLUMN reviewed_at TEXT")
    except sqlite3.OperationalError: pass
    c.commit()
    return c
def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()
def init_db():
    c=conn(); c.executescript(SCHEMA); c.commit(); c.close()
def audit(username,role,action,entity_type="",entity_id="",metadata=None):
    c=conn(); c.execute("INSERT INTO audit_logs(username,role,action,entity_type,entity_id,metadata,created_at) VALUES(?,?,?,?,?,?,?)",(username,role,action,entity_type,entity_id,json.dumps(metadata or {}),datetime.now().isoformat())); c.commit(); c.close()
def seed_demo_data():
    c=conn()
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
        for u,p,r in [("admin","admin123","District Admin"),("vet","vet123","Veterinarian"),("field","field123","Field Worker"),("farmer","farmer123","Farmer")]:
            c.execute("INSERT INTO users(username,password_hash,role,created_at) VALUES(?,?,?,?)",(u,hash_password(p),r,datetime.now().isoformat()))
    if c.execute("SELECT COUNT(*) FROM animals").fetchone()[0]==0:
        animals=[("MH-NAS-0001","farmer","Village A","Cattle","Gir",48,"Female","Healthy"),
        ("MH-NAS-0002","farmer","Village B","Buffalo","Murrah",60,"Female","Under observation"),
        ("MH-PUN-0003","farmer","Village C","Goat","Osmanabadi",30,"Female","Vaccination due"),
        ("MH-NAG-0004","farmer","Village D","Sheep","Deccani",24,"Male","Healthy")]
        c.executemany("INSERT INTO animals(tag_id,owner,village,species,breed,age_months,sex,health_status,created_at) VALUES(?,?,?,?,?,?,?,?,?)",[(a,b,v,s,br,age,se,h,datetime.now().isoformat()) for a,b,v,s,br,age,se,h in animals])
        c.executemany("INSERT INTO health_records(tag_id,record_type,title,details,record_date,provider) VALUES(?,?,?,?,?,?)",[
        ("MH-NAS-0001","Vaccination","FMD","Annual dose administered","2026-08-12","Veterinary Team"),
        ("MH-NAS-0001","Vaccination","Brucellosis","Routine vaccination","2026-07-18","Veterinary Team"),
        ("MH-NAS-0002","Treatment","Fever","Supportive treatment; observation","2026-09-05","Dr. Patil"),
        ("MH-PUN-0003","Vaccination","PPR","Due for campaign dose","2026-09-01","Field Worker")])
    if c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]==0:
        rows=[("PR-NAS-001","field","Field Worker","Village A","Igatpuri","Nashik","Cattle",20,10,2,"Fever, Nasal discharge, Cough","2026-09-05",19.70,73.56,32,28,84,86,"HIGH","Veterinary verification and sample collection","Escalated",None,(datetime.now()-timedelta(hours=4)).isoformat()),
        ("PR-NAS-002","farmer","Farmer","Village C","Niphad","Nashik","Cattle",30,13,1,"Fever, Oral lesions, Salivation","2026-09-06",20.08,74.11,33,35,88,82,"CRITICAL","Immediate veterinary review; isolate affected animals","Escalated",None,(datetime.now()-timedelta(hours=7)).isoformat()),
        ("PR-PUN-003","field","Field Worker","Village B","Haveli","Pune","Goat",40,8,0,"Cough, Nasal discharge","2026-09-06",18.52,73.86,31,12,72,48,"MEDIUM","Veterinary review within 24 hours","New",None,(datetime.now()-timedelta(days=1)).isoformat()),
        ("PR-NAG-004","vet","Veterinarian","Village D","Kamptee","Nagpur","Buffalo",25,2,0,"Weakness, Reduced appetite","2026-09-04",21.23,79.20,30,8,65,27,"LOW","Monitor and provide preventive guidance","Verified",None,(datetime.now()-timedelta(days=2)).isoformat())]
        c.executemany("""INSERT INTO reports(report_code,reporter,reporter_role,village,block,district,species,animal_count,sick_count,deaths,symptoms,onset_date,latitude,longitude,temperature,rainfall,humidity,risk_score,risk_level,recommended_action,status,photo_path,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",rows)
    # Link compatible demo reports to registered animals.
    c.execute("UPDATE reports SET animal_tag_id=? WHERE report_code=?", ("MH-NAS-0001", "PR-NAS-001"))
    c.execute("UPDATE reports SET animal_tag_id=? WHERE report_code=?", ("MH-NAS-0001", "PR-NAS-002"))
    c.execute("UPDATE reports SET animal_tag_id=? WHERE report_code=?", ("MH-PUN-0003", "PR-PUN-003"))
    c.commit(); c.close()
