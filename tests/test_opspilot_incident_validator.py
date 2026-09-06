import asyncio
import json
import time
from pathlib import Path

from coded_tools.opspilot.incident_validator import IncidentValidator


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_valid_existing_incident():
    result = asyncio.run(IncidentValidator().async_invoke({"incident_id": "INC008381021"}, {}))

    assert result["valid"] is True
    assert result["incident_id"] == "INC008381021"
    assert result["incident_found"] is True
    assert result["incident_record"]["status"] == "Monitoring"
    assert result["log_evidence_found"] is True
    assert result["log_match_count"] > 0
    assert result["log_files"] == ["sasgrid_metadata.log"]
    assert result["reason"] == "Incident record found."


def test_nonexistent_incident_fails_closed():
    result = IncidentValidator().invoke({"query": "Investigate INC999999999"}, {})

    assert result == {
        "valid": False,
        "incident_id": "INC999999999",
        "incident_found": False,
        "incident_record": None,
        "log_evidence_found": False,
        "log_match_count": 0,
        "log_files": [],
        "reason": "No matching incident record found.",
    }


def test_malformed_id():
    result = IncidentValidator().invoke({"incident_id": "ABC123"}, {})

    assert result["valid"] is False
    assert result["incident_id"] is None
    assert result["reason"] == "Invalid or missing incident ID. Expected format INC followed by 9 digits."


def test_missing_input():
    result = IncidentValidator().invoke({}, {})

    assert result["valid"] is False
    assert result["incident_id"] is None
    assert result["incident_record"] is None


def test_html_wrapped_incident_id():
    result = IncidentValidator().invoke({"query": "<b>inc008381021</b> &amp; investigate"}, {})

    assert result["valid"] is True
    assert result["incident_id"] == "INC008381021"


def test_incident_record_without_log_evidence(tmp_path):
    incidents_path = tmp_path / "incidents.json"
    incidents_path.write_text(
        json.dumps(
            [
                {
                    "incident_id": "INC123456789",
                    "title": "Synthetic test incident",
                    "priority": "P3",
                    "status": "Open",
                    "service": "Test Service",
                }
            ]
        ),
        encoding="utf-8",
    )
    tool = IncidentValidator()
    tool.incidents_path = incidents_path
    tool.logs_directory = tmp_path / "logs"
    tool.logs_directory.mkdir()

    result = tool.invoke({"incident_id": "INC123456789"}, {})

    assert result["valid"] is True
    assert result["incident_found"] is True
    assert result["log_evidence_found"] is False
    assert result["log_match_count"] == 0
    assert result["log_files"] == []


def test_execution_completes_under_one_second():
    started = time.perf_counter()
    result = IncidentValidator().invoke({"incident_id": "INC008381021"}, {})

    assert result["valid"] is True
    assert time.perf_counter() - started < 1
