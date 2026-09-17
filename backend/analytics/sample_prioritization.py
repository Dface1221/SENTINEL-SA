from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..database.models import Alert, Case, Asset

def prioritize_recommended_samples(db: Session, benchmarks: dict) -> List[Dict[str, Any]]:
    """
    Identifies high-priority representative alert samples for manual supervisory review,
    accompanied by clear checkmark explanations ('Why this alert was selected').
    """
    global_medians = benchmarks.get("global_medians", {})
    peer_crit_dur = global_medians.get("crit_median_dur", 48.0)

    # Query alerts focusing on Critical and High severity
    alerts = db.query(Alert).filter(Alert.severity.in_(["Critical", "High"])).order_by(Alert.timestamp.desc()).all()
    
    # Pre-calculate asset recurrence counts
    asset_counts = {}
    for a in alerts:
        key = (a.cse_id, a.asset_id, a.category)
        asset_counts[key] = asset_counts.get(key, 0) + 1

    samples = []
    seen_assets = set()

    for a in alerts:
        reasons = []
        score = 0

        # Criterion 1: Critical Severity
        if a.severity == "Critical":
            reasons.append("Critical severity operational threat")
            score += 30

        # Criterion 2: Abnormally fast closure
        dur = a.duration_minutes or 0.0
        if dur > 0 and dur < 15.0 and a.severity == "Critical":
            dev = round(((peer_crit_dur - dur) / peer_crit_dur) * 100.0, 1)
            reasons.append(f"Closure time ({dur}m) is {dev}% below peer median ({peer_crit_dur}m)")
            score += 25

        # Criterion 3: Missing escalation
        if a.severity == "Critical" and not a.escalated:
            reasons.append("No Tier-2 / Incident Response escalation record found")
            score += 25

        # Criterion 4: Asset recurrence
        rec_cnt = asset_counts.get((a.cse_id, a.asset_id, a.category), 1)
        if rec_cnt >= 8:
            reasons.append(f"Same asset generated {rec_cnt} recurring '{a.category}' alerts")
            score += 20

        # Check case details
        case = db.query(Case).filter(Case.case_id == a.case_id).first() if a.case_id else None
        if case:
            if (case.evidence_count or 0) == 0:
                reasons.append("Zero forensic evidence artifacts attached to investigation")
                score += 15
            if not case.root_cause_identified:
                reasons.append("No root-cause determination documented in case file")
                score += 10
            if not case.remediation_recorded:
                reasons.append("No engineering remediation recorded")
                score += 10

        # Asset criticality
        asset = db.query(Asset).filter(Asset.asset_id == a.asset_id).first()
        if asset and asset.criticality == "Critical":
            reasons.append(f"Originates from Critical Tier-1 infrastructure asset ({asset.asset_name})")
            score += 15

        # Only select if it has strong compelling reasons
        if len(reasons) >= 3 and score >= 65:
            priority_label = "Critical" if score >= 90 else ("High" if score >= 75 else "Medium")
            samples.append({
                "sample_id": f"SMP-{a.alert_id}",
                "alert_id": a.alert_id,
                "cse_id": a.cse_id,
                "asset_id": a.asset_id,
                "asset_name": asset.asset_name if asset else a.asset_id,
                "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "severity": a.severity,
                "category": a.category,
                "source": a.source,
                "duration_minutes": a.duration_minutes,
                "escalated": a.escalated,
                "case_id": a.case_id or "N/A",
                "evidence_count": case.evidence_count if case else 0,
                "investigation_notes": case.investigation_notes if case else "No case record",
                "score": score,
                "priority": priority_label,
                "selection_reasons": reasons
            })

            # Diversity cap per asset
            seen_assets.add(a.asset_id)

    # Sort samples by score descending
    samples.sort(key=lambda s: s["score"], reverse=True)
    return samples[:25]
