import logging
import re
import time
import traceback
from typing import Any
from typing import Dict
from typing import List
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)


class ResolutionPlanBuilder(CodedTool):
    """Builds recovery and validation actions directly from KB sections."""

    _numbered_item = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")
    _checklist_item = re.compile(r"^\s*-\s*\[[ xX]\]\s+(.*)$")
    _bullet_item = re.compile(r"^\s*[-*]\s+(.*)$")

    @staticmethod
    def _parse_items(value: Any, checklist: bool = False) -> List[str]:
        if not isinstance(value, str) or not value.strip():
            return []

        items: List[str] = []
        current: str | None = None
        for raw_line in value.splitlines():
            line = " ".join(raw_line.strip().split())
            if not line:
                continue

            match = ResolutionPlanBuilder._numbered_item.match(line)
            if match is None and checklist:
                match = ResolutionPlanBuilder._checklist_item.match(line)
                if match is None:
                    match = ResolutionPlanBuilder._bullet_item.match(line)
            if match is not None:
                if current is not None:
                    items.append(current)
                current = match.group(2) if match.re is ResolutionPlanBuilder._numbered_item else match.group(1)
            elif current is not None:
                current = f"{current} {line}"
            elif not checklist:
                current = line

        if current is not None:
            items.append(current)
        return items

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """Build a structured plan without adding or interpreting KB content."""
        start_time = time.perf_counter()
        try:
            arguments = args if isinstance(args, dict) else {}
            incident_id = arguments.get("incident_id", "")
            kb_file = arguments.get("kb_file", "")
            kb_title = arguments.get("kb_title", "")
            resolution_items = self._parse_items(arguments.get("resolution_steps"))
            validation_items = self._parse_items(arguments.get("validation_checklist"), checklist=True)

            missing_information = []
            if not resolution_items:
                missing_information.append("KB resolution steps")
            if not validation_items:
                missing_information.append("KB validation checklist")

            elapsed_seconds = time.perf_counter() - start_time
            if missing_information:
                return {
                    "incident_id": incident_id,
                    "kb_file": kb_file,
                    "kb_title": kb_title,
                    "status": "INSUFFICIENT_EVIDENCE",
                    "missing_information": missing_information,
                    "elapsed_seconds": elapsed_seconds,
                }

            return {
                "incident_id": incident_id,
                "kb_file": kb_file,
                "kb_title": kb_title,
                "status": "READY_FOR_REVIEW",
                "recovery_actions": [
                    {
                        "action_number": index,
                        "action": action,
                        "source": f"{kb_file} Resolution Step #{index}",
                    }
                    for index, action in enumerate(resolution_items, start=1)
                ],
                "validation_actions": [
                    {
                        "validation_number": index,
                        "action": action,
                        "source": f"{kb_file} Validation Checklist #{index}",
                    }
                    for index, action in enumerate(validation_items, start=1)
                ],
                "missing_information": [],
                "elapsed_seconds": elapsed_seconds,
            }
        except Exception as error:
            elapsed_seconds = time.perf_counter() - start_time
            return (
                f"ERROR TYPE: {type(error).__name__}\n"
                f"ERROR: {str(error)}\n"
                f"elapsed_seconds={elapsed_seconds:.6f}\n\n"
                f"TRACEBACK:\n{traceback.format_exc()}"
            )

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """Delegates to synchronous plan construction because it is local and bounded."""
        return self.invoke(args, sly_data)
