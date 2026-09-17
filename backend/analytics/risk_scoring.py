from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..database.models import CSE

def calculate_supervisory_attention_scores(db: Session, benchmarks: dict, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes a transparent, explainable 0–100 Supervisory Attention Score for each CSE.
    Scores are strictly derived from deterministic components, not an opaque black box.
    """
    entity_metrics = benchmarks.get("entity_metrics", {})
    global_medians = benchmarks.get("global_medians", {})
    
    # Map findings by CSE and category
    cse_findings_map = {}
    for f in findings:
        cid = f["cse_id"]
        cse_findings_map.setdefault(cid, []).append(f)

    results = {}

    for cid, m in entity_metrics.items():
        c_findings = cse_findings_map.get(cid, [])
        rule_categories = [f.get("rule_category", "") for f in c_findings]

        # 1. Detection Weakness (Max 25 pts)
        # Factors: missing alert categories, low activity, repeat alerts
        score_detection = 0.0
        if "missing_alert_category" in rule_categories:
            score_detection += 10.0
        if "unusually_low_activity" in rule_categories:
            score_detection += 10.0
        if "repeated_alerts_no_remediation" in rule_categories:
            score_detection += 5.0
        score_detection = min(25.0, score_detection)

        # 2. Investigation Quality (Max 25 pts)
        # Factors: critical closure duration (< 15 min), weak investigations (0 evidence), repetitive notes
        score_investigation = 0.0
        crit_dur = m.get("crit_median_dur", 50.0)
        peer_crit_dur = global_medians.get("crit_median_dur", 48.0)
        
        if crit_dur < 12.0:
            score_investigation += 12.0
        elif crit_dur < 20.0:
            score_investigation += 7.0

        if "weak_investigations" in rule_categories:
            score_investigation += 7.0
        if "repetitive_investigation_notes" in rule_categories:
            score_investigation += 6.0
        score_investigation = min(25.0, score_investigation)

        # 3. Escalation Discipline (Max 20 pts)
        # Factors: critical escalation rate < 40%, unescalated critical finding
        score_escalation = 0.0
        crit_esc = m.get("crit_esc_rate", 85.0)
        if crit_esc < 25.0:
            score_escalation += 16.0
        elif crit_esc < 50.0:
            score_escalation += 10.0
        elif crit_esc < 70.0:
            score_escalation += 5.0

        if "unescalated_critical" in rule_categories:
            score_escalation += 4.0
        score_escalation = min(20.0, score_escalation)

        # 4. Telemetry Coverage (Max 15 pts)
        # Factors: telemetry gaps on critical assets, low overall coverage
        score_coverage = 0.0
        tel_cov = m.get("telemetry_coverage", 95.0)
        if "telemetry_gap" in rule_categories:
            score_coverage += 10.0
        if tel_cov < 75.0:
            score_coverage += 5.0
        elif tel_cov < 85.0:
            score_coverage += 3.0
        score_coverage = min(15.0, score_coverage)

        # 5. Operational Consistency & Metric Gaming (Max 15 pts)
        score_ops = 0.0
        if "metric_gaming" in rule_categories:
            score_ops += 9.0
        if "multivariate_anomaly" in rule_categories:
            score_ops += 6.0
        score_ops = min(15.0, score_ops)

        # Total Attention Score
        total_score = round(score_detection + score_investigation + score_escalation + score_coverage + score_ops, 1)

        # Map to supervisory category
        if total_score >= 70.0:
            category_label = "High Priority Manual Review"
            badge_color = "red"
        elif total_score >= 50.0:
            category_label = "Elevated Supervisory Attention"
            badge_color = "orange"
        elif total_score >= 30.0:
            category_label = "Review Recommended"
            badge_color = "amber"
        else:
            category_label = "Normal Monitoring"
            badge_color = "green"

        results[cid] = {
            "cse_id": cid,
            "attention_score": total_score,
            "category_label": category_label,
            "badge_color": badge_color,
            "components": {
                "detection_weakness": {
                    "score": round(score_detection, 1),
                    "max": 25,
                    "label": "Detection Coverage & Patterns"
                },
                "investigation_quality": {
                    "score": round(score_investigation, 1),
                    "max": 25,
                    "label": "Investigation Diligence & Depth"
                },
                "escalation_discipline": {
                    "score": round(score_escalation, 1),
                    "max": 20,
                    "label": "Escalation Rigor & Compliance"
                },
                "telemetry_coverage": {
                    "score": round(score_coverage, 1),
                    "max": 15,
                    "label": "Critical Asset Telemetry Health"
                },
                "operational_consistency": {
                    "score": round(score_ops, 1),
                    "max": 15,
                    "label": "Operational Integrity & Metric Discipline"
                }
            },
            "findings_count": len(c_findings)
        }

        # Update CSE record in DB
        cse_db = db.query(CSE).filter(CSE.cse_id == cid).first()
        if cse_db:
            cse_db.attention_score = total_score
            cse_db.review_status = category_label

    db.commit()
    return results
