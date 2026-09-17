import random
import datetime
from sqlalchemy.orm import Session
from ..database.models import CSE, Asset, Alert, Case, Escalation, Telemetry, GroundTruth, AuditLog

SECTORS = [
    "Power & Energy",
    "Banking & Financial",
    "Telecommunications",
    "Transportation",
    "Strategic & Defence",
    "Healthcare & Life Sciences"
]

ALERT_CATEGORIES = [
    "Ransomware Precursor",
    "Lateral Movement",
    "Privilege Escalation",
    "Data Exfiltration",
    "Brute Force Authentication",
    "Command & Control (C2)",
    "DDoS & Traffic Anomaly",
    "Suspicious PowerShell Execution",
    "Unauthorized Configuration Change",
    "SCADA Protocol Deviation"
]

SOURCES = ["EDR - Sentinel", "SIEM - Splunk", "NIDS - Suricata", "Firewall - PaloAlto", "WAF - Cloudflare", "OT-Inspector"]

CSE_DEFINITIONS = [
    {"id": "CSE-01", "name": "Reserve Financial Clearing Corp", "sector": "Banking & Financial", "criticality": "Level 1", "profile": "healthy"},
    {"id": "CSE-02", "name": "National Telecom Backbone Network", "sector": "Telecommunications", "criticality": "Level 1", "profile": "healthy"},
    {"id": "CSE-03", "name": "Strategic Defence Avionics Grid", "sector": "Strategic & Defence", "criticality": "Level 1", "profile": "low_activity"},
    {"id": "CSE-04", "name": "Metropolitan Rail Traffic Control", "sector": "Transportation", "criticality": "Level 2", "profile": "weak_investigations"},
    {"id": "CSE-05", "name": "Hydrocarbon Pipeline Trans-Grid", "sector": "Power & Energy", "criticality": "Level 2", "profile": "telemetry_gaps"},
    {"id": "CSE-06", "name": "Federal Revenue & Customs Gateway", "sector": "Banking & Financial", "criticality": "Level 2", "profile": "repeated_alerts"},
    {"id": "CSE-07", "name": "Northern Regional Load Despatch (NRLDC)", "sector": "Power & Energy", "criticality": "Level 1", "profile": "star_demo_problematic"},
    {"id": "CSE-08", "name": "Deepwater Container Terminal Systems", "sector": "Transportation", "criticality": "Level 2", "profile": "healthy"},
    {"id": "CSE-09", "name": "Civil Aviation En-Route Radar Network", "sector": "Transportation", "criticality": "Level 1", "profile": "missing_categories"},
    {"id": "CSE-10", "name": "National Biomedical Vaccine Repository", "sector": "Healthcare & Life Sciences", "criticality": "Level 2", "profile": "repetitive_notes"},
    {"id": "CSE-11", "name": "State Electricity Distribution Corp", "sector": "Power & Energy", "criticality": "Level 2", "profile": "healthy"},
    {"id": "CSE-12", "name": "Interbank Payment Gateway Interface", "sector": "Banking & Financial", "criticality": "Level 1", "profile": "healthy"},
]

TEMPLATE_NOTES_LIST = [
    "Standard alert review completed. System verified normal. Log verified with perimeter switch. No anomaly observed.",
    "Alert triaged according to standard operating procedure. Endpoint checked. No malicious persistence identified. Incident marked benign.",
    "Automated ticket closed per protocol. IP address checked against local whitelist. No further action deemed necessary by tier 1 analyst.",
    "Telemetry sampled for 15-minute window. CPU and memory metrics normal. Rule matched benign scheduled task.",
]

GENUINE_NOTES_LIST = [
    "Detailed triage initiated following anomalous outbound connection. Memory dump captured from endpoint. Discovered staged payload in AppData/Local/Temp. Hash queried on VirusTotal; host isolated from VLAN 40. Firewall drop rule implemented for external C2 IP 185.220.101.5. Escalated to IR Lead for forensic analysis.",
    "Investigated credential dumping attempt via LSASS process injection. Kerberos ticket-granting anomalies correlated in domain controller logs. Affected domain admin account disabled; password rotation forced enterprise-wide. Remediation confirmed in ticket SEC-4912.",
    "Reviewed suspicious PowerShell download cradle executing base64 encoded command. Deobfuscated command revealed attempted reconnaissance via whoami and net user. Scheduled task created by attacker removed. EDR policy updated to block unquoted service paths.",
    "Analysis of lateral movement alert across industrial subnet. Source workstation authenticated to PLC engineering station via unauthorized SMB. Network micro-segmentation rule enforced. Root cause identified as unpatched CVE-2023-38545.",
    "False positive investigation. Correlated automated vulnerability scanner activity from authorized internal IP 10.20.1.15 running weekly scheduled scan. Scanner credentials validated against change request CR-8831. Added temporary alert suppression rule for 48 hours."
]

def generate_synthetic_dataset(db: Session, target_alert_count: int = 16000) -> dict:
    random.seed(42)
    start_date = datetime.datetime(2026, 6, 1, 0, 0, 0)
    reporting_period = "2026-Q3 (Jun-Aug 2026)"

    # Clear existing data
    db.query(GroundTruth).delete()
    db.query(Telemetry).delete()
    db.query(Escalation).delete()
    db.query(Case).delete()
    db.query(Alert).delete()
    db.query(Asset).delete()
    db.query(CSE).delete()
    db.commit()

    cses = []
    assets_all = []
    ground_truths = []

    # 1. Create CSEs and Assets
    for cse_def in CSE_DEFINITIONS:
        cse = CSE(
            cse_id=cse_def["id"],
            cse_name=cse_def["name"],
            sector=cse_def["sector"],
            criticality=cse_def["criticality"],
            reporting_period=reporting_period,
            attention_score=0.0,
            review_status="Pending Review"
        )
        db.add(cse)
        cses.append(cse)

        # Assets per CSE
        asset_count = 35 if cse_def["criticality"] == "Level 1" else 20
        if cse_def["profile"] == "low_activity":
            asset_count = 42 # Highlight discrepancy: lots of assets, very low alerts

        for a_idx in range(1, asset_count + 1):
            if "Power" in cse_def["sector"]:
                asset_type = random.choice(["SCADA Master RTU", "Substation Controller", "HMI Gateway", "Historian DB", "Core Router"])
            elif "Banking" in cse_def["sector"]:
                asset_type = random.choice(["Core Banking DB", "SWIFT Gateway", "HSM Cluster", "Active Directory DC", "Transaction API"])
            elif "Telecom" in cse_def["sector"]:
                asset_type = random.choice(["BGP Core Router", "HLR/HSS Node", "Billing DB Server", "AAA Radius Server", "DNS Resolver"])
            else:
                asset_type = random.choice(["Domain Controller", "Database Cluster", "Web Application Gateway", "Core Switch", "Engineering Workstation"])

            crit = "Critical" if a_idx <= 8 else ("High" if a_idx <= 18 else "Medium")
            
            # Telemetry profile
            tel_expected = random.randint(900, 1000)
            tel_received = int(tel_expected * random.uniform(0.92, 0.99))

            # Problematic entities telemetry gaps
            if cse_def["profile"] == "star_demo_problematic" and a_idx in [1, 2, 3]: # 3 Critical SCADA assets with telemetry blind spot
                tel_received = int(tel_expected * random.uniform(0.02, 0.12))
            elif cse_def["profile"] == "telemetry_gaps" and a_idx in [1, 2, 4, 5, 6]:
                tel_received = int(tel_expected * random.uniform(0.10, 0.25))

            asset = Asset(
                asset_id=f"{cse_def['id']}-AST-{a_idx:03d}",
                cse_id=cse_def["id"],
                asset_name=f"{cse_def['id']} {asset_type} #{a_idx}",
                asset_type=asset_type,
                criticality=crit,
                telemetry_expected=tel_expected,
                telemetry_received=tel_received
            )
            db.add(asset)
            assets_all.append(asset)

            # Telemetry record
            coverage = round((tel_received / tel_expected) * 100.0, 1)
            telemetry_row = Telemetry(
                cse_id=cse_def["id"],
                asset_id=asset.asset_id,
                period=reporting_period,
                telemetry_expected=tel_expected,
                telemetry_received=tel_received,
                coverage_percentage=coverage
            )
            db.add(telemetry_row)

    db.commit()

    # Ground truth recordings
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-001",
        cse_id="CSE-07",
        finding_type="Execution Gap",
        rule_category="fast_closure_critical",
        title="Critical alerts closed abnormally fast (<10 min vs peer 48 min)",
        expected_flag=True,
        rationale="CSE-07 closed 18 critical alerts within 6-9 minutes without documented forensic validation."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-002",
        cse_id="CSE-07",
        finding_type="Execution Gap",
        rule_category="unescalated_critical",
        title="Critical alerts without escalation record",
        expected_flag=True,
        rationale="14 critical alerts on SCADA & Historian assets had no escalation to Tier 2 / Incident Response."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-003",
        cse_id="CSE-07",
        finding_type="Negative Space",
        rule_category="telemetry_gap",
        title="Critical SCADA RTUs with <15% telemetry received",
        expected_flag=True,
        rationale="Three Tier-1 critical SCADA RTUs (AST-001, AST-002, AST-003) generated under 12% expected telemetry."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-004",
        cse_id="CSE-07",
        finding_type="Execution Gap",
        rule_category="repeated_alerts_no_remediation",
        title="Recurring alert pattern without root-cause remediation",
        expected_flag=True,
        rationale="27 repeated SCADA protocol deviation alerts on AST-004 without root-cause remediation recorded."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-005",
        cse_id="CSE-07",
        finding_type="Execution Gap",
        rule_category="repetitive_investigation_notes",
        title="High textual similarity / template-like investigation notes",
        expected_flag=True,
        rationale="Over 75% of investigation notes are near-identical canned copy-paste text."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-006",
        cse_id="CSE-07",
        finding_type="Negative Space",
        rule_category="missing_alert_category",
        title="Potential detection coverage gap: Zero lateral movement alerts",
        expected_flag=True,
        rationale="Absence of Lateral Movement and Ransomware detection categories across 3 months."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-007",
        cse_id="CSE-03",
        finding_type="Negative Space",
        rule_category="unusually_low_activity",
        title="Anomalously low alert activity relative to critical asset inventory",
        expected_flag=True,
        rationale="CSE-03 generated 78% fewer alerts than peer median despite 42 critical defence assets."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-008",
        cse_id="CSE-04",
        finding_type="Execution Gap",
        rule_category="weak_investigations",
        title="Acknowledged but weakly investigated alerts with zero evidence",
        expected_flag=True,
        rationale="Over 45 cases marked closed with 0 evidence attached and missing root cause."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-009",
        cse_id="CSE-05",
        finding_type="Negative Space",
        rule_category="telemetry_gap",
        title="Telemetry gap on pipeline pump telemetry nodes",
        expected_flag=True,
        rationale="5 critical pipeline controller assets show below 25% telemetry coverage."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-010",
        cse_id="CSE-09",
        finding_type="Negative Space",
        rule_category="missing_alert_category",
        title="Absence of Brute Force / Authentication telemetry alerts",
        expected_flag=True,
        rationale="Zero brute force alerts detected across the entire aviation radar perimeter."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-011",
        cse_id="CSE-10",
        finding_type="Execution Gap",
        rule_category="repetitive_investigation_notes",
        title="Repetitive investigation descriptions across analyst shifts",
        expected_flag=True,
        rationale="Template investigation text reused across 60+ cases."
    ))
    ground_truths.append(GroundTruth(
        ground_truth_id="GT-012",
        cse_id="CSE-06",
        finding_type="Execution Gap",
        rule_category="repeated_alerts_no_remediation",
        title="Repeated database alerts without remediation",
        expected_flag=True,
        rationale="18 recurring SQL injection precursor alerts on DB-002 without remediation ticket."
    ))

    # Add negative ground truth controls (healthy entities that should NOT be flagged)
    for healthy_id in ["CSE-01", "CSE-02", "CSE-08", "CSE-12"]:
        ground_truths.append(GroundTruth(
            ground_truth_id=f"GT-CTRL-{healthy_id}-1",
            cse_id=healthy_id,
            finding_type="Execution Gap",
            rule_category="fast_closure_critical",
            title=f"Control: {healthy_id} normal critical closure duration",
            expected_flag=False,
            rationale=f"{healthy_id} exhibits thorough mean investigation times exceeding peer median."
        ))
        ground_truths.append(GroundTruth(
            ground_truth_id=f"GT-CTRL-{healthy_id}-2",
            cse_id=healthy_id,
            finding_type="Negative Space",
            rule_category="telemetry_gap",
            title=f"Control: {healthy_id} robust telemetry health",
            expected_flag=False,
            rationale=f"{healthy_id} maintains >95% telemetry across all critical assets."
        ))

    for gt in ground_truths:
        db.add(gt)
    db.commit()

    # 2. Generate Alerts & Cases
    alerts_to_insert = []
    cases_to_insert = []
    escalations_to_insert = []

    # Map assets by CSE
    cse_assets_map = {}
    for a in assets_all:
        cse_assets_map.setdefault(a.cse_id, []).append(a)

    alert_counter = 1
    case_counter = 1
    escalation_counter = 1

    for cse_def in CSE_DEFINITIONS:
        cid = cse_def["id"]
        profile = cse_def["profile"]
        assets = cse_assets_map[cid]

        # Target alert volume for this CSE
        if profile == "low_activity":
            n_alerts = random.randint(320, 480) # Significantly low!
        elif profile == "star_demo_problematic":
            n_alerts = random.randint(1800, 2200) # High volume with gaps
        elif cse_def["criticality"] == "Level 1":
            n_alerts = random.randint(1600, 2100)
        else:
            n_alerts = random.randint(1100, 1500)

        # Star demo repeated alerts target asset
        star_repeat_asset = assets[3].asset_id if len(assets) > 3 else assets[0].asset_id

        for _ in range(n_alerts):
            # Timestamp over 90 days
            day_offset = random.randint(0, 89)
            second_offset = random.randint(0, 86399)
            alert_time = start_date + datetime.timedelta(days=day_offset, seconds=second_offset)

            # Severity distribution
            if profile == "star_demo_problematic":
                # Higher critical/high proportion
                severity = random.choices(["Critical", "High", "Medium", "Low"], weights=[0.14, 0.32, 0.38, 0.16])[0]
            else:
                severity = random.choices(["Critical", "High", "Medium", "Low"], weights=[0.05, 0.20, 0.50, 0.25])[0]

            # Categories
            if profile == "star_demo_problematic":
                # Exclude Lateral Movement and Ransomware Precursor to simulate negative space!
                available_cats = [c for c in ALERT_CATEGORIES if c not in ["Lateral Movement", "Ransomware Precursor"]]
            elif profile == "missing_categories":
                # Exclude Brute Force Authentication
                available_cats = [c for c in ALERT_CATEGORIES if c != "Brute Force Authentication"]
            else:
                available_cats = ALERT_CATEGORIES

            category = random.choice(available_cats)

            # Asset selection
            if profile == "star_demo_problematic" and random.random() < 0.12:
                # Direct to repeated asset for recurrence pattern
                selected_asset = star_repeat_asset
                category = "SCADA Protocol Deviation"
            elif profile == "repeated_alerts" and random.random() < 0.10:
                selected_asset = assets[1].asset_id
                category = "Suspicious PowerShell Execution"
            else:
                selected_asset = random.choice(assets).asset_id

            # Ack and Investigation timelines
            ack_delay_mins = random.uniform(2.0, 18.0)
            ack_time = alert_time + datetime.timedelta(minutes=ack_delay_mins)

            inv_start_delay = random.uniform(1.0, 15.0)
            inv_start_time = ack_time + datetime.timedelta(minutes=inv_start_delay)

            # Closure duration
            if profile == "star_demo_problematic" and severity in ["Critical", "High"]:
                # Abnormally fast closure for high/critical: 5 to 11 minutes!
                dur_minutes = round(random.uniform(5.2, 11.4), 1)
            elif profile == "weak_investigations" and random.random() < 0.40:
                dur_minutes = round(random.uniform(4.0, 9.0), 1)
            elif severity == "Critical":
                # Healthy peer median for critical is ~45-65 mins
                dur_minutes = round(random.uniform(38.0, 75.0), 1)
            elif severity == "High":
                dur_minutes = round(random.uniform(28.0, 52.0), 1)
            else:
                dur_minutes = round(random.uniform(12.0, 35.0), 1)

            closed_time = inv_start_time + datetime.timedelta(minutes=dur_minutes)

            # Escalation
            escalated = False
            esc_level = "None"
            if severity == "Critical":
                if profile == "star_demo_problematic":
                    # Only escalate 15% of criticals! (85% unescalated gap)
                    escalated = random.random() < 0.15
                else:
                    # Healthy entities escalate 85%+ of criticals
                    escalated = random.random() < 0.88
                esc_level = "L3 (Incident Response)" if escalated else "None"
            elif severity == "High":
                if profile == "star_demo_problematic":
                    escalated = random.random() < 0.25
                else:
                    escalated = random.random() < 0.65
                esc_level = "L2 (Senior Analyst)" if escalated else "None"

            # Case association: ~25% of alerts get elevated to formal Case
            has_case = (severity in ["Critical", "High"]) or (random.random() < 0.15)
            cid_str = f"CASE-{case_counter:05d}" if has_case else None

            alert_id_str = f"ALT-{alert_counter:06d}"
            alert = Alert(
                alert_id=alert_id_str,
                cse_id=cid,
                asset_id=selected_asset,
                timestamp=alert_time,
                severity=severity,
                category=category,
                source=random.choice(SOURCES),
                acknowledged_at=ack_time,
                investigation_started_at=inv_start_time,
                closed_at=closed_time,
                duration_minutes=dur_minutes,
                disposition="True Positive" if (escalated or severity == "Critical") else random.choice(["False Positive", "Benign", "Policy Exception"]),
                case_id=cid_str,
                escalated=escalated,
                escalation_level=esc_level
            )
            alerts_to_insert.append(alert)
            alert_counter += 1

            if has_case:
                # Case attributes
                if profile == "star_demo_problematic":
                    notes = random.choice(TEMPLATE_NOTES_LIST)
                    ev_count = random.choice([0, 1])
                    root_cause = False if random.random() < 0.85 else True
                    remediation = False if (selected_asset == star_repeat_asset or random.random() < 0.80) else True
                    closure_reason = "Quick Closed - Policy Presumption"
                elif profile == "repetitive_notes":
                    notes = random.choice(TEMPLATE_NOTES_LIST)
                    ev_count = random.randint(1, 3)
                    root_cause = random.random() < 0.50
                    remediation = random.random() < 0.50
                    closure_reason = "Standard SOP Handled"
                elif profile == "weak_investigations":
                    notes = "Basic triage executed. No logs requested."
                    ev_count = 0
                    root_cause = False
                    remediation = False
                    closure_reason = "Closed without escalation"
                else:
                    notes = random.choice(GENUINE_NOTES_LIST)
                    ev_count = random.randint(2, 7)
                    root_cause = random.random() < 0.85
                    remediation = random.random() < 0.80
                    closure_reason = "Remediated & Verified" if remediation else "Documented & Mitigated"

                case_obj = Case(
                    case_id=cid_str,
                    cse_id=cid,
                    alert_id=alert_id_str,
                    opened_at=alert_time,
                    assigned_at=ack_time,
                    investigation_started_at=inv_start_time,
                    closed_at=closed_time,
                    duration_minutes=dur_minutes,
                    root_cause_identified=root_cause,
                    remediation_recorded=remediation,
                    evidence_count=ev_count,
                    investigation_notes=notes,
                    closure_reason=closure_reason
                )
                cases_to_insert.append(case_obj)

                # Escalation record if required
                if severity in ["Critical", "High"]:
                    esc_obj = Escalation(
                        escalation_id=f"ESC-{escalation_counter:05d}",
                        case_id=cid_str,
                        cse_id=cid,
                        severity=severity,
                        escalation_required=True,
                        escalated=escalated,
                        escalation_time=(inv_start_time + datetime.timedelta(minutes=5)) if escalated else None,
                        escalation_level=esc_level
                    )
                    escalations_to_insert.append(esc_obj)
                    escalation_counter += 1

                case_counter += 1

    # Bulk insert for efficiency
    db.bulk_save_objects(alerts_to_insert)
    db.bulk_save_objects(cases_to_insert)
    db.bulk_save_objects(escalations_to_insert)

    # Log audit event
    audit = AuditLog(
        user="System (Synthetic Generator)",
        action="Dataset Generated",
        details=f"Generated {len(cses)} CSEs, {len(assets_all)} assets, {len(alerts_to_insert)} alerts, {len(cases_to_insert)} cases across {reporting_period}."
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "cses_count": len(cses),
        "assets_count": len(assets_all),
        "alerts_count": len(alerts_to_insert),
        "cases_count": len(cases_to_insert),
        "escalations_count": len(escalations_to_insert),
        "reporting_period": reporting_period
    }
