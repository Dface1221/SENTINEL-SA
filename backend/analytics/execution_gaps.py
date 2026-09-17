import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..database.models import CSE, Alert, Case, Asset
from ..recommendations.remediation_engine import get_remediation_plan

def detect_execution_gaps(db: Session, benchmarks: dict) -> List[Dict[str, Any]]:
    findings = []
    entity_metrics = benchmarks.get("entity_metrics", {})
    global_medians = benchmarks.get("global_medians", {})
    peer_crit_dur = global_medians.get("crit_median_dur", 48.0)
    peer_crit_esc = global_medians.get("crit_esc_rate", 78.0)

    # 1. Fast Closure of High/Critical Alerts
    alerts_query = db.query(Alert).filter(Alert.severity.in_(["Critical", "High"])).all()
    if alerts_query:
        alerts_df = pd.DataFrame([{
            "alert_id": a.alert_id,
            "cse_id": a.cse_id,
            "asset_id": a.asset_id,
            "severity": a.severity,
            "category": a.category,
            "duration_minutes": a.duration_minutes or 0.0,
            "acknowledged_at": a.acknowledged_at.strftime("%Y-%m-%d %H:%M:%S") if a.acknowledged_at else "N/A",
            "closed_at": a.closed_at.strftime("%Y-%m-%d %H:%M:%S") if a.closed_at else "N/A",
            "escalated": a.escalated,
            "case_id": a.case_id or "None"
        } for a in alerts_query])

        for cse_id, group in alerts_df.groupby("cse_id"):
            crit_group = group[group["severity"] == "Critical"]
            if len(crit_group) >= 5:
                median_dur = float(crit_group["duration_minutes"].median())
                # Flag if critical closure median is < 18 minutes AND at least 50% below peer median
                if median_dur < 18.0 and median_dur < (peer_crit_dur * 0.50):
                    deviation_pct = round(((median_dur - peer_crit_dur) / peer_crit_dur) * 100.0, 1)
                    evidence_records = crit_group.sort_values("duration_minutes").head(15).replace({np.nan: None}).to_dict(orient="records")
                    rem_plan = get_remediation_plan("fast_closure_critical")

                    findings.append({
                        "finding_id": f"F-GAP-FAST-{cse_id}",
                        "cse_id": cse_id,
                        "finding_type": "Execution Gap",
                        "rule_category": "fast_closure_critical",
                        "severity": "High" if median_dur < 12.0 else "Medium",
                        "confidence": 0.94,
                        "title": f"Critical alerts closed unusually quickly ({median_dur} min vs peer {peer_crit_dur} min)",
                        "description": f"Entity median closure duration for critical severity alerts is {median_dur} minutes, which is {abs(deviation_pct)}% below the peer benchmark median ({peer_crit_dur} minutes). Potential execution gap requiring supervisory validation.",
                        "evidence": evidence_records,
                        "metrics": {
                            "signal": "Abnormally rapid disposition of high-consequence critical alerts",
                            "baseline": f"Peer median = {peer_crit_dur} minutes",
                            "observed": f"Entity median = {median_dur} minutes",
                            "deviation": f"{deviation_pct}% vs peer baseline",
                            "record_count": len(crit_group),
                            "fast_closed_count": int((crit_group["duration_minutes"] < 15.0).sum())
                        },
                        "risk_score": 84 if median_dur < 10.0 else 68,
                        "recommended_actions": rem_plan["recommended_actions"],
                        "verification_metrics": rem_plan["verification_metrics"],
                        "manual_review_required": True
                    })

    # 2. Critical Alerts Without Escalation
    critical_alerts = db.query(Alert).filter(Alert.severity == "Critical").all()
    if critical_alerts:
        crit_df = pd.DataFrame([{
            "alert_id": a.alert_id,
            "cse_id": a.cse_id,
            "asset_id": a.asset_id,
            "category": a.category,
            "case_id": a.case_id or "Unassigned",
            "escalated": a.escalated,
            "duration_minutes": a.duration_minutes or 0.0,
            "closed_at": a.closed_at.strftime("%Y-%m-%d %H:%M:%S") if a.closed_at else "N/A"
        } for a in critical_alerts])

        for cse_id, group in crit_df.groupby("cse_id"):
            unescalated = group[~group["escalated"]]
            unescalated_count = len(unescalated)
            total_crit = len(group)
            esc_rate = round(((total_crit - unescalated_count) / total_crit) * 100.0, 1)

            # Flag if unescalated count >= 5 and escalation rate < 40% (peer median is ~85%)
            if unescalated_count >= 5 and esc_rate < 40.0:
                dev_pct = round(((esc_rate - peer_crit_esc) / peer_crit_esc) * 100.0, 1)
                evidence_records = unescalated.head(15).replace({np.nan: None}).to_dict(orient="records")
                rem_plan = get_remediation_plan("unescalated_critical")

                findings.append({
                    "finding_id": f"F-GAP-ESC-{cse_id}",
                    "cse_id": cse_id,
                    "finding_type": "Execution Gap",
                    "rule_category": "unescalated_critical",
                    "severity": "Critical" if esc_rate < 20.0 else "High",
                    "confidence": 0.92,
                    "title": f"{unescalated_count} critical alerts closed without escalation record",
                    "description": f"Observed critical-alert escalation rate of {esc_rate}%, significantly below peer baseline of {peer_crit_esc}%. {unescalated_count} critical incidents were closed without Tier-2/Incident Response escalation.",
                    "evidence": evidence_records,
                    "metrics": {
                        "signal": "Critical alerts resolved at Tier 1 without documented escalation",
                        "baseline": f"Peer median escalation rate = {peer_crit_esc}%",
                        "observed": f"Entity escalation rate = {esc_rate}%",
                        "deviation": f"{dev_pct}% vs peer baseline",
                        "unescalated_count": unescalated_count,
                        "total_critical": total_crit
                    },
                    "risk_score": 88 if esc_rate < 20.0 else 72,
                    "recommended_actions": rem_plan["recommended_actions"],
                    "verification_metrics": rem_plan["verification_metrics"],
                    "manual_review_required": True
                })

    # 3. Acknowledged but Weakly Investigated Alerts
    cases_query = db.query(Case).all()
    if cases_query:
        cases_df = pd.DataFrame([{
            "case_id": c.case_id,
            "cse_id": c.cse_id,
            "alert_id": c.alert_id,
            "evidence_count": c.evidence_count or 0,
            "root_cause_identified": c.root_cause_identified,
            "remediation_recorded": c.remediation_recorded,
            "duration_minutes": c.duration_minutes or 0.0,
            "investigation_notes": c.investigation_notes or "",
            "closure_reason": c.closure_reason or ""
        } for c in cases_query])

        for cse_id, group in cases_df.groupby("cse_id"):
            # Condition: duration < 12 min, evidence_count == 0, root_cause == False
            weak_cases = group[(group["duration_minutes"] < 15.0) & (group["evidence_count"] == 0) & (~group["root_cause_identified"])]
            weak_count = len(weak_cases)
            if weak_count >= 10:
                evidence_records = weak_cases.head(12).replace({np.nan: None}).to_dict(orient="records")
                rem_plan = get_remediation_plan("weak_investigations")

                findings.append({
                    "finding_id": f"F-GAP-WEAK-{cse_id}",
                    "cse_id": cse_id,
                    "finding_type": "Execution Gap",
                    "rule_category": "weak_investigations",
                    "severity": "High" if weak_count >= 25 else "Medium",
                    "confidence": 0.89,
                    "title": f"{weak_count} cases closed with zero attached evidence and no root cause",
                    "description": f"Detected {weak_count} case investigations with rapid closure times, zero attached forensic evidence, and no recorded root-cause determination. Potential supervisory concern requiring validation.",
                    "evidence": evidence_records,
                    "metrics": {
                        "signal": "Investigation cases closed without forensic artifacts or root cause",
                        "baseline": "Expected minimum >= 1 evidence artifact & root cause documented",
                        "observed": f"{weak_count} weak investigation records",
                        "weak_case_percentage": f"{round((weak_count / len(group)) * 100.0, 1)}% of cases"
                    },
                    "risk_score": 75,
                    "recommended_actions": rem_plan["recommended_actions"],
                    "verification_metrics": rem_plan["verification_metrics"],
                    "manual_review_required": True
                })

        # 4. Repetitive / Template Investigations (TF-IDF Cosine Similarity)
        for cse_id, group in cases_df.groupby("cse_id"):
            notes_list = [n.strip() for n in group["investigation_notes"].tolist() if len(n.strip()) > 15]
            if len(notes_list) >= 20:
                try:
                    vectorizer = TfidfVectorizer(max_features=200, stop_words="english")
                    tfidf_matrix = vectorizer.fit_transform(notes_list)
                    sim_matrix = cosine_similarity(tfidf_matrix)
                    
                    # Calculate upper triangle similarity
                    triu_indices = np.triu_indices_from(sim_matrix, k=1)
                    mean_sim = float(np.mean(sim_matrix[triu_indices]))
                    high_sim_pairs = float(np.sum(sim_matrix[triu_indices] > 0.85) / len(triu_indices[0]))

                    if mean_sim > 0.45 or high_sim_pairs > 0.35:
                        # Extract unique sample templates
                        sample_notes = list(set(notes_list))[:3]
                        rem_plan = get_remediation_plan("repetitive_investigation_notes")

                        findings.append({
                            "finding_id": f"F-GAP-TMPL-{cse_id}",
                            "cse_id": cse_id,
                            "finding_type": "Execution Gap",
                            "rule_category": "repetitive_investigation_notes",
                            "severity": "Medium",
                            "confidence": 0.88,
                            "title": "Repetitive / template-driven investigation notes detected",
                            "description": f"Textual analysis reveals high repetitive similarity (mean similarity {round(mean_sim*100, 1)}%) across case investigation logs. Indicates potential boilerplate copy-paste triage rather than individualized analysis.",
                            "evidence": [{"sample_note": s, "similarity_score": round(mean_sim, 2)} for s in sample_notes],
                            "metrics": {
                                "signal": "High textual similarity across analyst investigation logs",
                                "baseline": "Expected natural language variance (similarity < 25%)",
                                "observed": f"Cosine similarity = {round(mean_sim * 100.0, 1)}%",
                                "high_similarity_ratio": f"{round(high_sim_pairs * 100.0, 1)}% of note pairs exceed 0.85 similarity"
                            },
                            "risk_score": 64,
                            "recommended_actions": rem_plan["recommended_actions"],
                            "verification_metrics": rem_plan["verification_metrics"],
                            "manual_review_required": True
                        })
                except Exception:
                    pass

    # 5. Repeated Alerts Without Root-Cause Remediation
    all_alerts = db.query(Alert).all()
    if all_alerts:
        df_all = pd.DataFrame([{
            "alert_id": a.alert_id,
            "cse_id": a.cse_id,
            "asset_id": a.asset_id,
            "category": a.category,
            "timestamp": a.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "disposition": a.disposition,
            "case_id": a.case_id
        } for a in all_alerts])

        # Group by CSE, Asset, Category
        asset_cat_groups = df_all.groupby(["cse_id", "asset_id", "category"]).size().reset_index(name="alert_count")
        severe_recurrences = asset_cat_groups[asset_cat_groups["alert_count"] >= 12]

        for _, row in severe_recurrences.iterrows():
            cid = row["cse_id"]
            aid = row["asset_id"]
            cat = row["category"]
            cnt = int(row["alert_count"])

            # Check if any remediation was recorded on cases for this asset
            asset_cases = db.query(Case).join(Alert, Case.alert_id == Alert.alert_id).filter(
                Alert.cse_id == cid, Alert.asset_id == aid
            ).all()
            remediations = [c.remediation_recorded for c in asset_cases if c.remediation_recorded]

            if len(remediations) == 0:
                matching_records = df_all[(df_all["cse_id"] == cid) & (df_all["asset_id"] == aid) & (df_all["category"] == cat)].head(15).replace({np.nan: None}).to_dict(orient="records")
                rem_plan = get_remediation_plan("repeated_alerts_no_remediation")

                cat_slug = cat.replace(" ", "_").replace("&", "and").replace("(", "").replace(")", "")
                findings.append({
                    "finding_id": f"F-GAP-RECUR-{cid}-{aid}-{cat_slug}",
                    "cse_id": cid,
                    "finding_type": "Execution Gap",
                    "rule_category": "repeated_alerts_no_remediation",
                    "severity": "High",
                    "confidence": 0.93,
                    "title": f"{cnt} repeated '{cat}' alerts on asset {aid} without remediation",
                    "description": f"Asset {aid} experienced {cnt} recurring alerts of category '{cat}' across the reporting period with zero recorded root-cause remediation tickets.",
                    "evidence": matching_records,
                    "metrics": {
                        "signal": "Chronic recurring alerts on critical asset without permanent remediation",
                        "baseline": "Expected RCA and remediation within 3 recurring occurrences",
                        "observed": f"{cnt} alerts without recorded fix",
                        "asset_id": aid,
                        "category": cat
                    },
                    "risk_score": 79,
                    "recommended_actions": rem_plan["recommended_actions"],
                    "verification_metrics": rem_plan["verification_metrics"],
                    "manual_review_required": True
                })

    # 6. Metric-Gaming Composite Indicator
    for cse_id, m in entity_metrics.items():
        # Composite score: fast closures + low escalation + high repetitive notes or weak investigations
        flags = 0
        if m.get("crit_median_dur", 50) < 15.0:
            flags += 1
        if m.get("crit_esc_rate", 80) < 30.0:
            flags += 1
        if m.get("avg_evidence", 4) < 1.2:
            flags += 1
        if m.get("remediation_rate", 75) < 35.0:
            flags += 1

        if flags >= 3:
            rem_plan = get_remediation_plan("metric_gaming")
            findings.append({
                "finding_id": f"F-METRIC-GAME-{cse_id}",
                "cse_id": cse_id,
                "finding_type": "Metric Gaming",
                "rule_category": "metric_gaming",
                "severity": "High",
                "confidence": 0.86,
                "title": "Potential operational metric optimization pattern requiring supervisory review",
                "description": f"Composite indicator triggered: multiple simultaneous signals observed including abnormally rapid closures ({m.get('crit_median_dur')} min), low critical escalation ({m.get('crit_esc_rate')}%), and minimal forensic evidence ({m.get('avg_evidence')} avg). Manual validation recommended.",
                "evidence": [{
                    "metric": "Critical Closure Median", "value": f"{m.get('crit_median_dur')} min", "peer_norm": f"{peer_crit_dur} min"
                }, {
                    "metric": "Critical Escalation Rate", "value": f"{m.get('crit_esc_rate')}%", "peer_norm": f"{peer_crit_esc}%"
                }, {
                    "metric": "Average Evidence Per Case", "value": str(m.get("avg_evidence")), "peer_norm": "3.5 - 5.0 items"
                }],
                "metrics": {
                    "signal": "Simultaneous co-occurrence of multiple rapid-closure and low-depth indicators",
                    "concurrent_signals": flags,
                    "risk_level": "Elevated supervisory concern"
                },
                "risk_score": 85,
                "recommended_actions": rem_plan["recommended_actions"],
                "verification_metrics": rem_plan["verification_metrics"],
                "manual_review_required": True
            })

    return findings
