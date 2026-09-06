# Copyright © 2025-2026 Cognizant Technology Solutions Corp, www.cognizant.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# END COPYRIGHT

import asyncio
import tempfile
import time
from pathlib import Path
from unittest import TestCase

from coded_tools.opspilot.log_search import LogSearch


class TestLogSearch(TestCase):
    """Focused tests for the OpsPilot log-search coded tool."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.tool = LogSearch()
        self.tool.logs_directory = self.tmp_path

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_matching_incident_id(self):
        """Searches a direct log file and returns the matching incident line."""
        (self.tmp_path / "sasgrid_metadata.log").write_text(
            "2026-09-03 ERROR incident INC008381005 requires investigation\n",
            encoding="utf-8",
        )

        result = asyncio.run(self.tool.async_invoke({"query": "INC008381005"}, {}))

        self.assertIn("sasgrid_metadata.log:1:", result)
        self.assertIn("INC008381005", result)
        self.assertIn("elapsed_seconds=", result)

    def test_no_match_includes_search_details(self):
        """Reports the query, resolved directory, and searched files when no line matches."""
        (self.tmp_path / "sasgrid_metadata.log").write_text("INFO service is healthy\n", encoding="utf-8")

        result = asyncio.run(self.tool.async_invoke({"query": "INC008381005"}, {}))

        self.assertIn("INC008381005", result)
        self.assertIn(str(self.tmp_path), result)
        self.assertIn("sasgrid_metadata.log", result)
        self.assertIn("No matching log entries found", result)
        self.assertIn("elapsed_seconds=", result)

    def test_search_completes_under_one_second(self):
        """Confirms the bounded direct-file search completes within one second."""
        (self.tmp_path / "sasgrid_metadata.log").write_text("ERROR metadata failure\n", encoding="utf-8")

        start_time = time.perf_counter()
        result = asyncio.run(self.tool.async_invoke({"query": "metadata"}, {}))
        elapsed_seconds = time.perf_counter() - start_time

        self.assertIn("metadata failure", result)
        self.assertLess(elapsed_seconds, 1)
