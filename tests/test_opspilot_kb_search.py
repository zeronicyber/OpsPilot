import asyncio
import tempfile
import time
from pathlib import Path
from unittest import TestCase

from coded_tools.opspilot.kb_search import KBSearch


class TestKBSearch(TestCase):
    """Focused tests for the OpsPilot knowledge-base search coded tool."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.tool = KBSearch()
        self.tool.kb_directory = self.tmp_path

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_matching_incident_id_returns_runbook_fields(self):
        (self.tmp_path / "KB-1101.md").write_text(
            "# Jupyter Kernel Startup Failure\n\n"
            "## Root Cause\n\nMissing ipykernel dependency.\n\n"
            "## Resolution Procedure\n\n1. Install ipykernel.\n2. Restart Jupyter.\n",
            encoding="utf-8",
        )
        (self.tmp_path / "KB-1101.meta.md").write_text(
            "Maps to INC008381110\n",
            encoding="utf-8",
        )

        result = asyncio.run(self.tool.async_invoke({"query": "INC008381110"}, {}))

        self.assertEqual(len(result["matches"]), 1)
        match = result["matches"][0]
        self.assertEqual(match["file"], "KB-1101.meta.md")
        self.assertEqual(match["title"], "KB-1101.meta")
        self.assertEqual(match["root_cause"], "")

    def test_keyword_search_extracts_title_root_cause_and_resolution(self):
        (self.tmp_path / "KB-1111.md").write_text(
            "# Python Batch Scoring Job Failure\n\n"
            "## Root Cause\n\nModel registry unavailable.\n\n"
            "## Resolution Steps\n\n1. Restart registry service.\n2. Rerun scoring.\n",
            encoding="utf-8",
        )

        result = asyncio.run(self.tool.async_invoke({"query": "registry"}, {}))

        match = result["matches"][0]
        self.assertEqual(match["title"], "Python Batch Scoring Job Failure")
        self.assertIn("Model registry unavailable", match["root_cause"])
        self.assertIn("Restart registry service", match["resolution_steps"])

    def test_no_match_returns_search_metadata(self):
        (self.tmp_path / "KB-1023.md").write_text("# Metadata Runbook\n", encoding="utf-8")

        result = asyncio.run(self.tool.async_invoke({"query": "INC999999999"}, {}))

        self.assertEqual(result["matches"], [])
        self.assertEqual(result["files_searched"], 1)
        self.assertEqual(result["query"], "INC999999999")

    def test_search_completes_under_one_second(self):
        for index in range(20):
            (self.tmp_path / f"KB-{index:04d}.md").write_text(
                f"# Runbook {index}\n\n## Root Cause\n\nCause {index}.\n",
                encoding="utf-8",
            )

        start_time = time.perf_counter()
        result = asyncio.run(self.tool.async_invoke({"query": "Cause 19"}, {}))
        elapsed_seconds = time.perf_counter() - start_time

        self.assertEqual(len(result["matches"]), 1)
        self.assertLess(elapsed_seconds, 1)
        self.assertLess(result["elapsed_seconds"], 1)
