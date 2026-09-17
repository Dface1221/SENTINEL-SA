from .database import engine, Base, SessionLocal, get_db
from .models import CSE, Asset, Alert, Case, Escalation, Telemetry, Finding, RemediationAction, GroundTruth, AuditLog

def init_db():
    Base.metadata.create_all(bind=engine)
