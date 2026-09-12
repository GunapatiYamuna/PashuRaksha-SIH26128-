# PashuRaksha SIH26128 — Demo & Testing Guide

## 1. Start the project

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## 2. Demo accounts

| Role | Username | Password |
|---|---|---|
| Farmer | farmer | farmer123 |
| Field Worker | field | field123 |
| Veterinarian | vet | vet123 |
| District Admin | admin | admin123 |

## 3. Role-specific module test

### Farmer
1. Login as `farmer`.
2. Confirm navbar shows only Farmer modules.
3. Open **Report Case** and submit a case.
4. Open **Animal Registry** and confirm farmer-owned demo animals are visible.
5. Open **Health Records** and add a vaccination/treatment record.
6. Open **Alerts** and confirm it is read-only.
7. Open **Offline Sync**, queue an event, and confirm the queue count increases.

### Field Worker
1. Login as `field`.
2. Confirm Dashboard, Report Case, Animal Registry, Health Records, Lab Referral, Alerts and Offline Sync are available.
3. Submit a field report.
4. Create a laboratory referral.
5. Queue an offline event.

### Veterinarian
1. Login as `vet`.
2. Confirm **Vet Review** and **Governance** are visible.
3. Open **Vet Review**.
4. Select a HIGH/CRITICAL report.
5. Compare Rule Risk vs AI Prediction and AI confidence.
6. Save a verification outcome.
7. Open Governance and confirm the `VERIFY_REPORT` audit event appears.
8. Open Lab Referral and create/update a referral.
9. Open Alerts and publish a multilingual advisory.
10. Open Exports and download an authorised CSV.

### District Admin
1. Login as `admin`.
2. Confirm Governance, Integrations and Exports are visible.
3. Open Dashboard and inspect district/risk map information.
4. Open Governance and inspect AI predictions, confidence and audit trail.
5. Open Integrations and confirm demo readiness status rather than fake live government connectivity.
6. Open Exports and download reports/animals/lab/audit CSVs.

## 4. Strong AI demo case

Create or use a report similar to:
- Species: Cattle
- Herd: 20
- Sick: 10
- Deaths: 2
- Symptoms: Fever, Oral lesions, Salivation
- Rainfall: 30 mm
- Temperature: 35 C
- Humidity: 90%
- Village: Village C (demo vaccination coverage 39%)

The rule engine should produce a high/critical surveillance signal. Governance then trains the prototype Random Forest and predicts a risk category with probabilities/confidence.

**Important:** this AI is a surveillance-priority prototype, not a disease diagnosis model. It is trained on synthetic/rule-derived scenarios because clinically validated labelled livestock surveillance data is not bundled with the hackathon prototype.

## 5. Full end-to-end SIH demo

`Farmer report → Rule risk + AI prediction → Vet Review → Veterinary verification → Lab Referral → Advisory → Admin Dashboard/Governance → Audit Trail`

## 6. What proves each requirement

- Symptom/mortality reporting: Report Case
- Rule/AI triage: Report Case + Governance + Vet Review
- Geospatial view: Dashboard map
- Weather context: Report Case + Dashboard
- Animal/herd records: Animal Registry + Health Records
- Vaccination tracking: Health Records + Dashboard vaccination priority
- Laboratory referral: Lab Referral
- Multilingual advisories: Alerts
- Offline-first queue: Offline Sync
- Role-specific access: Navbar + `auth.py`
- Accountability: Governance audit trail
- Operational exports: Exports
- Integration readiness: Integrations
