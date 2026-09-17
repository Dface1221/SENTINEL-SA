from typing import Dict, Any, List

REMEDIATION_MAP = {
    "fast_closure_critical": {
        "finding_type": "Execution Gap",
        "impact": "Potentially insufficient investigative diligence prior to disposition of high-consequence critical events.",
        "recommended_actions": [
            "Establish mandatory minimum investigation checklist before critical alert disposition.",
            "Enforce mandatory forensic evidence attachment (e.g., process dump, network flow, auth trace) for all closures.",
            "Introduce supervisor approval or peer review for critical closures under 15 minutes.",
            "Review Tier-1 analyst triage guidelines for high-severity alert escalation thresholds."
        ],
        "verification_metrics": [
            "Critical-alert median investigation duration (target: >= 40 minutes)",
            "Percentage of critical cases with verified forensic evidence attached",
            "Supervisor quality audit pass rate on fast-closed alerts"
        ]
    },
    "unescalated_critical": {
        "finding_type": "Execution Gap",
        "impact": "Potentially insufficient escalation discipline and lack of Tier-2/Incident Response awareness for high-impact threats.",
        "recommended_actions": [
            "Review and recalibrate the operational escalation matrix for Critical and High severity events.",
            "Implement a mandatory escalation decision field with mandatory justification prior to case closure.",
            "Define explicit escalation SLAs (e.g., critical escalation within 15 minutes of acknowledgement).",
            "Establish automated alert notification to Incident Response leads when critical events remain unescalated for > 30 minutes."
        ],
        "verification_metrics": [
            "Critical-alert escalation rate (target: >= 80% escalated or formal exception recorded)",
            "Escalation SLA compliance percentage",
            "Mean time to escalate critical incidents"
        ]
    },
    "repeated_alerts_no_remediation": {
        "finding_type": "Execution Gap",
        "impact": "Operational alert fatigue, chronic recurring vulnerabilities, and lack of permanent root-cause remediation.",
        "recommended_actions": [
            "Conduct structured root-cause analysis (RCA) on assets generating recurring alerts.",
            "Establish a recurring-alert threshold policy (e.g., >= 5 alerts on same asset triggers a Problem Ticket).",
            "Link repetitive alerts to a parent remediation record with designated engineering ownership.",
            "Implement configuration hardening or patch deployment on persistent offending hosts."
        ],
        "verification_metrics": [
            "Repeat alert recurrence reduction percentage (target: >= 70% reduction over 60 days)",
            "Remediation ticket closure rate with engineering sign-off",
            "Mean time to permanent remediation (MTTR)"
        ]
    },
    "repetitive_investigation_notes": {
        "finding_type": "Execution Gap",
        "impact": "Potential operational metric optimization or canned checkbox triage without substantive human analysis.",
        "recommended_actions": [
            "Eliminate generic copy-paste triage templates in case management software.",
            "Require structured investigation fields: affected host, analyzed hash/artifact, network vector, analyst deduction.",
            "Implement weekly random sampling and manual supervisory review of investigation narratives.",
            "Provide refresher training to analysts on artifact-driven incident documentation."
        ],
        "verification_metrics": [
            "Investigation narrative uniqueness ratio (TF-IDF diversity score >= 0.65)",
            "Evidence attachment completeness rate",
            "Root-cause documentation percentage"
        ]
    },
    "weak_investigations": {
        "finding_type": "Execution Gap",
        "impact": "Cases closed without verifiable evidence or root-cause identification, leaving residual compromise risks unaddressed.",
        "recommended_actions": [
            "Enforce mandatory evidence attachment (minimum 1 log/screenshot/pcap) before case closure.",
            "Require explicit root-cause categorization on all closed high/critical cases.",
            "Conduct supervisory audit on all cases closed with zero recorded evidence."
        ],
        "verification_metrics": [
            "Zero-evidence closure rate (target: < 5%)",
            "Documented root-cause rate on closed cases (target: > 85%)"
        ]
    },
    "metric_gaming": {
        "finding_type": "Metric Gaming",
        "impact": "Operational KPI distortion where SLA compliance metrics are maximized at the expense of defensive rigor.",
        "recommended_actions": [
            "Decouple analyst performance appraisal from pure closure velocity KPIs.",
            "Introduce qualitative investigation grading into SOC supervisory evaluation.",
            "Conduct independent supervisory review of high-volume rapid closures."
        ],
        "verification_metrics": [
            "Post-closure incident reopening rate",
            "Supervisory quality audit conformity score"
        ]
    },
    "telemetry_gap": {
        "finding_type": "Negative Space",
        "impact": "Critical monitoring blind spot preventing detection of adversary presence on essential infrastructure assets.",
        "recommended_actions": [
            "Validate physical and logical asset inventory against active SIEM/EDR log sources.",
            "Verify log forwarder agent health, firewall rules, and syslog ingestion pipeline status on flagged hosts.",
            "Implement automated heartbeat monitoring and dead-man alerting for critical asset telemetry.",
            "Record formal supervisory exceptions where telemetry is intentionally air-gapped or unmonitored."
        ],
        "verification_metrics": [
            "Critical asset telemetry coverage percentage (target: >= 95%)",
            "Telemetry freshness and log latency metrics",
            "Zero unmonitored critical assets without approved exception"
        ]
    },
    "missing_alert_category": {
        "finding_type": "Negative Space",
        "impact": "Potential detection coverage void across core MITRE ATT&CK tactic categories observed in comparable peer entities.",
        "recommended_actions": [
            "Audit SIEM and EDR detection rule repository against sector-specific threat profile.",
            "Verify whether relevant log sources (e.g., PowerShell script block, Kerberos, DNS query logs) are ingested.",
            "Conduct purple-team adversary emulation tests targeting the missing threat category.",
            "Tune detection threshold rules to ensure low-and-slow tactics trigger supervisory alerts."
        ],
        "verification_metrics": [
            "MITRE ATT&CK tactic detection coverage ratio",
            "Adversary emulation detection validation rate"
        ]
    },
    "unusually_low_activity": {
        "finding_type": "Negative Space",
        "impact": "Suspicious absence of expected security signals relative to critical infrastructure scale, indicating possible ingestion failure.",
        "recommended_actions": [
            "Audit end-to-end data pipeline from perimeter sensors to central SIEM repository.",
            "Verify network collector uptime and drop-rate statistics.",
            "Review alert suppression rules and global whitelisting filters for inadvertent over-filtering."
        ],
        "verification_metrics": [
            "Normalized alert volume per active monitored asset (target: within 1 standard deviation of peer median)",
            "Sensor ingestion drop-rate (< 0.1%)"
        ]
    }
}

def get_remediation_plan(rule_category: str) -> Dict[str, Any]:
    return REMEDIATION_MAP.get(rule_category, {
        "finding_type": "Supervisory Review",
        "impact": "Operational pattern differs from established sector norms requiring manual validation.",
        "recommended_actions": [
            "Review operational procedures and documentation with CSE SOC management.",
            "Conduct targeted sample review of related incident tickets."
        ],
        "verification_metrics": [
            "Operational conformity index",
            "Supervisory audit sign-off"
        ]
    })
