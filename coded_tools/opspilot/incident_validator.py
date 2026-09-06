import html
import json
import re
from pathlib import Path
from typing import Any
from typing import Dict

from neuro_san.interfaces.coded_tool import CodedTool


class IncidentValidator(CodedTool):
    """Validate incident identity against local incident and log sources."""

    incident_pattern = re.compile(r"\bINC\d{9}\b", re.IGNORECASE)
    html_tag_pattern = re.compile(r"<[^>]*>")

    def __init__(self):
        repository_root = Path(__file__).resolve().parents[2]
        self.incidents_path = repository_root / "opspilot_data" / "incidents.json"
        self.logs_directory = repository_root / "opspilot_data" / "logs"

    @classmethod
    def _extract_incident_id(cls, value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        clean_value = cls.html_tag_pattern.sub(" ", html.unescape(value))
        match = cls.incident_pattern.search(clean_value)
        return match.group(0).upper() if match else None

    @staticmethod
    def _invalid_result(incident_id: str | None, reason: str) -> Dict[str, Any]:
        return {
            "valid": False,
            "incident_id": incident_id,
            "incident_found": False,
            "incident_record": None,
            "log_evidence_found": False,
            "log_match_count": 0,
            "log_files": [],
            "reason": reason,
        }

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return deterministic validation data from local repository sources."""
        arguments = args if isinstance(args, dict) else {}
        requested_value = arguments.get("incident_id") or arguments.get("query")
        incident_id = self._extract_incident_id(requested_value)
        if incident_id is None:
            return self._invalid_result(
                None,
                "Invalid or missing incident ID. Expected format INC followed by 9 digits.",
            )

        try:
            incident_data = json.loads(self.incidents_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            return self._invalid_result(incident_id, "Incident repository could not be read safely.")

        if not isinstance(incident_data, list):
            return self._invalid_result(incident_id, "Incident repository has an invalid format.")

        incident_record = next(
            (
                record
                for record in incident_data
                if isinstance(record, dict)
                and str(record.get("incident_id", "")).casefold() == incident_id.casefold()
            ),
            None,
        )
        if incident_record is None:
            return self._invalid_result(incident_id, "No matching incident record found.")

        log_match_count = 0
        log_files = []
        incident_regex = re.compile(re.escape(incident_id), re.IGNORECASE)
        for log_file in sorted(self.logs_directory.glob("*.log")):
            if not log_file.is_file():
                continue
            try:
                file_match_count = 0
                with log_file.open("r", encoding="utf-8", errors="replace") as stream:
                    for line in stream:
                        file_match_count += len(incident_regex.findall(line))
                if file_match_count:
                    log_match_count += file_match_count
                    log_files.append(log_file.name)
            except OSError:
                continue

        return {
            "valid": True,
            "incident_id": incident_id,
            "incident_found": True,
            "incident_record": incident_record,
            "log_evidence_found": log_match_count > 0,
            "log_match_count": log_match_count,
            "log_files": log_files,
            "reason": "Incident record found.",
        }

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.invoke(args, sly_data)
