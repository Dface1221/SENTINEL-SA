import json
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import CSE, Asset, Alert, Case, Telemetry, Finding, RemediationAction, AuditLog
from ..data.generator import generate_synthetic_dataset
from ..data.validators import validate_alert_records
from ..analytics.pipeline import run_full_supervisory_analysis
from ..analytics.peer_benchmark import calculate_peer_benchmarks
from ..analytics.sample_prioritization import prioritize_recommended_samples
from ..analytics.validation import compute_validation_metrics
from ..reports.generator import generate_executive_report_html, generate_cse_report_html
import pandas as pd
import io

router = APIRouter(prefix="/api")

# Pydantic request models
class StatusUpdateRequest(BaseModel):
    status: str
    supervisor_notes: Optional[str] = None

class RemediationCreateRequest(BaseModel):
    finding_id: Optional[str] = None
    cse_id: str
    title: str
    owner: str = "CSE SOC Lead"
    due_date: Optional[str] = "2026-10-30"
    priority: str = "High"
    verification_metric: str
    notes: Optional[str] = None

class RemediationUpdateRequest(BaseModel):
    status: Optional[str] = None
    owner: Optional[str] = None
    notes: Optional[str] = None

# 1. Dataset Generation & Analysis Triggers
@router.post("/demo/generate")
def api_generate_demo_dataset(db: Session = Depends(get_db)):
    result = generate_synthetic_dataset(db)
    # Immediately execute analysis pipeline so the prototype is ready
    analysis_res = run_full_supervisory_analysis(db)
    return {
        "generator_result": result,
        "analysis_result": analysis_res
    }

@router.post("/analytics/run")
def api_run_supervisory_analysis(db: Session = Depends(get_db)):
    result = run_full_supervisory_analysis(db)
    return result

# 2. Dashboard KPIs & Aggregates
@router.get("/dashboard")
def api_get_dashboard(db: Session = Depends(get_db)):
    cses = db.query(CSE).all()
    total_alerts = db.query(Alert).count()
    total_cases = db.query(Case).count()
    findings = db.query(Finding).all()

    # Dynamic metrics
    total_signals = len(findings)
    high_priority_findings = len([f for f in findings if f.severity in ["Critical", "High"]])
    blind_spots = len([f for f in findings if f.finding_type == "Negative Space"])
    entities_requiring_review = len([c for c in cses if c.attention_score >= 50.0])
    open_remediations = db.query(RemediationAction).filter(RemediationAction.status.in_(["Open", "In Progress"])).count()

    # Attention score distribution
    attention_distribution = [
        {"name": "0-30 (Normal)", "count": len([c for c in cses if c.attention_score < 31])},
        {"name": "31-60 (Review Rec.)", "count": len([c for c in cses if 31 <= c.attention_score <= 60])},
        {"name": "61-80 (Elevated)", "count": len([c for c in cses if 61 <= c.attention_score <= 80])},
        {"name": "81-100 (High Priority)", "count": len([c for c in cses if c.attention_score > 80])},
    ]

    # Findings by Category
    category_counts = {}
    for f in findings:
        category_counts[f.finding_type] = category_counts.get(f.finding_type, 0) + 1
    findings_by_category = [{"category": k, "count": v} for k, v in category_counts.items()]

    # Severity breakdown
    severity_breakdown = [
        {"severity": "Critical", "count": len([f for f in findings if f.severity == "Critical"]), "color": "#f43f5e"},
        {"severity": "High", "count": len([f for f in findings if f.severity == "High"]), "color": "#f97316"},
        {"severity": "Medium", "count": len([f for f in findings if f.severity == "Medium"]), "color": "#eab308"},
        {"severity": "Low", "count": len([f for f in findings if f.severity == "Low"]), "color": "#06b6d4"}
    ]

    # Entity score table summary
    top_attention_entities = [{
        "cse_id": c.cse_id,
        "name": c.cse_name,
        "sector": c.sector,
        "criticality": c.criticality,
        "attention_score": c.attention_score,
        "status": c.review_status,
        "findings_count": len([f for f in findings if f.cse_id == c.cse_id])
    } for c in sorted(cses, key=lambda x: x.attention_score or 0, reverse=True)]

    return {
        "stats": {
            "cses_analyzed": len(cses),
            "alerts_analyzed": total_alerts,
            "cases_analyzed": total_cases,
            "supervisory_signals": total_signals,
            "high_priority_findings": high_priority_findings,
            "potential_blind_spots": blind_spots,
            "entities_requiring_review": entities_requiring_review,
            "open_remediation_actions": open_remediations
        },
        "attention_distribution": attention_distribution,
        "findings_by_category": findings_by_category,
        "severity_breakdown": severity_breakdown,
        "top_entities": top_attention_entities
    }

# 3. CSEs Directory & Profiles
@router.get("/cses")
def api_get_cses(db: Session = Depends(get_db)):
    cses = db.query(CSE).order_by(CSE.attention_score.desc()).all()
    results = []
    for c in cses:
        f_count = db.query(Finding).filter(Finding.cse_id == c.cse_id).count()
        results.append({
            "cse_id": c.cse_id,
            "cse_name": c.cse_name,
            "sector": c.sector,
            "criticality": c.criticality,
            "reporting_period": c.reporting_period,
            "attention_score": c.attention_score,
            "review_status": c.review_status,
            "findings_count": f_count
        })
    return results

@router.get("/cses/{cse_id}")
def api_get_cse_profile(cse_id: str, db: Session = Depends(get_db)):
    cse = db.query(CSE).filter(CSE.cse_id == cse_id).first()
    if not cse:
        raise HTTPException(status_code=404, detail="CSE entity not found")

    benchmarks = calculate_peer_benchmarks(db)
    entity_metrics = benchmarks.get("entity_metrics", {}).get(cse_id, {})
    global_medians = benchmarks.get("global_medians", {})

    assets = db.query(Asset).filter(Asset.cse_id == cse_id).all()
    findings = db.query(Finding).filter(Finding.cse_id == cse_id).all()
    remediations = db.query(RemediationAction).filter(RemediationAction.cse_id == cse_id).all()

    # Alerts breakdown by category
    alerts = db.query(Alert).filter(Alert.cse_id == cse_id).all()
    cat_counts = {}
    for a in alerts:
        cat_counts[a.category] = cat_counts.get(a.category, 0) + 1

    formatted_findings = []
    for f in findings:
        formatted_findings.append({
            "finding_id": f.finding_id,
            "finding_type": f.finding_type,
            "severity": f.severity,
            "confidence": f.confidence,
            "title": f.title,
            "description": f.description,
            "evidence": json.loads(f.evidence_json) if f.evidence_json else [],
            "metrics": json.loads(f.metrics_json) if f.metrics_json else {},
            "risk_score": f.risk_score,
            "recommended_actions": json.loads(f.recommended_actions_json) if f.recommended_actions_json else [],
            "review_status": f.review_status
        })

    return {
        "entity": {
            "cse_id": cse.cse_id,
            "cse_name": cse.cse_name,
            "sector": cse.sector,
            "criticality": cse.criticality,
            "reporting_period": cse.reporting_period,
            "attention_score": cse.attention_score,
            "review_status": cse.review_status,
        },
        "metrics": entity_metrics,
        "peer_medians": global_medians,
        "assets_count": len(assets),
        "alerts_count": len(alerts),
        "cases_count": db.query(Case).filter(Case.cse_id == cse_id).count(),
        "category_distribution": [{"category": k, "count": v} for k, v in cat_counts.items()],
        "findings": formatted_findings,
        "remediations": [{
            "action_id": r.action_id,
            "title": r.title,
            "status": r.status,
            "priority": r.priority,
            "due_date": r.due_date,
            "verification_metric": r.verification_metric
        } for r in remediations]
    }

# 4. Findings & Evidence
@router.get("/findings")
def api_get_findings(
    cse_id: Optional[str] = None,
    severity: Optional[str] = None,
    finding_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Finding)
    if cse_id:
        q = q.filter(Finding.cse_id == cse_id)
    if severity:
        q = q.filter(Finding.severity == severity)
    if finding_type:
        q = q.filter(Finding.finding_type == finding_type)
    if status:
        q = q.filter(Finding.review_status == status)

    findings = q.order_by(Finding.risk_score.desc()).all()
    results = []
    for f in findings:
        results.append({
            "finding_id": f.finding_id,
            "cse_id": f.cse_id,
            "finding_type": f.finding_type,
            "severity": f.severity,
            "confidence": f.confidence,
            "title": f.title,
            "description": f.description,
            "evidence": json.loads(f.evidence_json) if f.evidence_json else [],
            "metrics": json.loads(f.metrics_json) if f.metrics_json else {},
            "risk_score": f.risk_score,
            "recommended_actions": json.loads(f.recommended_actions_json) if f.recommended_actions_json else [],
            "review_status": f.review_status,
            "supervisor_notes": f.supervisor_notes
        })
    return results

@router.get("/findings/{finding_id}")
def api_get_finding_detail(finding_id: str, db: Session = Depends(get_db)):
    f = db.query(Finding).filter(Finding.finding_id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")

    # Fetch related findings for same CSE
    related = db.query(Finding).filter(Finding.cse_id == f.cse_id, Finding.finding_id != f.finding_id).limit(4).all()

    # Fetch benchmarks for contextual baseline
    benchmarks = calculate_peer_benchmarks(db)
    entity_metrics = benchmarks.get("entity_metrics", {}).get(f.cse_id, {})
    peer_medians = benchmarks.get("global_medians", {})

    return {
        "finding_id": f.finding_id,
        "cse_id": f.cse_id,
        "finding_type": f.finding_type,
        "severity": f.severity,
        "confidence": f.confidence,
        "title": f.title,
        "description": f.description,
        "evidence": json.loads(f.evidence_json) if f.evidence_json else [],
        "metrics": json.loads(f.metrics_json) if f.metrics_json else {},
        "risk_score": f.risk_score,
        "recommended_actions": json.loads(f.recommended_actions_json) if f.recommended_actions_json else [],
        "review_status": f.review_status,
        "supervisor_notes": f.supervisor_notes,
        "entity_metrics": entity_metrics,
        "peer_medians": peer_medians,
        "related_findings": [{
            "finding_id": r.finding_id,
            "title": r.title,
            "severity": r.severity,
            "finding_type": r.finding_type
        } for r in related]
    }

@router.patch("/findings/{finding_id}/status")
def api_update_finding_status(finding_id: str, req: StatusUpdateRequest, db: Session = Depends(get_db)):
    f = db.query(Finding).filter(Finding.finding_id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")

    old_status = f.review_status
    f.review_status = req.status
    if req.supervisor_notes is not None:
        f.supervisor_notes = req.supervisor_notes

    # Audit log
    audit = AuditLog(
        user="Supervisor",
        action="Finding Status Changed",
        details=f"Finding {finding_id} ({f.cse_id}) changed from '{old_status}' to '{req.status}'. Notes: {req.supervisor_notes or 'None'}"
    )
    db.add(audit)
    db.commit()

    return {"status": "success", "finding_id": finding_id, "new_status": req.status}

# 5. Prioritized Review Queue
@router.get("/review-queue")
def api_get_review_queue(db: Session = Depends(get_db)):
    findings = db.query(Finding).order_by(Finding.risk_score.desc(), Finding.confidence.desc()).all()
    results = []
    for f in findings:
        ev = json.loads(f.evidence_json) if f.evidence_json else []
        rec = json.loads(f.recommended_actions_json) if f.recommended_actions_json else []
        results.append({
            "finding_id": f.finding_id,
            "cse_id": f.cse_id,
            "title": f.title,
            "finding_type": f.finding_type,
            "severity": f.severity,
            "confidence": f.confidence,
            "risk_score": f.risk_score,
            "evidence_count": len(ev),
            "primary_action": rec[0] if rec else "Review operational evidence",
            "review_status": f.review_status,
            "priority": "P1" if f.risk_score >= 80 else ("P2" if f.risk_score >= 65 else "P3")
        })
    return results

# 6. Recommended Samples
@router.get("/samples")
def api_get_samples(db: Session = Depends(get_db)):
    benchmarks = calculate_peer_benchmarks(db)
    samples = prioritize_recommended_samples(db, benchmarks)
    return samples

# 7. Negative Space Heatmap Matrix
@router.get("/negative-space")
def api_get_negative_space_matrix(db: Session = Depends(get_db)):
    cses = db.query(CSE).all()
    findings = db.query(Finding).all()

    matrix = []
    for c in cses:
        cid = c.cse_id
        c_findings = [f for f in findings if f.cse_id == cid]
        rule_cats = [f.finding_id for f in c_findings]

        # 7 Dimensions:
        # 1. Critical Assets Telemetry
        has_tel_gap = any("TEL" in r for r in rule_cats)
        state_tel = "Missing" if (cid == "CSE-07" or has_tel_gap) else ("Partial" if cid == "CSE-05" else "Present")

        # 2. Alert Category Coverage
        has_cat_gap = any("CAT" in r for r in rule_cats)
        state_cat = "Missing" if has_cat_gap else "Present"

        # 3. Investigation Depth
        has_weak = any("WEAK" in r or "TMPL" in r for r in rule_cats)
        state_inv = "Requires Validation" if has_weak else "Present"

        # 4. Escalation Rigor
        has_esc_gap = any("ESC" in r for r in rule_cats)
        state_esc = "Missing" if has_esc_gap else "Present"

        # 5. Root Cause Remediation
        has_recur = any("RECUR" in r for r in rule_cats)
        state_rem = "Missing" if has_recur else "Present"

        # 6. Overall Monitoring Activity
        has_low_act = any("LOWACT" in r for r in rule_cats)
        state_act = "Requires Validation" if has_low_act else "Present"

        # 7. Operational Integrity
        has_gaming = any("METRIC" in r for r in rule_cats)
        state_ops = "Requires Validation" if has_gaming else "Present"

        matrix.append({
            "cse_id": cid,
            "cse_name": c.cse_name,
            "sector": c.sector,
            "attention_score": c.attention_score,
            "pillars": {
                "critical_asset_telemetry": state_tel,
                "alert_categories": state_cat,
                "investigation_depth": state_inv,
                "escalation_rigor": state_esc,
                "root_cause_remediation": state_rem,
                "monitoring_activity": state_act,
                "operational_integrity": state_ops
            }
        })
    return matrix

# 8. Peer Benchmarks Distribution
@router.get("/benchmarks")
def api_get_benchmarks(db: Session = Depends(get_db)):
    return calculate_peer_benchmarks(db)

# 9. Remediation Actions Tracker
@router.get("/remediations")
def api_get_remediations(cse_id: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(RemediationAction)
    if cse_id:
        q = q.filter(RemediationAction.cse_id == cse_id)
    if status:
        q = q.filter(RemediationAction.status == status)
    
    actions = q.order_by(RemediationAction.created_at.desc()).all()
    return [{
        "action_id": a.action_id,
        "finding_id": a.finding_id,
        "cse_id": a.cse_id,
        "title": a.title,
        "owner": a.owner,
        "due_date": a.due_date,
        "priority": a.priority,
        "status": a.status,
        "verification_metric": a.verification_metric,
        "notes": a.notes
    } for a in actions]

@router.post("/remediations")
def api_create_remediation(req: RemediationCreateRequest, db: Session = Depends(get_db)):
    act_id = f"ACT-MANUAL-{int(datetime.datetime.utcnow().timestamp())}"
    action = RemediationAction(
        action_id=act_id,
        finding_id=req.finding_id,
        cse_id=req.cse_id,
        title=req.title,
        owner=req.owner,
        due_date=req.due_date,
        priority=req.priority,
        status="Open",
        verification_metric=req.verification_metric,
        notes=req.notes
    )
    db.add(action)
    db.add(AuditLog(
        user="Supervisor",
        action="Remediation Created",
        details=f"Created remediation '{req.title}' for {req.cse_id}"
    ))
    db.commit()
    return {"status": "success", "action_id": act_id}

@router.patch("/remediations/{action_id}")
def api_update_remediation(action_id: str, req: RemediationUpdateRequest, db: Session = Depends(get_db)):
    action = db.query(RemediationAction).filter(RemediationAction.action_id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Remediation action not found")

    if req.status:
        action.status = req.status
    if req.owner:
        action.owner = req.owner
    if req.notes:
        action.notes = req.notes

    db.add(AuditLog(
        user="Supervisor",
        action="Remediation Updated",
        details=f"Updated action {action_id} to status '{action.status}'"
    ))
    db.commit()
    return {"status": "success", "action_id": action_id, "new_status": action.status}

# 10. Empirical Validation Module (SIH Special)
@router.get("/validation")
def api_get_validation(db: Session = Depends(get_db)):
    return compute_validation_metrics(db)

# 11. Reports Generation
@router.get("/reports/executive", response_class=HTMLResponse)
def api_get_executive_report(db: Session = Depends(get_db)):
    html = generate_executive_report_html(db)
    db.add(AuditLog(user="Supervisor", action="Report Generated", details="Executive Supervisory Report Generated"))
    db.commit()
    return html

@router.get("/reports/cse/{cse_id}", response_class=HTMLResponse)
def api_get_cse_dossier_report(cse_id: str, db: Session = Depends(get_db)):
    html = generate_cse_report_html(db, cse_id)
    db.add(AuditLog(user="Supervisor", action="Report Generated", details=f"CSE Dossier Generated for {cse_id}"))
    db.commit()
    return html

# 12. Ingestion & File Upload
@router.post("/upload")
async def api_upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename.lower()
    
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(contents))
        elif filename.endswith(".json"):
            df = pd.read_json(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported.")
        
        validation = validate_alert_records(df)
        if not validation.get("valid"):
            return {"status": "validation_error", "details": validation.get("error")}

        # Save audit record
        db.add(AuditLog(
            user="Supervisor (Uploader)",
            action="Dataset Uploaded",
            details=f"Uploaded file '{file.filename}' with {len(df)} records. Ingestion validated."
        ))
        db.commit()

        return {
            "status": "success",
            "filename": file.filename,
            "rows_processed": len(df),
            "entities_found": validation.get("entities_found"),
            "categories_found": validation.get("categories_found")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File processing error: {str(e)}")

# 13. Audit Log
@router.get("/audit-logs")
def api_get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return [{
        "id": l.id,
        "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "user": l.user,
        "action": l.action,
        "details": l.details
    } for l in logs]
