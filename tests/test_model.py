import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# These tests assume train_model.py has already generated the model files.
import lambda_function


def invoke(text):
    return lambda_function.lambda_handler({"incident_text": text}, None)


def test_network_routing():
    result = invoke("Production VPN tunnel is DOWN and remote users cannot reach the application. Many users are impacted.")
    assert result["category"] == "network"
    assert result["assigned_team"] == "network-operations"


def test_security_routing():
    result = invoke("GuardDuty detected credential misuse and unauthorized IAM API calls from an unusual location.")
    assert result["category"] == "security"
    assert result["assigned_team"] == "security-operations"


def test_p1_guardrail():
    result = invoke("Production outage. All users are unable to access the customer portal.")
    assert result["severity"] == "P1"
    assert result["requires_human_review"] is True
