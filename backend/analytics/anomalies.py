import numpy as np
import pandas as pd
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

def run_local_anomaly_detection(db: Session, benchmarks: dict) -> List[Dict[str, Any]]:
    """
    Executes an offline, local Isolation Forest model to detect multivariate operational anomalies across CSEs.
    Runs entirely on local CPU with zero cloud/external API dependencies.
    """
    entity_metrics = benchmarks.get("entity_metrics", {})
    if len(entity_metrics) < 4:
        return []

    cids = list(entity_metrics.keys())
    feature_matrix = []

    # Features:
    # 0: crit_median_dur
    # 1: crit_esc_rate
    # 2: telemetry_coverage
    # 3: avg_evidence
    # 4: repeated_rate
    # 5: all_median_dur
    for cid in cids:
        m = entity_metrics[cid]
        feature_matrix.append([
            m.get("crit_median_dur", 50.0),
            m.get("crit_esc_rate", 80.0),
            m.get("telemetry_coverage", 95.0),
            m.get("avg_evidence", 3.0),
            m.get("repeated_rate", 5.0),
            m.get("all_median_dur", 25.0)
        ])

    X = np.array(feature_matrix)
    
    # Train local Isolation Forest (deterministic seed)
    clf = IsolationForest(contamination=0.25, random_state=42, n_estimators=50)
    preds = clf.fit_predict(X)
    scores = clf.decision_function(X) # lower score = more anomalous

    anomalies = []
    for idx, (cid, pred, score) in enumerate(zip(cids, preds, scores)):
        if pred == -1: # flagged as anomaly
            m = entity_metrics[cid]
            # Normalize anomaly score to 0-100 scale where higher is more anomalous
            norm_anomaly_score = round(float((0.2 - score) * 200.0), 1)
            norm_anomaly_score = max(55.0, min(95.0, norm_anomaly_score))

            # Explain which features contributed most to anomaly
            contributions = []
            if m.get("crit_median_dur", 50) < 18:
                contributions.append("Abnormally low critical closure duration")
            if m.get("crit_esc_rate", 80) < 40:
                contributions.append("Severely depressed critical escalation rate")
            if m.get("telemetry_coverage", 95) < 70:
                contributions.append("Degraded telemetry coverage")
            if m.get("repeated_rate", 5) > 15:
                contributions.append("Elevated repeat alert clustering")

            anomalies.append({
                "finding_id": f"F-ML-ANOM-{cid}",
                "cse_id": cid,
                "finding_type": "Multivariate Anomaly",
                "rule_category": "multivariate_anomaly",
                "severity": "High" if norm_anomaly_score > 75 else "Medium",
                "confidence": round(0.75 + (norm_anomaly_score / 400.0), 2),
                "title": f"Multivariate operational pattern deviation (Isolation Forest Score: {norm_anomaly_score})",
                "description": f"Local unsupervised Isolation Forest detected significant multi-dimensional divergence from peer operational patterns. Principal contributing signals: {', '.join(contributions) if contributions else 'Non-linear correlation deviation'}.",
                "evidence": [{
                    "feature": "Critical Closure Median", "entity_value": f"{m.get('crit_median_dur')}m",
                }, {
                    "feature": "Critical Escalation Rate", "entity_value": f"{m.get('crit_esc_rate')}%",
                }, {
                    "feature": "Telemetry Coverage", "entity_value": f"{m.get('telemetry_coverage')}%",
                }, {
                    "feature": "Repeat Alert Rate", "entity_value": f"{m.get('repeated_rate')}%"
                }],
                "metrics": {
                    "model": "Local Scikit-Learn IsolationForest (n_estimators=50)",
                    "raw_decision_score": round(float(score), 4),
                    "anomaly_intensity": norm_anomaly_score,
                    "top_drivers": contributions
                },
                "risk_score": norm_anomaly_score,
                "recommended_actions": [
                    "Conduct comprehensive holistic SOC assessment.",
                    "Validate telemetry integrity and escalation governance with entity technical lead."
                ],
                "verification_metrics": [
                    "Supervisory comprehensive audit review completion"
                ],
                "manual_review_required": True
            })

    return anomalies
