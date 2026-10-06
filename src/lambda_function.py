import json
import os
from pathlib import Path
import joblib

MODEL_DIR = Path(os.getenv("MODEL_DIR", "/var/task/models"))
CATEGORY_MODEL = joblib.load(MODEL_DIR / "category_model.joblib")
SEVERITY_MODEL = joblib.load(MODEL_DIR / "severity_model.joblib")

TEAM_MAP = {
    "compute": "cloud-platform",
    "network": "network-operations",
    "database": "database-engineering",
    "security": "security-operations",
    "storage": "cloud-platform",
}

RUNBOOK_MAP = {
    "compute": "Check workload health, scaling activity, CPU, memory, and deployment logs.",
    "network": "Validate load balancer health, routes, DNS, security groups, NACLs, and VPN state.",
    "database": "Review connections, query latency, replication, failover status, and recent schema changes.",
    "security": "Preserve evidence, review CloudTrail or GuardDuty, rotate exposed credentials, and isolate affected resources.",
    "storage": "Check capacity, I/O latency, backup state, throttling, and write errors.",
}

CRITICAL_TERMS = [
    "production outage", "all users", "complete service failure",
    "revenue-impacting", "critical customer path", "possible account compromise",
    "sensitive exports", "primary file system is unavailable", "cannot be served",
    "orders cannot be saved", "unable to access"
]


def guardrail_severity(text, predicted):
    lower = text.lower()
    if any(term in lower for term in CRITICAL_TERMS):
        return "P1"
    return predicted


def lambda_handler(event, context):
    text = event.get("incident_text") or event.get("detail", {}).get("reason", "")
    if not text.strip():
        raise ValueError("incident_text is required")

    category = CATEGORY_MODEL.predict([text])[0]
    cat_conf = float(CATEGORY_MODEL.predict_proba([text]).max())
    raw_severity = SEVERITY_MODEL.predict([text])[0]
    severity = guardrail_severity(text, raw_severity)
    sev_conf = float(SEVERITY_MODEL.predict_proba([text]).max())

    requires_human = severity == "P1" or cat_conf < 0.30
    result = {
        "category": category,
        "category_confidence": round(cat_conf, 4),
        "severity": severity,
        "severity_confidence": round(sev_conf, 4),
        "assigned_team": TEAM_MAP[category],
        "suggested_runbook": RUNBOOK_MAP[category],
        "requires_human_review": requires_human,
        "automation_action": "review" if requires_human else "route"
    }
    return result
