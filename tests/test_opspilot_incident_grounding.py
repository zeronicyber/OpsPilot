import asyncio
import json
import time
from pathlib import Path

import pytest

from coded_tools.opspilot.kb_search import KBSearch
from coded_tools.opspilot.log_search import LogSearch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
INCIDENTS_PATH = REPOSITORY_ROOT / "opspilot_data" / "incidents.json"
LOGS_PATH = REPOSITORY_ROOT / "opspilot_data" / "logs"
KB_PATH = REPOSITORY_ROOT / "opspilot_data" / "kb"

INCIDENT_IDS = [
    "INC008381005",
    "INC008381110",
    "INC008381111",
    "INC008381021",
    "INC008380944",
    "INC008380901",
]


def _grounding_context(incident_id: str) -> str:
    return (
        f"Incident {incident_id}: missing log evidence or missing KB mapping. "
        "Confirm the incident ID is present in incidents.json, operational logs, and KB files."
    )


@pytest.mark.parametrize("incident_id", INCIDENT_IDS)
def test_incident_is_grounded_in_logs_and_kb(incident_id: str):
    """Verify each incident can be grounded locally without an LLM or external API."""
    incidents = json.loads(INCIDENTS_PATH.read_text(encoding="utf-8"))
    incident_records = [record for record in incidents if record.get("incident_id") == incident_id]
    assert incident_records, _grounding_context(incident_id)

    log_search = LogSearch()
    log_search.logs_directory = LOGS_PATH
    log_started = time.perf_counter()
    log_result = asyncio.run(log_search.async_invoke({"query": incident_id}, {}))
    log_elapsed = time.perf_counter() - log_started

    assert isinstance(log_result, str), f"Incident {incident_id}: unexpected log result type"
    assert not log_result.startswith("ERROR TYPE:"), f"Incident {incident_id}: log search exception: {log_result}"
    assert "No matching log entries found" not in log_result, _grounding_context(incident_id)
    assert incident_id in log_result, _grounding_context(incident_id)
    assert log_elapsed < 1, f"Incident {incident_id}: log search exceeded one second ({log_elapsed:.6f}s)"

    kb_search = KBSearch()
    kb_search.kb_directory = KB_PATH
    kb_started = time.perf_counter()
    kb_result = asyncio.run(kb_search.async_invoke({"query": incident_id}, {}))
    kb_elapsed = time.perf_counter() - kb_started

    assert isinstance(kb_result, dict), f"Incident {incident_id}: KB search returned an error: {kb_result}"
    matches = kb_result.get("matches", [])
    assert matches, _grounding_context(incident_id)
    match = matches[0]
    assert match.get("file"), f"Incident {incident_id}: KB filename missing"
    assert match.get("title"), f"Incident {incident_id}: KB title missing"
    assert match.get("root_cause"), f"Incident {incident_id}: KB root cause missing"
    assert match.get("resolution_steps"), f"Incident {incident_id}: KB resolution steps missing"
    assert match.get("validation_checklist"), f"Incident {incident_id}: KB validation checklist missing"
    assert kb_elapsed < 1, f"Incident {incident_id}: KB search exceeded one second ({kb_elapsed:.6f}s)"
