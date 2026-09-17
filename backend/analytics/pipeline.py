import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..database.models import Finding, RemediationAction, AuditLog
from .peer_benchmark import calculate_peer_benchmarks
from .execution_gaps import detect_execution_gaps
from .negative_space import detect_negative_space
from .anomalies import run_local_anomaly_detection
from .risk_scoring import calculate_supervisory_attention_scores
from .sample_prioritization import prioritize_recommended_samples

def run_full_supervisory_analysis(db: Session) -> Dict[str, Any]:
    """
    Master supervisory pipeline:
    1. Peer Benchmarking
    2. Execution Gap Detection
    3. Negative Space Detection
    4. Local ML Anomaly Detection
    5. Supervisory Attention Scoring
    6. Database Persistence & Audit Logging
    """
    # 1. Peer Benchmarks
    benchmarks = calculate_peer_benchmarks(db)
    if not benchmarks:
        return {"status": "error", "message": "No data found to analyze."}

    # 2. Execution Gaps
    gap_findings = detect_execution_gaps(db, benchmarks)

    # 3. Negative Space
    neg_findings = detect_negative_space(db, benchmarks)

    # 4. Anomalies
    anom_findings = run_local_anomaly_detection(db, benchmarks)

    all_findings = gap_findings + neg_findings + anom_findings

    # 5. Supervisory Attention Scores
    scores = calculate_supervisory_attention_scores(db, benchmarks, all_findings)

    # 6. Sample Prioritization
    samples = prioritize_recommended_samples(db, benchmarks)

    # 7. Persist Findings to SQLite
    # Clear existing findings to refresh
    db.query(Finding).delete()
    db.commit()

    findings_to_insert = []
    remediations_to_insert = []
    seen_finding_ids = set()
    seen_action_ids = set()

    for f in all_findings:
        fid = f["finding_id"]
        if fid in seen_finding_ids:
            continue
        seen_finding_ids.add(fid)

        finding_row = Finding(
            finding_id=fid,
            cse_id=f["cse_id"],
            finding_type=f["finding_type"],
            severity=f["severity"],
            confidence=f["confidence"],
            title=f["title"],
            description=f["description"],
            evidence_json=json.dumps(f["evidence"]),
            metrics_json=json.dumps(f["metrics"]),
            risk_score=f["risk_score"],
            recommended_actions_json=json.dumps(f["recommended_actions"]),
            review_status="New",
            supervisor_notes=None
        )
        findings_to_insert.append(finding_row)

        # Seed initial remediation items for high-priority findings
        if f["severity"] in ["Critical", "High"] and f["recommended_actions"]:
            action_id = f"ACT-{fid}"
            if action_id not in seen_action_ids:
                seen_action_ids.add(action_id)
                existing_act = db.query(RemediationAction).filter(RemediationAction.action_id == action_id).first()
                if not existing_act:
                    rec_actions = f["recommended_actions"]
                    ver_metrics = f.get("verification_metrics", ["Supervisory operational review"])
                    remediations_to_insert.append(RemediationAction(
                        action_id=action_id,
                        finding_id=fid,
                        cse_id=f["cse_id"],
                        title=f"Corrective Action: {rec_actions[0]}",
                        owner=f"{f['cse_id']} SOC Team Lead",
                        due_date="2026-10-15",
                        priority=f["severity"],
                        status="Open",
                        verification_metric=ver_metrics[0] if ver_metrics else "Conformity verification",
                        notes=f"Auto-generated from finding {fid}."
                    ))

    db.bulk_save_objects(findings_to_insert)
    if remediations_to_insert:
        db.bulk_save_objects(remediations_to_insert)

    # Audit log
    audit = AuditLog(
        user="Supervisor (Pipeline)",
        action="Analysis Executed",
        details=f"Supervisory analysis completed: {len(all_findings)} findings identified across {len(scores)} entities. {len(remediations_to_insert)} remediation actions staged."
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "total_findings": len(all_findings),
        "execution_gaps_count": len(gap_findings),
        "negative_space_count": len(neg_findings),
        "anomalies_count": len(anom_findings),
        "prioritized_samples_count": len(samples),
        "entities_analyzed": len(scores)
    }
