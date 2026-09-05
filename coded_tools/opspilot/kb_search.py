import logging
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)


class KbSearch(CodedTool):
    """CodedTool implementation that searches OpsPilot knowledge-base runbooks."""

    def __init__(self):
        repository_root = Path(__file__).resolve().parents[2]
        self.kb_directory = repository_root / "opspilot_data" / "kb"
        logger.debug("... OpsPilot KB search initialized for %s ...", self.kb_directory)

    @staticmethod
    def _section(content: str, headings: List[str]) -> str:
        lines = content.splitlines()
        wanted = {heading.casefold() for heading in headings}
        section_lines: List[str] = []
        collecting = False
        for line in lines:
            if line.startswith("## "):
                heading = line[3:].strip().casefold()
                if collecting:
                    break
                collecting = heading in wanted
                continue
            if collecting:
                section_lines.append(line)
        return "\n".join(line.strip() for line in section_lines).strip()

    @staticmethod
    def _title(content: str, fallback: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return fallback

    def _parse_match(self, kb_file: Path, content: str) -> Dict[str, Any]:
        root_cause = self._section(content, ["Root Cause"])
        resolution = self._section(content, ["Resolution Procedure", "Resolution Steps"])
        validation = self._section(content, ["Validation Checklist", "Validation Steps"])
        return {
            "file": kb_file.name,
            "path": str(kb_file),
            "title": self._title(content, kb_file.stem),
            "root_cause": root_cause,
            "resolution_steps": resolution,
            "validation_checklist": validation,
        }

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """Search KB Markdown files by incident ID or keyword."""
        start_time = time.perf_counter()
        try:
            query = args.get("query") if isinstance(args, dict) else None
            if not isinstance(query, str) or not query.strip():
                elapsed_seconds = time.perf_counter() - start_time
                return f"Error: No search query provided. elapsed_seconds={elapsed_seconds:.6f}"

            query = query.strip()
            query_lower = query.casefold()
            kb_files = sorted(
                path for path in self.kb_directory.rglob("*.md") if path.is_file()
            )
            matches = []
            for kb_file in kb_files:
                content = kb_file.read_text(encoding="utf-8", errors="replace")
                if query_lower in content.casefold():
                    matches.append(self._parse_match(kb_file, content))

            elapsed_seconds = time.perf_counter() - start_time
            return {
                "query": query,
                "matches": matches,
                "files_searched": len(kb_files),
                "elapsed_seconds": elapsed_seconds,
            }
        except Exception as error:
            elapsed_seconds = time.perf_counter() - start_time
            return (
                f"ERROR TYPE: {type(error).__name__}\n"
                f"ERROR: {str(error)}\n"
                f"resolved_path={self.kb_directory}\n"
                f"elapsed_seconds={elapsed_seconds:.6f}\n\n"
                f"TRACEBACK:\n{traceback.format_exc()}"
            )

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """Delegates to synchronous KB search because the file scan is bounded and local."""
        return self.invoke(args, sly_data)


KBSearch = KbSearch
