import streamlit as st
from database import audit

ROLES = {
    "District Admin": {
    "Home",
    "Reports",
    "Dashboard",
    "Animal Registry",
    "Health Records",
    "Alerts",
    "Integrations",
    "Governance",
    "Offline Sync",
    "Exports"
},
    "Veterinarian": {"Home", "Report Case", "Dashboard", "Animal Registry", "Health Records", "Vet Review", "Lab Referral", "Alerts", "Governance", "Offline Sync", "Exports"},
    "Field Worker": {"Home", "Report Case", "Dashboard", "Animal Registry", "Health Records", "Lab Referral", "Alerts", "Offline Sync"},
    "Farmer": {"Home", "Report Case", "Animal Registry", "Health Records", "Alerts", "Offline Sync"},
}

ROLE_NAV = {
    "District Admin": [
    ("Dashboard","dashboard","📊","Dashboard"),
    ("Reports","reports","📋","Reports"),
    ("Animals","animals","🐄","Animal Registry"),
    ("Health","health","💉","Health Records"),
    ("Alerts","alerts","🔔","Alerts"),
    ("Governance","governance","🛡️","Governance"),
    ("Integrations","integrations","🔌","Integrations"),
    ("Offline Sync","offline","📱","Offline Sync"),
    ("Exports","exports","📤","Exports")
],
    "Veterinarian": [("Reports","report","📝","Report Case"),("Dashboard","dashboard","📊","Dashboard"),("Animals","animals","🐄","Animal Registry"),("Health","health","💉","Health Records"),("Vet Review","vetreview","👨‍⚕️","Vet Review"),("Lab Referral","lab","🧪","Lab Referral"),("Alerts","alerts","🔔","Alerts"),("Governance","governance","🛡️","Governance"),("Offline Sync","offline","📱","Offline Sync"),("Exports","exports","📤","Exports")],
    "Field Worker": [("Field Reports","report","📝","Report Case"),("Field Dashboard","dashboard","📊","Dashboard"),("Animals","animals","🐄","Animal Registry"),("Health Records","health","💉","Health Records"),("Samples","lab","🧪","Lab Referral"),("Alerts","alerts","🔔","Alerts"),("Offline Sync","offline","📱","Offline Sync")],
    "Farmer": [("Report Health Issue","report","📝","Report Case"),("My Animals","animals","🐄","Animal Registry"),("Health History","health","💚","Health Records"),("Alerts","alerts","🔔","Alerts"),("Offline Reports","offline","📱","Offline Sync")],
}

def role_allowed(page):
    user = st.session_state.get("user") or {}
    role = user.get("role", "")

    # Allow both page keys and display names
    aliases = {
        "home": "Home",
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
    }

    allowed = ROLES.get(role, set())

    # Direct match
    if page in allowed:
        return True

    # Page key → display name
    display_name = aliases.get(page)

    if display_name and display_name in allowed:
        return True

    # Display name → page key
    reverse_alias = {
        value: key for key, value in aliases.items()
    }

    page_key = reverse_alias.get(page)

    if page_key:
        # Check either the key or its display name
        if page_key in allowed or page in allowed:
            return True

    return False
def record(action, entity="", eid="", meta=None):
    u=st.session_state.get("user", {})
    audit(u.get("username","unknown"),u.get("role","unknown"),action,entity,eid,meta)
