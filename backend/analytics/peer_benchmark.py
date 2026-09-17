import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from ..database.models import CSE, Alert, Case, Telemetry, Asset

def calculate_peer_benchmarks(db: Session) -> dict:
    """
    Computes sector and global peer distributions for operational SOC metrics.
    Returns entity-level metrics, peer medians, and percentile ranks.
    """
    # Load alerts and cases into pandas DataFrames for fast vector analytics
    alerts_query = db.query(
        Alert.alert_id, Alert.cse_id, Alert.severity, Alert.category,
        Alert.duration_minutes, Alert.escalated, Alert.asset_id
    ).all()
    
    if not alerts_query:
        return {}

    alerts_df = pd.DataFrame([{
        "alert_id": a.alert_id,
        "cse_id": a.cse_id,
        "severity": a.severity,
        "category": a.category,
        "duration_minutes": a.duration_minutes or 0.0,
        "escalated": bool(a.escalated),
        "asset_id": a.asset_id
    } for a in alerts_query])

    cases_query = db.query(
        Case.case_id, Case.cse_id, Case.evidence_count,
        Case.root_cause_identified, Case.remediation_recorded, Case.duration_minutes
    ).all()

    cases_df = pd.DataFrame([{
        "case_id": c.case_id,
        "cse_id": c.cse_id,
        "evidence_count": c.evidence_count or 0,
        "root_cause_identified": bool(c.root_cause_identified),
        "remediation_recorded": bool(c.remediation_recorded),
        "duration_minutes": c.duration_minutes or 0.0
    } for c in cases_query]) if cases_query else pd.DataFrame(columns=["cse_id", "evidence_count", "root_cause_identified", "remediation_recorded", "duration_minutes"])

    telemetry_query = db.query(Telemetry.cse_id, Telemetry.coverage_percentage).all()
    telemetry_df = pd.DataFrame([{
        "cse_id": t.cse_id,
        "coverage": t.coverage_percentage or 0.0
    } for t in telemetry_query]) if telemetry_query else pd.DataFrame(columns=["cse_id", "coverage"])

    cses = db.query(CSE).all()
    entity_metrics = {}

    for cse in cses:
        cid = cse.cse_id
        ent_alerts = alerts_df[alerts_df["cse_id"] == cid]
        ent_cases = cases_df[cases_df["cse_id"] == cid]
        ent_tel = telemetry_df[telemetry_df["cse_id"] == cid]

        # Critical alert metrics
        crit_alerts = ent_alerts[ent_alerts["severity"] == "Critical"]
        crit_median_dur = float(crit_alerts["duration_minutes"].median()) if len(crit_alerts) > 0 else 0.0
        crit_esc_rate = float((crit_alerts["escalated"].sum() / len(crit_alerts)) * 100.0) if len(crit_alerts) > 0 else 0.0

        # High alert metrics
        high_alerts = ent_alerts[ent_alerts["severity"] == "High"]
        high_median_dur = float(high_alerts["duration_minutes"].median()) if len(high_alerts) > 0 else 0.0
        high_esc_rate = float((high_alerts["escalated"].sum() / len(high_alerts)) * 100.0) if len(high_alerts) > 0 else 0.0

        # Overall closure duration
        all_median_dur = float(ent_alerts["duration_minutes"].median()) if len(ent_alerts) > 0 else 0.0

        # Case quality metrics
        avg_evidence = float(ent_cases["evidence_count"].mean()) if len(ent_cases) > 0 else 0.0
        remediation_rate = float((ent_cases["remediation_recorded"].sum() / len(ent_cases)) * 100.0) if len(ent_cases) > 0 else 0.0
        root_cause_rate = float((ent_cases["root_cause_identified"].sum() / len(ent_cases)) * 100.0) if len(ent_cases) > 0 else 0.0

        # Telemetry mean
        tel_coverage = float(ent_tel["coverage"].mean()) if len(ent_tel) > 0 else 100.0

        # Repeated alerts rate (assets with > 5 alerts of same category)
        asset_cat_counts = ent_alerts.groupby(["asset_id", "category"]).size()
        repeated_alerts_count = int(asset_cat_counts[asset_cat_counts >= 5].sum())
        repeated_rate = round((repeated_alerts_count / max(1, len(ent_alerts))) * 100.0, 1)

        entity_metrics[cid] = {
            "cse_id": cid,
            "sector": cse.sector,
            "criticality": cse.criticality,
            "total_alerts": len(ent_alerts),
            "total_cases": len(ent_cases),
            "crit_median_dur": round(crit_median_dur, 1),
            "high_median_dur": round(high_median_dur, 1),
            "all_median_dur": round(all_median_dur, 1),
            "crit_esc_rate": round(crit_esc_rate, 1),
            "high_esc_rate": round(high_esc_rate, 1),
            "avg_evidence": round(avg_evidence, 1),
            "remediation_rate": round(remediation_rate, 1),
            "root_cause_rate": round(root_cause_rate, 1),
            "telemetry_coverage": round(tel_coverage, 1),
            "repeated_rate": repeated_rate
        }

    # Now calculate peer medians across all entities and per sector
    metrics_summary_df = pd.DataFrame(list(entity_metrics.values()))
    
    global_medians = {
        "crit_median_dur": round(float(metrics_summary_df["crit_median_dur"].median()), 1),
        "high_median_dur": round(float(metrics_summary_df["high_median_dur"].median()), 1),
        "all_median_dur": round(float(metrics_summary_df["all_median_dur"].median()), 1),
        "crit_esc_rate": round(float(metrics_summary_df["crit_esc_rate"].median()), 1),
        "avg_evidence": round(float(metrics_summary_df["avg_evidence"].median()), 1),
        "remediation_rate": round(float(metrics_summary_df["remediation_rate"].median()), 1),
        "telemetry_coverage": round(float(metrics_summary_df["telemetry_coverage"].median()), 1),
        "repeated_rate": round(float(metrics_summary_df["repeated_rate"].median()), 1)
    }

    # Attach peer comparisons to each entity
    for cid, m in entity_metrics.items():
        m["peer_medians"] = global_medians
        
        # Percent deviations: ((Entity - Peer) / Peer) * 100
        p_crit = global_medians["crit_median_dur"]
        m["crit_dur_deviation"] = round(((m["crit_median_dur"] - p_crit) / max(1.0, p_crit)) * 100.0, 1)
        
        p_esc = global_medians["crit_esc_rate"]
        m["crit_esc_deviation"] = round(((m["crit_esc_rate"] - p_esc) / max(1.0, p_esc)) * 100.0, 1)

        p_tel = global_medians["telemetry_coverage"]
        m["tel_deviation"] = round(((m["telemetry_coverage"] - p_tel) / max(1.0, p_tel)) * 100.0, 1)

    return {
        "entity_metrics": entity_metrics,
        "global_medians": global_medians
    }
