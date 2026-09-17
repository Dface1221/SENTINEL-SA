# NCIIPC SAT-SA: Supervisory Analytics Tool for SOC Assessment

[![Smart India Hackathon](https://img.shields.io/badge/SIH-Cybersecurity-blue?style=for-the-badge)](https://www.sih.gov.in/)
[![Architecture](https://img.shields.io/badge/Architecture-Air--Gapped%20Local-emerald?style=for-the-badge)](#architecture)
[![License](https://img.shields.io/badge/Mandate-Sec.%2070A%20IT%20Act-navy?style=for-the-badge)](#mandate)

> **Supervisory intelligence for National Critical Information Infrastructure Protection Centre (NCIIPC)**  
> **Shift the Paradigm from Operational SOC Monitoring to Strategic Supervisory Oversight.**

---

## 1. Executive Summary & Problem Context

Critical Sector Entities (CSEs)—spanning Power grids, Banking & Financial networks, Telecommunications, Transportation, Strategic Defence, and Healthcare—regularly operate Security Operations Centres (SOCs) and generate periodic alert and case-management reports.

Traditional national monitoring approaches attempt to ingest raw SIEM feeds in real time, creating massive bandwidth bottlenecks, operational friction, jurisdiction conflicts, and overwhelming alert fatigue.

### The Objective
**SAT-SA does NOT build another SOC, SIEM, or real-time platform.**  
Instead, SAT-SA is a **Supervisory Analytics Platform** that evaluates periodic SOC submissions to:
- Detect operational **Execution Gaps** (e.g., abnormally fast closures of critical events, unescalated high-impact alerts, template-driven copy-paste investigations).
- Reveal **Negative Space Blind Spots** (what SHOULD exist but is absent: unmonitored critical assets, missing MITRE ATT&CK categories, or silent telemetry ingestion failures).
- Establish objective **Sector Peer Benchmarks** without arbitrary "best company" rankings.
- Calculate a transparent, explainable **Supervisory Attention Score (0–100)**.
- Drive the core loop: **FIND → PROVE → PRIORITIZE → HEAL**.

---

## 2. Core Paradigm: FIND → PROVE → PRIORITIZE → HEAL

SAT-SA never issues definitive, adversarial accusations of non-compliance or breach. In accordance with supervisory governance principles, findings are strictly framed as:
- *"Potential execution gap detected"*
- *"Requires supervisory review"*
- *"Potential monitoring blind spot"*
- *"Evidence indicates..."*
- *"Recommended corrective action..."*

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│    1. FIND      │  ──▶  │    2. PROVE     │  ──▶  │   3. PRIORITIZE     │  ──▶  │      4. HEAL        │
│ Suspicious/weak │       │ Underlying data │       │ Supervisory risk &  │       │ Actionable practical│
│ operational     │       │ records & peer  │       │ attention scoring   │       │ corrective actions  │
│ patterns        │       │ baseline delta  │       │ (0–100 scale)       │       │ & verifications     │
└─────────────────┘       └─────────────────┘       └─────────────────────┘       └─────────────────────┘
```

---

## 3. High-Level Architecture

```
                 ┌────────────────────────────────┐
                 │       Human Supervisor         │
                 └──────────────┬─────────────────┘
                                │
                                ▼
 ┌────────────────────────────────────────────────────────────────┐
 │        React Frontend (Vanilla CSS Design System)             │
 │  - High-density Gov-Cybersecurity Dark Navy/Charcoal Theme     │
 │  - 12 Dedicated Functional Views + Interactive Evidence Modals │
 └──────────────────────────────┬─────────────────────────────────┘
                                │ REST API (Port 8000)
                                ▼
 ┌────────────────────────────────────────────────────────────────┐
 │              FastAPI Backend (Python 3.11)                     │
 ├────────────────────────────────┬───────────────────────────────┤
 │ Data Ingestion & Validation    │ Synthetic Demo Data Engine    │
 │ (CSV, JSON, SQLite)            │ (12 CSEs, 17,000+ alerts)     │
 ├────────────────────────────────┼───────────────────────────────┤
 │ Supervisory Analytics Engine   │ "Heal the Wound" Engine       │
 │ - Execution Gap Detection      │ - Finding → Action Mapping    │
 │ - Negative Space Detection     │ - Verification Metrics        │
 │ - Peer Benchmarking            │ - Remediation Tracker         │
 │ - Transparent Attention Score  │ - Printable / HTML Reports    │
 │ - Sample Prioritization Engine │ - Ground-Truth Validation     │
 └──────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
 ┌────────────────────────────────────────────────────────────────┐
 │                 Local SQLite Database                          │
 │  - CSEs, Assets, Alerts, Cases, Telemetry, Escalations         │
 │  - Findings, Remediation Actions, Audit Trail, Ground Truth    │
 └────────────────────────────────────────────────────────────────┘
```

---

## 4. Key Innovations & Differentiators

### A. Negative Space Detection
Most security tools only analyze what exists. SAT-SA evaluates **what SHOULD exist but is absent**:
1. **Critical Asset Telemetry Gaps:** Identifies Tier-1 infrastructure assets (e.g. SCADA RTUs, Core Banking DBs) generating < 30% expected telemetry.
2. **Missing Threat Categories:** Evaluates peer-prevalent MITRE ATT&CK categories (e.g. Ransomware, Lateral Movement) that are completely absent from an entity's telemetry.
3. **Unusually Low Activity:** Detects entities generating 75%+ fewer alerts than sector peers despite identical critical asset scales.
4. **Missing Workflow Evidence:** Identifies cases closed without recorded root cause, evidence artifacts, or remediation records.

### B. Transparent Supervisory Attention Score (0–100)
Unlike opaque "AI black-box" scores, SAT-SA calculates an explicit, auditable composite index:
- **Detection Coverage & Blind Spots (Max 25 pts)**
- **Investigation Diligence & Depth (Max 25 pts)**
- **Escalation Rigor & Compliance (Max 20 pts)**
- **Critical Asset Telemetry Health (Max 15 pts)**
- **Operational Consistency & Metric Gaming (Max 15 pts)**

Classification:
- `0–30`: Normal Monitoring
- `31–60`: Review Recommended
- `61–80`: Elevated Supervisory Attention
- `81–100`: High Priority Manual Review

### C. "Heal the Wound" Local Recommendation Engine
Every finding maps directly to:
1. **Operational Impact:** Why this matters to national critical resilience.
2. **Step-by-Step Corrective Actions:** Practical SOP and configuration changes.
3. **Quantitative Verification Metrics:** Concrete measurable KPIs (e.g. Critical-alert escalation rate >= 80%, Telemetry coverage >= 95%).

### D. Empirical Ground-Truth Validation (SIH Special)
Includes a dynamic validation module benchmarking the supervisory engine against embedded synthetic ground truth, calculating live:
- **Precision:** `TP / (TP + FP)`
- **Recall:** `TP / (TP + FN)`
- **F1 Score:** Harmonic mean
- **Human-in-the-Loop Feedback Calibration:** Tracks supervisor confirmations and dismissals in SQLite.

---

## 5. Technology Stack & Air-Gapped Assurance

- **Backend:** Python 3.11, FastAPI, Uvicorn, SQLAlchemy ORM
- **Analytics:** Pandas, NumPy, Scikit-learn (TF-IDF Cosine Similarity, Isolation Forest)
- **Database:** Local SQLite (`sat_sa.db`, seamless drop-in transition to PostgreSQL)
- **Frontend:** React 18, Vite, Lucide React icons, Custom Vanilla CSS Design System
- **Reporting:** Embedded HTML / Printable Dossiers with official disclaimers
- **Strictly 100% Offline:** Zero external network calls, zero CDN links, zero OpenAI/cloud API dependencies.

---

## 6. Installation & Running Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Quick Start (Development Mode)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nciipc-sih/sat-sa.git
   cd sat-sa
   ```

2. **Install Python Backend Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Launch the FastAPI Backend:**
   ```bash
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
   ```

5. **Launch the Vite Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

### Standalone Single-Process Offline Mode
You can run the entire system (backend + compiled React frontend) with a single command:
```bash
cd frontend && npm run build && cd ..
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Then navigate to `http://127.0.0.1:8000` to access the full application.

---

## 7. 2-Minute SIH Demonstration Script

Follow this scripted flow for a high-impact hackathon presentation:

| Step | Action | What to Explain to Judges |
| :--- | :--- | :--- |
| **1** | Open `http://localhost:5173` | *"SAT-SA is NCIIPC’s Supervisory Analytics Tool for SOC Assessment. Notice our air-gapped dark theme designed for national defense and critical infrastructure oversight."* |
| **2** | Click **"Generate Demo Dataset"** | *"Generates 12 Critical Sector Entities across 6 sectors with over 17,000 alerts and 6,000 cases over 90 days. Data processing is 100% local."* |
| **3** | Click **"Run Supervisory Analysis"** | *"Our analytics engine executes execution gap analysis, negative space detection, peer benchmarking, and transparent attention scoring."* |
| **4** | Point to Top KPI Cards | *"Notice the scale: 17,230 alerts triaged into 28 supervisory signals, highlighting 5 entities requiring review and 7 potential blind spots."* |
| **5** | Click **"Inspect CSE-07 Story"** | *"Here is our star demo case: Northern Regional Load Despatch (Power Grid), flagged with an Attention Score of 79/100."* |
| **6** | Show the **5-Reason Narrative** | *"SAT-SA clearly explains why: 1) Critical closures 85.5% faster than peers, 2) 14 unescalated criticals, 3) 3 SCADA telemetry blind spots, 4) 27 repeated unmitigated alerts, 5) template-driven notes."* |
| **7** | Click finding **"Critical alerts closed unusually quickly"** | *"Drill down into the Finding Detail Modal. Show the explainability matrix, the raw evidence table, and the lifecycle timeline flowchart. Click 'Confirm Finding' to save to SQLite."* |
| **8** | Navigate to **"Negative Space Heatmap"** | *"Show what SHOULD exist but is absent. Notice the rose and purple blind spots on critical telemetry and omitted threat categories."* |
| **9** | Navigate to **"Recommended Samples"** | *"Supervisors don't read 17,000 alerts. Our sample engine selects representative alerts with transparent checkmark rationales ('Why this alert was selected')."* |
| **10** | Navigate to **"Analytics Validation"** | *"Demonstrate empirical evaluation: Precision (100%), Recall (75%), F1 Score (0.86) calculated dynamically against synthetic ground truth."* |
| **11** | Open **"Supervisory Reports"** | *"Generate the Executive Supervisory Assessment Report and CSE Audit Dossier with official NCIIPC headers and non-compliance disclaimers."* |

---

## 8. Directory Layout

```
sat-sa/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # FastAPI REST endpoints
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py            # SQLite / Postgres engine & session
│   │   └── models.py              # SQLAlchemy ORM models
│   ├── data/
│   │   ├── __init__.py
│   │   ├── generator.py           # 12 CSEs synthetic dataset generator
│   │   └── validators.py          # CSV/JSON ingestion validators
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── pipeline.py            # Master supervisory pipeline runner
│   │   ├── execution_gaps.py      # Fast closures, unescalated, weak investigations
│   │   ├── negative_space.py      # Telemetry gaps, missing categories, low volume
│   │   ├── peer_benchmark.py      # Sector distributions, medians, percentiles
│   │   ├── risk_scoring.py        # Transparent 0-100 Attention Score
│   │   ├── sample_prioritization.py # Intelligent alert sampler with checkmarks
│   │   ├── anomalies.py           # Local Scikit-Learn Isolation Forest
│   │   └── validation.py          # Ground-truth precision/recall/F1 evaluator
│   ├── recommendations/
│   │   ├── __init__.py
│   │   └── remediation_engine.py  # "Heal the Wound" mapping & verification metrics
│   ├── reports/
│   │   ├── __init__.py
│   │   └── generator.py           # Printable HTML report generator
│   ├── __init__.py
│   └── main.py                    # App entrypoint and static file mount
├── frontend/
│   ├── src/
│   │   ├── api.js                 # Frontend REST API client
│   │   ├── App.jsx                # Root application router
│   │   ├── index.css              # Vanilla CSS dark cybersecurity design system
│   │   ├── main.jsx               # React DOM root
│   │   ├── components/
│   │   │   ├── Sidebar.jsx        # 12-view navigation drawer
│   │   │   └── TopBar.jsx         # Actions: Generate Data & Run Analysis
│   │   └── views/
│   │       ├── DashboardView.jsx  # National command dashboard
│   │       ├── CSEsView.jsx       # CSE entity directory
│   │       ├── CSEProfileView.jsx # Star demo & entity dossier
│   │       ├── FindingsView.jsx   # Filterable findings explorer
│   │       ├── FindingDetailModal.jsx # FIND->PROVE->PRIORITIZE->HEAL modal
│   │       ├── ReviewQueueView.jsx # Triage queue with SQLite status updates
│   │       ├── SamplesView.jsx    # Recommended samples with checkmarks
│   │       ├── NegativeSpaceView.jsx # 7-pillar color-coded heatmap matrix
│   │       ├── PeerBenchmarkView.jsx # Sector medians and deviation hub
│   │       ├── RemediationView.jsx # Corrective action tracker
│   │       ├── ValidationView.jsx # Ground truth precision/recall evaluator
│   │       ├── ReportsView.jsx    # Printable supervisory reports
│   │       └── DataUploadView.jsx # CSV upload and audit trail
│   ├── package.json
│   └── vite.config.js
├── sample_data/                   # Sample CSVs (alerts, cases, assets)
├── tests/
│   └── test_analytics.py          # Automated integration & regression test suite
├── Dockerfile                     # Container definition
├── docker-compose.yml             # Docker compose deployment
├── requirements.txt               # Python package dependencies
└── README.md                      # Comprehensive project documentation
```

---

## 9. Limitations & Future Roadmap

1. **Production Database:** Prototype utilizes local SQLite with WAL mode for zero-configuration laptop demos. In production, configure `DATABASE_URL=postgresql://user:pass@host/sat_sa_db`.
2. **Automated CSE Connector:** Current ingestion uses batch CSV/JSON upload. Future enhancements include cryptographically signed submission bundles via SFTP or air-gapped diode.
3. **Federated Threat Intelligence:** Integrating local STIX/TAXII indicator feeds without external internet connectivity.

---

## 10. Legal & Compliance Disclaimer

*This tool is designed as an analytical decision-support assistant for authorized supervisory personnel. All indicators, deviation scores, and negative space signals represent statistical alerts for human investigation and do not constitute a definitive finding of legal non-compliance or security compromise.*
