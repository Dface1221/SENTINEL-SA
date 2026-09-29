from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class CSE(Base):
    __tablename__ = "cses"

    cse_id = Column(String(50), primary_key=True, index=True)
    cse_name = Column(String(100), nullable=False)
    sector = Column(String(50), nullable=False, index=True)  # Power, Banking, Telecom, Transport, Defence
    criticality = Column(String(20), nullable=False)        # Level 1, Level 2, Level 3
    reporting_period = Column(String(50), nullable=False)   # e.g., Q3-2026 / 2026-M06-M08
    attention_score = Column(Float, default=0.0)
    review_status = Column(String(50), default="Pending Review") # Normal, Review Recommended, Elevated Attention, High Priority Review

    # Relationships
    assets = relationship("Asset", back_populates="cse", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="cse", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="cse", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="cse", cascade="all, delete-orphan")
    telemetries = relationship("Telemetry", back_populates="cse", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String(50), primary_key=True, index=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    asset_name = Column(String(100), nullable=False)
    asset_type = Column(String(50), nullable=False)         # SCADA/RTU, Domain Controller, Core Switch, DB Server, Web Gateway
    criticality = Column(String(20), nullable=False)        # Critical, High, Medium, Low
    telemetry_expected = Column(Integer, default=100)       # Expected log events / heartbeat index
    telemetry_received = Column(Integer, default=100)       # Received log events / heartbeat index

    cse = relationship("CSE", back_populates="assets")
    alerts = relationship("Alert", back_populates="asset")


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(50), primary_key=True, index=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    asset_id = Column(String(50), ForeignKey("assets.asset_id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # Critical, High, Medium, Low
    category = Column(String(50), nullable=False, index=True)  # Lateral Movement, Ransomware Precursor, Brute Force, Data Exfiltration, Privilege Escalation, Policy Violation, DDoS
    source = Column(String(50), nullable=False)                # EDR, SIEM, NIDS, Firewall, WAF
    acknowledged_at = Column(DateTime, nullable=True)
    investigation_started_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, default=0.0)
    disposition = Column(String(50), default="False Positive") # True Positive, False Positive, Policy Exception, Benign
    case_id = Column(String(50), nullable=True, index=True)
    escalated = Column(Boolean, default=False)
    escalation_level = Column(String(20), nullable=True)      # L1, L2, L3, None

    cse = relationship("CSE", back_populates="alerts")
    asset = relationship("Asset", back_populates="alerts")


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String(50), primary_key=True, index=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    alert_id = Column(String(50), nullable=True)
    opened_at = Column(DateTime, nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    investigation_started_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, default=0.0)
    root_cause_identified = Column(Boolean, default=False)
    remediation_recorded = Column(Boolean, default=False)
    evidence_count = Column(Integer, default=0)
    investigation_notes = Column(Text, nullable=True)
    closure_reason = Column(String(100), nullable=True)

    cse = relationship("CSE", back_populates="cases")


class Escalation(Base):
    __tablename__ = "escalations"

    escalation_id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), nullable=True, index=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    escalation_required = Column(Boolean, default=True)
    escalated = Column(Boolean, default=False)
    escalation_time = Column(DateTime, nullable=True)
    escalation_level = Column(String(20), nullable=True)


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    asset_id = Column(String(50), ForeignKey("assets.asset_id"), nullable=False, index=True)
    period = Column(String(50), nullable=False)
    telemetry_expected = Column(Integer, default=100)
    telemetry_received = Column(Integer, default=100)
    coverage_percentage = Column(Float, default=100.0)

    cse = relationship("CSE", back_populates="telemetries")


class Finding(Base):
    __tablename__ = "findings"

    finding_id = Column(String(50), primary_key=True, index=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    finding_type = Column(String(50), nullable=False, index=True) # Execution Gap, Negative Space, Anomaly, Metric Gaming
    severity = Column(String(20), nullable=False, index=True)     # Critical, High, Medium, Low
    confidence = Column(Float, default=0.90)                      # 0.0 to 1.0
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence_json = Column(Text, nullable=False)                  # JSON serialized list of record summaries
    metrics_json = Column(Text, nullable=False)                   # JSON serialized metrics (entity vs peer, percentiles, etc.)
    risk_score = Column(Float, default=50.0)                      # Contribution to attention score
    recommended_actions_json = Column(Text, nullable=False)       # JSON serialized recommended corrective actions & verifications
    review_status = Column(String(50), default="New")             # New, Under Review, Confirmed, Dismissed, Requires CSE Clarification
    supervisor_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    cse = relationship("CSE", back_populates="findings")


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    action_id = Column(String(50), primary_key=True, index=True)
    finding_id = Column(String(50), ForeignKey("findings.finding_id"), nullable=True, index=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    owner = Column(String(100), default="CSE SOC Lead")
    due_date = Column(String(50), nullable=True)
    priority = Column(String(20), default="High")                 # Critical, High, Medium, Low
    status = Column(String(50), default="Open")                   # Open, In Progress, Completed, Verification Pending, Closed
    verification_metric = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class GroundTruth(Base):
    __tablename__ = "ground_truth"

    ground_truth_id = Column(String(50), primary_key=True, index=True)
    cse_id = Column(String(50), ForeignKey("cses.cse_id"), nullable=False, index=True)
    finding_type = Column(String(50), nullable=False)
    rule_category = Column(String(50), nullable=False)            # e.g., fast_closure, unescalated_critical, telemetry_gap, etc.
    title = Column(String(255), nullable=False)
    expected_flag = Column(Boolean, default=True)
    rationale = Column(Text, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    user = Column(String(100), default="Supervisor (NCIIPC)")
    action = Column(String(100), nullable=False)                  # Login, Dataset Generated, Analysis Executed, Finding Updated, Remediation Created, Report Generated
    details = Column(Text, nullable=True)
    previous_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), nullable=True)

import hashlib
from sqlalchemy import event

@event.listens_for(AuditLog, 'before_insert')
def receive_before_insert(mapper, connection, target):
    # Fetch the last log entry's hash using a direct SQL execution on the connection
    result = connection.execute(
        mapper.local_table.select().order_by(mapper.local_table.c.id.desc()).limit(1)
    ).first()
    
    prev_hash = result.current_hash if result and result.current_hash else "0" * 64
    target.previous_hash = prev_hash
    
    # Calculate current hash
    data_string = f"{target.timestamp}{target.user}{target.action}{target.details}{prev_hash}"
    target.current_hash = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
