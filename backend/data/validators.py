import pandas as pd
from typing import Dict, Any, List

REQUIRED_ALERT_COLUMNS = ["alert_id", "cse_id", "asset_id", "timestamp", "severity", "category", "source"]
REQUIRED_CASE_COLUMNS = ["case_id", "cse_id", "opened_at", "investigation_notes"]
REQUIRED_ASSET_COLUMNS = ["asset_id", "cse_id", "asset_name", "asset_type", "criticality"]

def validate_alert_records(df: pd.DataFrame) -> Dict[str, Any]:
    missing_cols = [col for col in REQUIRED_ALERT_COLUMNS if col not in df.columns]
    if missing_cols:
        return {"valid": False, "error": f"Missing required columns: {', '.join(missing_cols)}"}
    
    # Check nulls
    null_ids = df["alert_id"].isnull().sum()
    if null_ids > 0:
        return {"valid": False, "error": f"Found {null_ids} records with null alert_id"}

    # Validate severities
    valid_severities = {"Critical", "High", "Medium", "Low"}
    invalid_sev = set(df["severity"].dropna().unique()) - valid_severities
    if invalid_sev:
        return {"valid": False, "error": f"Invalid severities detected: {', '.join(invalid_sev)}"}

    return {
        "valid": True,
        "record_count": len(df),
        "entities_found": int(df["cse_id"].nunique()),
        "categories_found": int(df["category"].nunique())
    }

def validate_asset_records(df: pd.DataFrame) -> Dict[str, Any]:
    missing_cols = [col for col in REQUIRED_ASSET_COLUMNS if col not in df.columns]
    if missing_cols:
        return {"valid": False, "error": f"Missing required columns: {', '.join(missing_cols)}"}
    return {"valid": True, "record_count": len(df)}
