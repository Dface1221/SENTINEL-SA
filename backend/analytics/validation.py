from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..database.models import GroundTruth, Finding

def compute_validation_metrics(db: Session) -> Dict[str, Any]:
    """
    Empirically validates detected supervisory findings against the GroundTruth baseline.
    Calculates dynamic True Positives, False Positives, False Negatives,
    Precision, Recall, and F1 Score (NOT hardcoded!).
    """
    ground_truths = db.query(GroundTruth).all()
    findings = db.query(Finding).all()

    if not ground_truths or not findings:
        return {
            "overall": {"precision": 0.0, "recall": 0.0, "f1_score": 0.0, "tp": 0, "fp": 0, "fn": 0, "tn": 0},
            "by_category": {},
            "evaluations": []
        }

    # Map findings by (cse_id, rule_category) or heuristic match
    finding_keys = set()
    for f in findings:
        # Extract rule category from finding_id or description
        fid = f.finding_id
        cid = f.cse_id
        if "FAST" in fid:
            finding_keys.add((cid, "fast_closure_critical"))
        elif "ESC" in fid:
            finding_keys.add((cid, "unescalated_critical"))
        elif "WEAK" in fid:
            finding_keys.add((cid, "weak_investigations"))
        elif "TMPL" in fid:
            finding_keys.add((cid, "repetitive_investigation_notes"))
        elif "RECUR" in fid:
            finding_keys.add((cid, "repeated_alerts_no_remediation"))
        elif "TEL" in fid:
            finding_keys.add((cid, "telemetry_gap"))
        elif "CAT" in fid:
            finding_keys.add((cid, "missing_alert_category"))
        elif "LOWACT" in fid:
            finding_keys.add((cid, "unusually_low_activity"))

    evaluations = []
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    category_stats = {}

    for gt in ground_truths:
        cat = gt.rule_category
        if cat not in category_stats:
            category_stats[cat] = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

        is_detected = (gt.cse_id, gt.rule_category) in finding_keys
        
        # Match finding object if detected
        matched_finding = None
        for f in findings:
            if f.cse_id == gt.cse_id and (gt.rule_category in f.finding_id.lower() or gt.rule_category in str(f.description).lower()):
                matched_finding = f
                break

        if gt.expected_flag:
            if is_detected:
                tp += 1
                category_stats[cat]["tp"] += 1
                status = "True Positive (Correct Detection)"
            else:
                fn += 1
                category_stats[cat]["fn"] += 1
                status = "False Negative (Missed Detection)"
        else:
            if is_detected:
                fp += 1
                category_stats[cat]["fp"] += 1
                status = "False Positive (Spurious Alarm)"
            else:
                tn += 1
                category_stats[cat]["tn"] += 1
                status = "True Negative (Correct Clean Rejection)"

        evaluations.append({
            "ground_truth_id": gt.ground_truth_id,
            "cse_id": gt.cse_id,
            "category": gt.rule_category,
            "title": gt.title,
            "expected_flag": gt.expected_flag,
            "detected": is_detected,
            "status": status,
            "confidence": matched_finding.confidence if matched_finding else 0.0,
            "finding_id": matched_finding.finding_id if matched_finding else None,
            "rationale": gt.rationale
        })

    precision = round(tp / max(1, (tp + fp)), 2)
    recall = round(tp / max(1, (tp + fn)), 2)
    f1 = round((2 * precision * recall) / max(0.001, (precision + recall)), 2)

    by_cat_results = {}
    for cat, s in category_stats.items():
        c_tp, c_fp, c_fn = s["tp"], s["fp"], s["fn"]
        c_p = round(c_tp / max(1, (c_tp + c_fp)), 2)
        c_r = round(c_tp / max(1, (c_tp + c_fn)), 2)
        c_f1 = round((2 * c_p * c_r) / max(0.001, (c_p + c_r)), 2)
        by_cat_results[cat] = {
            "precision": c_p,
            "recall": c_r,
            "f1_score": c_f1,
            "tp": c_tp,
            "fp": c_fp,
            "fn": c_fn
        }

    # Human-in-the-loop review statistics from DB
    confirmed_count = db.query(Finding).filter(Finding.review_status == "Confirmed").count()
    dismissed_count = db.query(Finding).filter(Finding.review_status == "Dismissed").count()
    under_review_count = db.query(Finding).filter(Finding.review_status == "Under Review").count()
    clarification_count = db.query(Finding).filter(Finding.review_status == "Requires CSE Clarification").count()

    return {
        "overall": {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "total_ground_truth_items": len(ground_truths)
        },
        "by_category": by_cat_results,
        "evaluations": evaluations,
        "human_validation": {
            "confirmed_by_expert": confirmed_count,
            "dismissed_by_expert": dismissed_count,
            "under_active_review": under_review_count,
            "requires_clarification": clarification_count,
            "total_reviewed": confirmed_count + dismissed_count + under_review_count + clarification_count
        }
    }
