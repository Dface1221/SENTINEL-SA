# SAT-SA

## Supervisory Analytics Tool for SOC Assessment

> **SIH 2026 — Problem Statement SIH26157**
> A local, air-gapped supervisory analytics platform for assessing Security Operations Center (SOC) performance across Critical Sector Entities.

---

## Overview

**SAT-SA (Supervisory Analytics Tool for SOC Assessment)** is a supervisory decision-support platform designed to help oversight teams assess the operational effectiveness of Security Operations Centers (SOCs) serving Critical Sector Entities (CSEs).

Rather than replacing an organization's SIEM or SOC tooling, SAT-SA works **above the operational layer**.

It analyzes periodic SOC assessment data and identifies:

* Execution gaps in security workflows
* Negative-space and visibility gaps
* Unusual operational patterns
* Missing expected security activity
* Deviations from peer-sector baselines
* Findings requiring supervisory attention
* Corrective actions and remediation status

The platform emphasizes **explainability, evidence traceability, human review, and audit integrity**.

SAT-SA is designed to operate locally and can function in **air-gapped environments without dependence on cloud services or external AI APIs**.

---

## The Problem

Traditional security monitoring platforms are primarily designed for operational SOC teams.

A supervisory organization has a different question:

> **"Is the SOC actually performing the expected security operations, and can we prove where attention is required?"**

A SOC may report that alerts are being processed and cases are being closed, while important execution problems remain hidden.

Examples include:

* Critical alerts being closed unusually quickly
* Critical alerts lacking escalation records
* Repetitive investigation notes
* Repeated alerts without corresponding remediation
* Critical assets lacking expected telemetry
* Expected alert categories being absent
* Unusually low activity from important systems

These are not necessarily visible through conventional volume-based monitoring.

SAT-SA addresses this supervisory gap by looking at both **what happened** and **what should have happened but is missing**.

---

# Core Concept

SAT-SA follows a supervisory analytics pipeline:

```text
Periodic SOC Data
        │
        ▼
┌───────────────────────┐
│ Data Normalization    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Supervisory Analytics │
└───────────┬───────────┘
            │
      ┌─────┴─────┐
      ▼           ▼
Execution      Negative
  Gaps          Space
      │           │
      └─────┬─────┘
            ▼
┌───────────────────────┐
│ Peer Context &        │
│ Anomaly Indicators    │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ Attention Prioritizing│
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ Human Supervisory     │
│ Review                │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ Remediation           │
└───────────┬───────────┘
            ▼
┌───────────────────────┐
│ Tamper-Evident        │
│ Audit Ledger           │
└───────────────────────┘
```

### FIND → PROVE → PRIORITIZE → HEAL

SAT-SA's workflow can be summarized as:

**FIND**
Detect operational deviations and visibility gaps.

**PROVE**
Trace findings back to supporting records and measurable evidence.

**PRIORITIZE**
Surface entities and findings requiring supervisory attention.

**HEAL**
Track recommended corrective actions through remediation and verification.

---

# Key Capabilities

## 1. Supervisory Dashboard

The dashboard provides an overview of the assessment environment.

It presents:

* CSEs assessed
* Alerts analyzed
* Cases reviewed
* Supervisory findings
* Negative-space indicators
* Open remediation actions
* Attention distribution
* Finding categories
* Severity distribution
* High-attention entities
* Recent audit activity

The dashboard dynamically identifies entities requiring attention based on the analytics results rather than relying on a hardcoded demonstration entity.

---

## 2. Execution Gap Detection

SAT-SA looks for situations where operational activity appears inconsistent with expected SOC procedures.

Examples include:

### Fast Critical Alert Closure

A critical alert is closed significantly faster than expected, potentially indicating insufficient investigation.

### Missing Escalation

A critical alert is processed without the expected escalation workflow.

### Repetitive Investigations

Investigation notes show excessive similarity or template-like behavior.

### Repeated Alerts Without Remediation

The same asset repeatedly generates alerts without evidence of root-cause remediation.

These signals are surfaced as explainable findings rather than opaque model predictions.

---

# 3. Negative-Space Analysis

One of SAT-SA's central concepts is **negative-space detection**.

Instead of asking only:

> "What security activity occurred?"

SAT-SA also asks:

> **"What should have been present, but isn't?"**

Examples:

* Critical assets with insufficient telemetry
* Expected alert categories with no observed activity
* Missing investigation records
* Missing escalation records
* Missing remediation evidence
* Unusually low activity from important systems

This helps identify potential visibility gaps that conventional event-count monitoring may overlook.

---

# 4. Explainable Findings

Every supervisory finding is designed to provide an evidence trail.

A typical finding can be understood as:

```text
Signal
  ↓
Expected Baseline
  ↓
Observed Value
  ↓
Deviation
  ↓
Supporting Evidence
  ↓
Supervisory Implication
  ↓
Recommended Action
```

The objective is to ensure that supervisors can understand **why a finding was generated** rather than receiving an unexplained score.

---

# 5. Attention Score

SAT-SA combines relevant supervisory signals into an **Attention Score** used to prioritize entities requiring review.

The score is supported by underlying operational indicators such as:

* Execution gaps
* Negative-space indicators
* Investigation behavior
* Escalation behavior
* Telemetry coverage
* Repeated alerts
* Other measurable operational deviations

The system is designed around explainable deterministic analytics rather than requiring a black-box machine-learning model.

---

# 6. Peer Benchmarking

SAT-SA provides contextual comparison between entities using peer-sector metrics.

The interface focuses on:

* Entity value
* Peer median
* Deviation
* Operational context

Peer benchmarking is intended to provide an objective baseline for supervisory analysis rather than ranking entities as winners or losers.

---

# 7. Supervisory Review Queue

Detected findings can be prioritized through a review queue.

Supervisors can filter findings by:

* Priority
* Category
* Entity
* Status

This allows reviewers to focus on the findings most relevant to their current assessment.

---

# 8. Remediation Tracking

SAT-SA connects findings to corrective actions.

A remediation workflow can include:

```text
Finding
   ↓
Recommended Action
   ↓
Owner
   ↓
Due Date
   ↓
Status
   ↓
Verification Metric
```

Supported remediation states include:

* Open
* In Progress
* Verification Pending
* Completed
* Closed

This allows supervisory assessment to continue beyond detection into measurable corrective action.

---

# 9. Tamper-Evident Audit Ledger

SAT-SA maintains a local **SHA-256 chained audit ledger**.

Each audit record is cryptographically linked to the previous record:

```text
Record 1
   │
   └── Hash 1
          │
          ▼
       Record 2
          │
          └── Hash 2
                 │
                 ▼
              Record 3
```

Each record incorporates the previous hash, creating a sequential chain.

The interface provides an integrity status such as:

```text
AUDIT CHAIN ✓ VALID
```

The system deliberately uses the term **tamper-evident audit ledger** rather than claiming to implement a distributed blockchain network.

---

# 10. Supervisory Reports

SAT-SA provides generated assessment reports containing information such as:

* Executive assessment
* Assessment period
* CSE profile
* Attention Score
* Major findings
* Negative-space indicators
* Peer context
* Evidence and reasoning
* Remediation recommendations
* Audit integrity status

Reports are generated locally.

The current implementation provides an HTML report optimized for browser printing and PDF export through the browser's native **Print → Save as PDF** workflow.

---

# Architecture

SAT-SA uses a deliberately lightweight local architecture.

```text
┌──────────────────────────────────────┐
│              Frontend                │
│                                      │
│       React + Vite                   │
│                                      │
│ Dashboard / CSE / Findings / Review  │
│ Negative Space / Benchmark / Reports │
└──────────────────┬───────────────────┘
                   │
                   │ REST API
                   ▼
┌──────────────────────────────────────┐
│              Backend                 │
│                                      │
│             FastAPI                  │
│                                      │
│ API Routes / Analytics / Reports     │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             Analytics                │
│                                      │
│ Execution Gap Detection              │
│ Negative-Space Analysis              │
│ Peer Benchmarking                    │
│ Attention Scoring                    │
│ Evidence Generation                  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│             SQLite                   │
│                                      │
│ CSE / Assets / Alerts / Cases        │
│ Telemetry / Findings / Remediation   │
│ Audit Ledger                          │
└──────────────────────────────────────┘
```

### Technology Stack

| Layer           | Technology            |
| --------------- | --------------------- |
| Frontend        | React                 |
| Build Tool      | Vite                  |
| Backend         | Python / FastAPI      |
| ORM             | SQLAlchemy            |
| Database        | SQLite                |
| Analytics       | Python                |
| Reports         | Local HTML generation |
| Audit Integrity | SHA-256 hash chain    |
| Deployment      | Local / Air-Gapped    |

---

# Data Model

The core assessment model includes entities such as:

```text
CSE
 ├── Assets
 ├── Alerts
 ├── Cases
 ├── Escalations
 └── Telemetry

Findings
 ├── Evidence
 └── Remediation Actions

Audit Logs
 └── Cryptographic Hash Chain
```

The demonstration environment uses deterministic synthetic data so that the same assessment scenarios can be reproduced reliably.

---

# Synthetic Assessment Dataset

SAT-SA includes a deterministic synthetic data generator for demonstration and development.

The dataset contains multiple Critical Sector Entities with different operational profiles, including scenarios such as:

* Low activity
* Telemetry gaps
* Repeated alerts
* Missing alert categories
* Weak investigations
* Repetitive investigation notes
* Critical alerts closed unusually quickly
* Critical alerts without escalation

The deterministic dataset allows the complete supervisory workflow to be demonstrated without requiring access to sensitive real-world SOC data.

---

# Security & Deployment Philosophy

SAT-SA is designed around a **local-first and air-gapped deployment model**.

The prototype does not require:

* Cloud databases
* Cloud analytics
* External AI APIs
* SaaS monitoring platforms
* PostgreSQL
* Docker orchestration
* Internet connectivity during normal application operation

This architecture is intended to support environments where sensitive supervisory assessment data should remain within the local infrastructure.

---

# Project Structure

```text
SAT-SA/
│
├── backend/
│   ├── analytics/
│   │   ├── execution_gaps.py
│   │   ├── negative_space.py
│   │   └── ...
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── data/
│   │   └── generator.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── reports/
│   │   └── generator.py
│   │
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── App.jsx
│   │   └── api.js
│   │
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
└── README.md
```

---

# Local Setup

## Prerequisites

* Python 3.x
* Node.js
* npm

Clone the repository:

```bash
git clone https://github.com/Dface1221/SENTINEL-SA.git
cd SENTINEL-SA
```

---

## Backend

Create/activate the Python environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

---

## Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The application will be available at:

```text
http://localhost:5173
```

---

# Demonstration Workflow

A complete SAT-SA demonstration can be performed using the following sequence:

### 1. Generate Assessment Data

Generate the deterministic local assessment dataset.

### 2. Run Analytics

Execute the supervisory analytics pipeline.

### 3. Review Dashboard

Inspect the overall supervisory picture and attention distribution.

### 4. Inspect a CSE

Open the entity profile and examine the Attention Score and supporting operational indicators.

### 5. Prove a Finding

Open a finding and trace it from:

```text
Signal → Baseline → Deviation → Evidence
```

### 6. Inspect Negative Space

Review telemetry and activity gaps that indicate potential visibility problems.

### 7. Compare Peer Context

Use peer-sector medians to understand deviations from comparable entities.

### 8. Review Findings

Use the Review Queue to prioritize supervisory attention.

### 9. Track Remediation

Inspect corrective actions and their verification status.

### 10. Verify Audit Integrity

Open the Tamper-Evident Audit Ledger and verify the hash-chain status.

### 11. Generate the Report

Open the supervisory report and use browser printing if a PDF copy is required.

---

# Example Supervisory Questions

SAT-SA is designed to help answer questions such as:

### Operational Discipline

* Are critical alerts being investigated appropriately?
* Are critical events being escalated when expected?
* Are investigations showing meaningful analytical activity?

### Visibility

* Are critical assets producing expected telemetry?
* Are expected alert categories represented?
* Are there suspicious gaps in reported activity?

### Supervisory Attention

* Which entities exhibit multiple operational deviations?
* What evidence supports those deviations?
* Which findings require human review?

### Remediation

* What corrective action has been recommended?
* Who owns the action?
* Has the action reached verification?

### Auditability

* Can supervisory actions be traced?
* Is the audit chain intact?
* Can the integrity of the assessment history be verified?

---

# Design Principles

SAT-SA follows several core principles:

### Explainability over opacity

Every important signal should have a reason and supporting evidence.

### Supervision over replacement

SAT-SA complements SOC/SIEM operations rather than replacing them.

### Absence is a signal

Missing expected activity can be as important as observed malicious activity.

### Context over ranking

Peer comparisons provide context without reducing entities to simplistic rankings.

### Human-in-the-loop

Analytics prioritize attention; supervisors make the final assessment.

### Local-first security

Sensitive supervisory data should not require cloud infrastructure.

### Auditability

Important actions should leave a verifiable integrity trail.

---

# Current Prototype Scope

The current implementation is a demonstration-ready supervisory analytics prototype.

It focuses on:

* Synthetic assessment data
* Deterministic analytics
* Explainable findings
* Negative-space detection
* Peer benchmarking
* Review workflows
* Remediation tracking
* Tamper-evident audit logging
* Local report generation

Production deployment would require additional work around real-world data ingestion, authentication and authorization, deployment hardening, operational security controls, data validation, integration testing, and organization-specific assessment policies.

---

# SIH 2026

**Problem Statement:** SIH26157
**Project:** SAT-SA — Supervisory Analytics Tool for SOC Assessment
**Theme:** Blockchain & Cybersecurity
**Category:** Software

SAT-SA demonstrates how supervisory analytics can transform periodic SOC operational data into:

```text
Evidence
   ↓
Insight
   ↓
Supervisory Attention
   ↓
Human Review
   ↓
Remediation
   ↓
Auditable Outcome
```

---

## Team

**Team:** ROOT.KNIGHT 

**SIH 2026**

---

## License

Add the appropriate project license before public production/reuse.

---

## Disclaimer

SAT-SA is a prototype developed for demonstration and assessment purposes. The synthetic dataset does not represent real Critical Sector Entity or SOC data.
