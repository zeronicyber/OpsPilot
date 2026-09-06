from pathlib import Path

from coded_tools.opspilot.incident_validator import IncidentValidator


REGISTRY_PATH = Path(__file__).resolve().parents[1] / "registries" / "basic" / "opspilot.hocon"


def test_unknown_incident_cannot_supply_investigation_evidence():
    result = IncidentValidator().invoke({"incident_id": "INC999999999"}, {})

    assert result["valid"] is False
    assert result["incident_record"] is None
    assert result["log_match_count"] == 0
    assert result["log_files"] == []
    for forbidden_key in ("root_cause", "kb_id", "recovery_plan", "status", "confidence"):
        assert forbidden_key not in result
    assert "Grounded" not in result["reason"]
    assert "Resolved" not in result["reason"]


def test_valid_incident_still_has_a_successful_validation_path():
    result = IncidentValidator().invoke({"incident_id": "INC008381021"}, {})

    assert result["valid"] is True
    assert result["incident_found"] is True
    assert result["log_evidence_found"] is True


def test_registry_puts_validation_before_downstream_agents():
    registry = " ".join(REGISTRY_PATH.read_text(encoding="utf-8").split())

    assert '"name": "incident_validator"' in registry
    assert '"class": "coded_tools.opspilot.incident_validator.IncidentValidator"' in registry
    assert '"tools": ["incident_validator", "LogInvestigator"' in registry
    assert "ALWAYS invoke incident_validator first" in registry
    assert "Do not invoke any other agent or tool after validation failure" in registry
