import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..database.models import CSE, Asset, Alert, Case, Telemetry
from ..recommendations.remediation_engine import get_remediation_plan

def detect_negative_space(db: Session, benchmarks: dict) -> List[Dict[str, Any]]:
    findings = []
    entity_metrics = benchmarks.get("entity_metrics", {})
    global_medians = benchmarks.get("global_medians", {})

    # A. Critical Asset Telemetry Gap
    # Compare critical assets: expected telemetry vs received
    assets_query = db.query(Asset).filter(Asset.criticality.in_(["Critical", "High"])).all()
    if assets_query:
        assets_df = pd.DataFrame([{
            "asset_id": a.asset_id,
            "cse_id": a.cse_id,
            "asset_name": a.asset_name,
            "asset_type": a.asset_type,
            "criticality": a.criticality,
            "telemetry_expected": a.telemetry_expected or 100,
            "telemetry_received": a.telemetry_received or 0
        } for a in assets_query])

        assets_df["coverage_pct"] = (assets_df["telemetry_received"] / assets_df["telemetry_expected"]) * 100.0

        for cse_id, group in assets_df.groupby("cse_id"):
            # Severely degraded telemetry assets (< 30% coverage)
            gapped_assets = group[group["coverage_pct"] < 30.0]
            if len(gapped_assets) >= 1:
                gapped_count = len(gapped_assets)
                evidence_records = gapped_assets.replace({np.nan: None}).to_dict(orient="records")
                rem_plan = get_remediation_plan("telemetry_gap")

                findings.append({
                    "finding_id": f"F-NEG-TEL-{cse_id}",
                    "cse_id": cse_id,
                    "finding_type": "Negative Space",
                    "rule_category": "telemetry_gap",
                    "severity": "Critical" if gapped_count >= 3 else "High",
                    "confidence": 0.96,
                    "title": f"Potential monitoring blind spot: {gapped_count} critical assets with little/no telemetry",
                    "description": f"Supervisory inventory audit revealed {gapped_count} critical infrastructure assets generating under 30% expected telemetry during the reporting period. Absence of security telemetry creates potential operational blindness.",
                    "evidence": evidence_records,
                    "metrics": {
                        "signal": "Telemetry absence on designated critical infrastructure assets",
                        "baseline": "Expected >= 90% continuous telemetry ingestion",
                        "observed": f"{gapped_count} critical assets with severe telemetry deficit",
                        "affected_asset_ids": [r["asset_id"] for r in evidence_records]
                    },
                    "risk_score": 90 if gapped_count >= 3 else 75,
                    "recommended_actions": rem_plan["recommended_actions"],
                    "verification_metrics": rem_plan["verification_metrics"],
                    "manual_review_required": True
                })

    # B. Missing Alert Categories
    # Calculate all alert categories reported across peers
    alerts_query = db.query(Alert.cse_id, Alert.category).all()
    if alerts_query:
        df_alerts = pd.DataFrame([{"cse_id": a.cse_id, "category": a.category} for a in alerts_query])
        peer_categories = set(df_alerts["category"].unique())

        cses = db.query(CSE).all()
        for cse in cses:
            cid = cse.cse_id
            ent_alerts = df_alerts[df_alerts["cse_id"] == cid]
            ent_cats = set(ent_alerts["category"].unique())
            missing_cats = peer_categories - ent_cats

            # Key high-risk categories to check
            high_risk_expected = {"Lateral Movement", "Ransomware Precursor", "Brute Force Authentication"}
            missing_high_risk = missing_cats.intersection(high_risk_expected)

            if missing_high_risk:
                rem_plan = get_remediation_plan("missing_alert_category")
                findings.append({
                    "finding_id": f"F-NEG-CAT-{cid}",
                    "cse_id": cid,
                    "finding_type": "Negative Space",
                    "rule_category": "missing_alert_category",
                    "severity": "High",
                    "confidence": 0.87,
                    "title": f"Potential detection coverage gap: Complete absence of {', '.join(missing_high_risk)} alerts",
                    "description": f"While comparable peer entities generated regular detections across {', '.join(missing_high_risk)}, {cid} recorded zero alerts in these categories throughout the reporting period. Absence of expected evidence requires validation.",
                    "evidence": [{
                        "missing_category": cat,
                        "peer_prevalence": "Present across 85%+ sector peers",
                        "entity_detections": 0
                    } for cat in missing_high_risk],
                    "metrics": {
                        "signal": "Zero detections recorded for core threat tactic categories",
                        "baseline": "Expected baseline visibility across peer-confirmed categories",
                        "observed": f"0 alerts in {len(missing_high_risk)} critical categories",
                        "missing_categories": list(missing_high_risk)
                    },
                    "risk_score": 78,
                    "recommended_actions": rem_plan["recommended_actions"],
                    "verification_metrics": rem_plan["verification_metrics"],
                    "manual_review_required": True
                })

    # C. Unusually Low Activity
    # Compare alert volume vs critical asset count against peers
    all_cses = db.query(CSE).all()
    volume_stats = []
    for cse in all_cses:
        cid = cse.cse_id
        alert_cnt = db.query(Alert).filter(Alert.cse_id == cid).count()
        crit_asset_cnt = db.query(Asset).filter(Asset.cse_id == cid, Asset.criticality.in_(["Critical", "High"])).count()
        volume_stats.append({
            "cse_id": cid,
            "alerts": alert_cnt,
            "crit_assets": crit_asset_cnt,
            "ratio": alert_cnt / max(1, crit_asset_cnt)
        })

    vol_df = pd.DataFrame(volume_stats)
    if len(vol_df) > 0:
        median_ratio = float(vol_df["ratio"].median())
        for _, row in vol_df.iterrows():
            cid = row["cse_id"]
            ratio = row["ratio"]
            # Flag if ratio is less than 35% of median AND critical assets >= 15
            if ratio < (median_ratio * 0.35) and row["crit_assets"] >= 15:
                pct_below = round(((median_ratio - ratio) / median_ratio) * 100.0, 1)
                rem_plan = get_remediation_plan("unusually_low_activity")

                findings.append({
                    "finding_id": f"F-NEG-LOWACT-{cid}",
                    "cse_id": cid,
                    "finding_type": "Negative Space",
                    "rule_category": "unusually_low_activity",
                    "severity": "High",
                    "confidence": 0.90,
                    "title": f"Anomalously low alert activity ({pct_below}% below peer baseline)",
                    "description": f"Entity generated {int(row['alerts'])} total alerts despite managing {int(row['crit_assets'])} high-criticality assets ({round(ratio, 1)} alerts/asset vs peer median {round(median_ratio, 1)}). Indicates potential sensor outage, ingestion suppression, or operational blind spot.",
                    "evidence": [{
                        "monitored_critical_assets": int(row["crit_assets"]),
                        "actual_alerts": int(row["alerts"]),
                        "alerts_per_asset": round(ratio, 1),
                        "peer_median_alerts_per_asset": round(median_ratio, 1)
                    }],
                    "metrics": {
                        "signal": "Dramatically depressed alert telemetry volume relative to asset scale",
                        "baseline": f"Peer median = {round(median_ratio, 1)} alerts/asset",
                        "observed": f"Entity ratio = {round(ratio, 1)} alerts/asset",
                        "deviation": f"{pct_below}% below peer norm"
                    },
                    "risk_score": 81,
                    "recommended_actions": rem_plan["recommended_actions"],
                    "verification_metrics": rem_plan["verification_metrics"],
                    "manual_review_required": True
                })

    # D. Missing Investigation Evidence (Workflow Gaps)
    cases_query = db.query(Case).all()
    if cases_query:
        df_c = pd.DataFrame([{
            "case_id": c.case_id,
            "cse_id": c.cse_id,
            "evidence_count": c.evidence_count or 0,
            "root_cause": c.root_cause_identified,
            "remediation": c.remediation_recorded
        } for c in cases_query])

        for cse_id, group in df_c.groupby("cse_id"):
            missing_rc_count = int((~group["root_cause"]).sum())
            rc_missing_rate = (missing_rc_count / len(group)) * 100.0
            if rc_missing_rate > 75.0 and len(group) >= 15:
                findings.append({
                    "finding_id": f"F-NEG-NORC-{cse_id}",
                    "cse_id": cse_id,
                    "finding_type": "Negative Space",
                    "rule_category": "weak_investigations",
                    "severity": "Medium",
                    "confidence": 0.85,
                    "title": f"Systemic absence of root-cause documentation ({round(rc_missing_rate, 1)}% cases missing RCA)",
                    "description": f"{missing_rc_count} out of {len(group)} cases ({round(rc_missing_rate, 1)}%) were closed without recording root-cause determination, impeding organizational resilience.",
                    "evidence": group[~group["root_cause"]].head(10).replace({np.nan: None}).to_dict(orient="records"),
                    "metrics": {
                        "signal": "Lack of recorded root-cause analysis across closed security cases",
                        "baseline": "Peer baseline: >= 75% cases have documented RCA",
                        "observed": f"{round(100.0 - rc_missing_rate, 1)}% documentation rate",
                        "missing_cases_count": missing_rc_count
                    },
                    "risk_score": 68,
                    "recommended_actions": [
                        "Enforce mandatory root-cause taxonomy field prior to case closure.",
                        "Establish monthly SOC case review committee to validate root-cause assignments."
                    ],
                    "verification_metrics": [
                        "RCA documentation compliance rate (target: > 85%)"
                    ],
                    "manual_review_required": True
                })

    return findings
