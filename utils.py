import streamlit as st

NAV_ITEMS = [
    ("Home", "home", "🏠", "Home"),
    ("Report Case", "report", "📝", "Report Case"),
    ("Dashboard", "dashboard", "📊", "Dashboard"),
    ("Animal Registry", "animals", "🐄", "Animal Registry"),
    ("Health Records", "health", "💉", "Health Records"),
    ("Vet Review", "vetreview", "👨‍⚕️", "Vet Review"),
    ("Lab Referral", "lab", "🧪", "Lab Referral"),
    ("Alerts", "alerts", "🔔", "Alerts"),
    ("Integrations", "integrations", "🔌", "Integrations"),
    ("Governance", "governance", "🛡️", "Governance"),
    ("Offline Sync", "offline", "📱", "Offline Sync"),
    ("Exports", "exports", "📤", "Exports"),
]



def inject_css():
    st.markdown(r"""
    <style>
    :root{
      --ink:#123c2d;--ink2:#1d5642;--muted:#5e746b;--green:#14855a;--green2:#2bb878;
      --mint:#e9f8f0;--cream:#fffdf7;--line:#cfe7da;--danger:#d94f55;--amber:#e39b26;
      --shadow:0 18px 55px rgba(18,73,51,.10);--radius:24px;
    }
    *{box-sizing:border-box}
    html,body,.stApp{font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink)!important}
    .stApp{background:
      radial-gradient(circle at 7% 12%,rgba(54,191,132,.20),transparent 25%),
      radial-gradient(circle at 92% 18%,rgba(246,194,84,.16),transparent 23%),
      radial-gradient(circle at 75% 88%,rgba(71,164,211,.10),transparent 25%),
      linear-gradient(135deg,#eefbf5 0%,#fffef9 47%,#f4fbf7 100%);
      background-attachment:fixed;overflow-x:hidden;min-height:100vh;
    }
    .stApp:before,.stApp:after{content:"";position:fixed;border-radius:999px;pointer-events:none;z-index:0;filter:blur(1px)}
    .stApp:before{width:430px;height:430px;left:-210px;top:18%;background:rgba(38,167,112,.11);animation:orb1 14s ease-in-out infinite}
    .stApp:after{width:360px;height:360px;right:-170px;bottom:7%;background:rgba(247,192,65,.10);animation:orb2 17s ease-in-out infinite}
    @keyframes orb1{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(120px,45px,0) scale(1.08)}}
    @keyframes orb2{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(-100px,-70px,0) scale(1.1)}}
    @keyframes floatIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
    @keyframes shimmer{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
    @keyframes pulseGlow{0%,100%{box-shadow:0 0 0 0 rgba(43,184,120,.18)}50%{box-shadow:0 0 0 10px rgba(43,184,120,0)}}

    #MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"],[data-testid="stAppDeployButton"]{visibility:hidden!important}
    header[data-testid="stHeader"]{background:transparent!important;height:0!important}
    [data-testid="stSidebar"]{display:none!important}[data-testid="stAppViewContainer"]{margin-left:0!important}
    .block-container{max-width:1450px!important;padding:1.1rem 2.2rem 2.5rem!important;position:relative;z-index:1}

    /* Global readable typography: Streamlit dark-theme text must never disappear on our light cards. */
    .stApp p,.stApp span,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6,
    .stApp div,.stApp li,.stApp td,.stApp th,.stApp [data-testid="stMarkdownContainer"]{color:var(--ink)}
    .stApp .muted,.stApp .muted *{color:var(--muted)!important}
    .stCaptionContainer,.stCaptionContainer *{color:#71867d!important}

    /* Navbar */
    .topnav{position:sticky;top:8px;z-index:1000;margin:0 0 20px;padding:9px 10px;border:1px solid rgba(207,231,218,.95);
      border-radius:22px;background:rgba(255,255,255,.88);backdrop-filter:blur(20px);box-shadow:0 14px 38px rgba(17,73,51,.10)}
    .brand-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:4px 7px 10px}
    .brand{display:flex;align-items:center;gap:11px;font-weight:950;color:var(--ink)!important;font-size:1.05rem;letter-spacing:-.02em}
    .brand-badge{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;background:linear-gradient(135deg,#108354,#35c383);color:white!important;box-shadow:0 9px 22px rgba(20,133,90,.28);animation:pulseGlow 4s infinite}
    .brand-sub{font-size:.72rem;color:#789087!important;font-weight:750}
    .nav-grid{display:flex;gap:7px;overflow-x:auto;scrollbar-width:none;padding:1px}.nav-grid::-webkit-scrollbar{display:none}
    .nav-grid > div{min-width:max-content}
    .nav-user{font-size:.75rem;font-weight:800;color:#4f6a5f!important;background:#f2faf6;padding:7px 11px;border-radius:999px;border:1px solid #d7ebe1}
    .role-strip{margin:0 7px 8px;padding:7px 11px;border-radius:12px;background:#f0faf5;border:1px solid #d7ebe1;color:#39705a!important;font-size:.74rem;font-weight:750}.role-strip *{color:#39705a!important}
    .nav-signout{margin-top:8px}
    .nav-signout button{background:#15372c!important;color:#fff!important;border:1px solid #15372c!important}

    /* Streamlit buttons become navbar pills / action buttons */
    .stButton>button,.stFormSubmitButton>button,.stDownloadButton>button{border-radius:14px!important;border:1px solid #c9e2d5!important;
      min-height:42px;font-weight:850!important;color:var(--ink)!important;background:rgba(255,255,255,.94)!important;
      box-shadow:0 5px 16px rgba(20,75,53,.05);transition:transform .18s ease,box-shadow .18s ease,background .18s ease!important}
    .stButton>button:hover,.stFormSubmitButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(20,75,53,.12)!important}
    .stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:linear-gradient(135deg,#13875b,#25ad78)!important;color:white!important;border-color:#13875b!important}

    /* Hero */
    .hero{position:relative;overflow:hidden;padding:34px 36px;margin:0 0 22px;border:1px solid #d1e9dd;border-radius:30px;
      background:linear-gradient(120deg,rgba(229,249,239,.96),rgba(255,255,255,.92),rgba(246,252,249,.97));
      background-size:200% 200%;animation:shimmer 15s ease infinite;box-shadow:var(--shadow)}
    .hero:before{content:"";position:absolute;width:220px;height:220px;border-radius:50%;right:-65px;top:-90px;background:rgba(46,183,123,.11)}
    .hero:after{content:"";position:absolute;width:120px;height:120px;border-radius:50%;right:110px;bottom:-75px;background:rgba(245,191,66,.10)}
    .hero .section-kicker,.hero h1,.hero p{position:relative;z-index:2}
    .hero h1{font-size:clamp(2rem,3.4vw,3.05rem)!important;line-height:1.05!important;letter-spacing:-.045em!important;margin:.2rem 0 .75rem!important;color:#103d2d!important}
    .hero p{font-size:1.05rem!important;max-width:850px;color:#526c61!important;margin:0!important}
    .section-kicker{font-size:.72rem;font-weight:950;letter-spacing:.12em;text-transform:uppercase;color:#188158!important;margin-bottom:5px}

    /* Home */
    .home-hero{padding:36px;border-radius:30px;background:linear-gradient(135deg,#0d513b,#16875b 55%,#27b87e);color:white;position:relative;overflow:hidden;box-shadow:0 22px 60px rgba(12,83,58,.24);margin-bottom:22px}
    .home-hero:before{content:"";position:absolute;width:420px;height:420px;border:1px solid rgba(255,255,255,.15);border-radius:50%;right:-140px;top:-190px}
    .home-hero:after{content:"";position:absolute;width:300px;height:300px;border:1px solid rgba(255,255,255,.12);border-radius:50%;right:30px;bottom:-240px}
    .home-hero h1,.home-hero p,.home-hero .section-kicker{color:white!important;position:relative;z-index:2}
    .home-hero h1{font-size:clamp(2.2rem,4.2vw,3.7rem)!important;letter-spacing:-.05em!important;margin:.3rem 0 .8rem!important}
    .home-hero p{font-size:1.08rem!important;max-width:760px;color:rgba(255,255,255,.82)!important}
    .hero-badge{display:inline-flex;gap:8px;align-items:center;padding:7px 11px;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.12);border-radius:999px;font-size:.76rem;font-weight:850;color:white!important}
    .home-visual{border-radius:28px;overflow:hidden;border:1px solid #cfe8db;background:linear-gradient(145deg,#e9f8f0,#fffdf6);box-shadow:var(--shadow);min-height:310px;padding:12px}
    .home-visual img{border-radius:20px}

    /* Cards */
    .feature-card,.card,.section-card,.status-card,.metric-card{border:1px solid #d4e9de!important;border-radius:23px!important;background:rgba(255,255,255,.92)!important;
      box-shadow:0 12px 34px rgba(21,77,55,.075)!important;animation:floatIn .42s ease both;transition:transform .22s ease,box-shadow .22s ease}
    .feature-card:hover,.status-card:hover,.card:hover{transform:translateY(-4px);box-shadow:0 20px 42px rgba(21,77,55,.12)!important}
    .feature-card{padding:23px!important;min-height:155px}
    .feature-card h3,.feature-card h4,.status-card h3,.status-card h4{color:#174b38!important;margin:.55rem 0 .35rem!important}
    .card{padding:20px!important}.section-card{padding:22px!important;margin:12px 0!important}.status-card{padding:21px!important}
    .card p,.feature-card p,.status-card p,.section-card p{color:var(--muted)!important}
    .icon-bubble{width:48px;height:48px;border-radius:16px;display:grid;place-items:center;background:#e8f7ef;border:1px solid #cde8d9;font-size:1.35rem}
    .pill{display:inline-block;padding:6px 10px;border-radius:999px;font-weight:900;font-size:.72rem;background:#e8f7ef;color:#176a48!important;border:1px solid #cde8d9}
    .status-online{background:#e8f8ef!important;color:#167049!important}.status-demo{background:#fff5db!important;color:#8b6115!important}
    .stat-number{font-size:2.25rem!important;font-weight:950!important;color:#123c2d!important}.small-label{font-size:.76rem;color:#71877d!important;font-weight:800}
    .risk-high{color:#b33c42!important}.risk-medium{color:#a76b0b!important}.risk-low{color:#1c7b50!important}
    .flow{padding:15px 9px;border-radius:16px;background:rgba(255,255,255,.82);text-align:center;border:1px solid #d8eae1;font-weight:900;color:#245c48!important;box-shadow:0 7px 20px rgba(25,65,45,.05);transition:.2s}
    .flow:hover{transform:translateY(-3px);background:#f1faf5}

    /* Inputs / widgets */
    .stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input,.stTimeInput input,
    .stSelectbox div[data-baseweb="select"],.stMultiSelect div[data-baseweb="select"],.stFileUploader section{border-radius:14px!important;
      border:1px solid #c9e1d5!important;background:#fff!important;color:#173d30!important;box-shadow:0 4px 14px rgba(20,75,53,.04)!important;transition:.18s!important}
    .stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus,.stDateInput input:focus{border-color:#45a979!important;box-shadow:0 0 0 4px rgba(43,184,120,.12)!important}
    .stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#9aaba3!important}
    .stFileUploader section{padding:12px!important}
    .stCheckbox label,.stRadio label,.stSelectbox label,.stMultiSelect label,.stNumberInput label,.stTextInput label,.stTextArea label{font-weight:800!important;color:#2b5545!important}
    .stForm{border-radius:24px!important}
    .form-shell{padding:24px 26px;border-radius:25px;background:linear-gradient(135deg,rgba(255,255,255,.98),rgba(235,249,242,.95));border:1px solid #d0e8dc;box-shadow:var(--shadow);margin:8px 0 18px;position:relative;overflow:hidden}
    .form-shell:after{content:"";position:absolute;width:180px;height:180px;border-radius:50%;right:-65px;top:-85px;background:rgba(42,184,120,.10)}
    .form-title{font-size:1.45rem;font-weight:950;color:#153f30!important;margin:.15rem 0 .35rem}.form-description{color:#61776e!important;max-width:800px}
    .report-section{padding:22px 24px;border-radius:24px;background:linear-gradient(145deg,rgba(255,255,255,.98),rgba(239,250,245,.94));border:1px solid #cfe7da;box-shadow:0 12px 34px rgba(18,73,51,.07);margin:14px 0;position:relative;overflow:hidden}
    .report-section:before{content:"";position:absolute;width:150px;height:150px;border-radius:50%;right:-55px;top:-75px;background:rgba(43,184,120,.10);pointer-events:none}
    .report-section .section-heading{position:relative;z-index:1}
    .field-help{font-size:.78rem;color:#71877d!important;margin:-5px 0 10px}
    .upload-zone{padding:15px 18px;border:1.5px dashed #9fd0b7;border-radius:18px;background:#f5fcf8;margin-top:5px}
    .triage-result{padding:24px;border-radius:25px;background:linear-gradient(135deg,#f7fffa,#ffffff);border:1px solid #cce8d9;box-shadow:0 16px 40px rgba(18,73,51,.10);animation:floatIn .45s ease both}
    .score-wrap{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
    .score-circle{width:92px;height:92px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#22a66d var(--score),#e7f1eb 0);position:relative;box-shadow:0 0 0 8px #effaf4}
    .score-circle:after{content:"";position:absolute;inset:10px;border-radius:50%;background:#fff}
    .score-circle span{position:relative;z-index:1;font-size:1.35rem;font-weight:950;color:#123c2d!important}
    .reason-chip{display:inline-block;padding:8px 11px;border-radius:999px;background:#eef9f3;border:1px solid #cfe8da;color:#2a614d!important;font-weight:750;font-size:.78rem;margin:4px 4px 0 0}
    .submit-strip{padding:14px 16px;border-radius:18px;background:linear-gradient(90deg,#0f6b4c,#1e9c6e);color:#fff!important;margin-top:8px;box-shadow:0 12px 28px rgba(15,107,76,.18)}
    .submit-strip *{color:#fff!important}
    .section-heading{font-size:1.05rem;font-weight:950;color:#174b38!important;margin:8px 0 12px;padding-bottom:9px;border-bottom:1px dashed #cfe4d9}

    /* Metrics */
    div[data-testid="stMetric"]{background:rgba(255,255,255,.94)!important;border:1px solid #d4e9de!important;padding:16px 17px!important;border-radius:19px!important;box-shadow:0 9px 25px rgba(25,65,45,.06)!important}
    div[data-testid="stMetric"] label,div[data-testid="stMetric"] [data-testid="stMetricLabel"]{color:#6a8077!important;font-weight:800!important}
    div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#123c2d!important;font-weight:950!important}
    div[data-testid="stMetric"] [data-testid="stMetricDelta"]{font-weight:900!important}

    .page-footer{padding:30px 0 12px;color:#789087!important;text-align:center;font-size:.78rem}
    .notice{padding:15px 18px;border-radius:17px;background:#eef9f3;border:1px solid #cfe8da;color:#2b604b!important;font-weight:700}
    .warning-box{padding:16px 18px;border-radius:18px;background:#fff7e3;border:1px solid #f1d89c;color:#7b5a18!important}
    .danger-box{padding:16px 18px;border-radius:18px;background:#fff0f1;border:1px solid #efc7ca;color:#8d3339!important}
    .success-box{padding:16px 18px;border-radius:18px;background:#eaf9f0;border:1px solid #c7e7d3;color:#216b49!important}
    .timeline{display:flex;gap:8px;align-items:center;overflow-x:auto;padding:6px 0 12px}.timeline-step{min-width:145px;padding:13px;border-radius:16px;border:1px solid #d7e9e0;background:#fff;text-align:center;font-weight:850;color:#376354!important}.timeline-step.active{background:#e8f8ef;border-color:#bfe1ce;color:#166846!important}
    @media(max-width:900px){.block-container{padding:1rem 1rem 2rem!important}.topnav{top:2px}.brand-sub{display:none}.home-hero{padding:26px}.hero{padding:26px}.nav-grid{gap:5px}}
    </style>
    """, unsafe_allow_html=True)


def require_role(roles):
    if not st.session_state.get("user") or st.session_state.user["role"] not in roles:
        st.error("Permission denied.")
        st.stop()


def hero(title, subtitle, emoji="🐾"):
    st.markdown(f'<div class="hero"><div class="section-kicker">PashuRaksha</div><h1>{emoji} {title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def form_header(kicker, title, description, emoji="✨"):
    st.markdown(f'<div class="form-shell"><div class="section-kicker">{emoji} {kicker}</div><div class="form-title">{title}</div><div class="form-description">{description}</div></div>', unsafe_allow_html=True)


def section_title(title, subtitle=None, emoji=""):
    sub = f'<div class="muted" style="margin-top:3px">{subtitle}</div>' if subtitle else ''
    st.markdown(f'<div style="margin:22px 0 12px"><div class="section-heading">{emoji} {title}</div>{sub}</div>', unsafe_allow_html=True)


def card(title, body, icon="✨"):
    st.markdown(f'<div class="card"><div class="icon-bubble">{icon}</div><h4 style="margin:10px 0 4px">{title}</h4><div class="muted">{body}</div></div>', unsafe_allow_html=True)


def status_card(title, description, icon="🔌", status="Demo mode", online=False):
    cls = "status-online" if online else "status-demo"
    st.markdown(f'''<div class="status-card"><div style="display:flex;justify-content:space-between;gap:10px;align-items:flex-start"><div class="icon-bubble">{icon}</div><span class="pill {cls}">{status}</span></div><h3>{title}</h3><p>{description}</p></div>''', unsafe_allow_html=True)


def risk_badge(level):
    return {"CRITICAL":"🔴 CRITICAL","HIGH":"🟠 HIGH","MEDIUM":"🟡 MEDIUM","LOW":"🟢 LOW"}.get(level, level)


def nav():
    from auth import ROLE_NAV
    current = st.session_state.get("page", "home")
    user = st.session_state.get("user", {})
    role = user.get("role", "User")
    visible = ROLE_NAV.get(role, [])

    st.markdown(
        f"""<div class="topnav"><div class="brand-row"><div class="brand"><div class="brand-badge">🐾</div>
        <div>PashuRaksha<div class="brand-sub">Animal Health Intelligence & Response</div></div></div>
        <div class="nav-user">👤 {role} workspace</div></div>
        <div class="role-strip">🔐 <b>{role}</b> · Showing role-specific tools and permissions</div>
        <div class="nav-grid">""", unsafe_allow_html=True)

    cols = st.columns([0.72] + [1] * len(visible), gap="small")
    with cols[0]:
        if st.button("🏠 Home", key="nav_home", use_container_width=True, type="primary" if current == "home" else "secondary"):
            st.session_state.page = "home"; st.rerun()
    for col, (label, key, icon, permission_name) in zip(cols[1:], visible):
        with col:
            if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True, type="primary" if current == key else "secondary"):
                st.session_state.page = key; st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

    a,b=st.columns([5,1])
    with a: st.caption(f"Signed in as **{user.get('username','')}** · {role}")
    with b:
        if st.button("Sign out", key="top_signout", use_container_width=True):
            st.session_state.user=None; st.session_state.page="home"; st.rerun()
