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

import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)


class LogSearch(CodedTool):
    """
    CodedTool implementation that searches the OpsPilot log files.
    """

    def __init__(self, logs_directory: Union[str, Path, None] = None):
        """
        Constructs a log search tool.
        :param logs_directory: Directory containing log files. Defaults to the
                repository's OpsPilot log directory.
        """
        self.logs_directory = Path(logs_directory) if logs_directory else Path(__file__).parents[2] / "opspilot_data" / "logs"
        logger.debug("... OpsPilot log search initialized for %s ...", self.logs_directory)

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. The dictionary expects:
                    "query": Text to find in the logs. "search_term" is also
                        accepted for compatibility with callers using that name.
                    "log_file": Optional log filename to search.

        :param sly_data: Private agent-hierarchy data. No keys are expected.

        :return: Matching log entries, or an error message.
        """
        query = args.get("query") or args.get("search_term")
        if not isinstance(query, str) or not query.strip():
            return "Error: No search query provided."

        if not self.logs_directory.is_dir():
            logger.error("OpsPilot log directory does not exist: %s", self.logs_directory)
            return f"Error: Log directory not found: {self.logs_directory}"

        requested_file = args.get("log_file")
        if requested_file:
            log_files = [self.logs_directory / str(requested_file)]
        else:
            log_files = sorted(self.logs_directory.glob("*.log"))

        query_lower = query.casefold()
        matches = []
        for log_file in log_files:
            if not log_file.is_file():
                continue
            try:
                with log_file.open("r", encoding="utf-8") as stream:
                    for line_number, line in enumerate(stream, start=1):
                        if query_lower in line.casefold():
                            matches.append(f"{log_file.name}:{line_number}: {line.rstrip()}")
            except OSError as error:
                logger.warning("Unable to read log file %s: %s", log_file, error)

        if not matches:
            return f"No log entries found for '{query}'."
        return "\n".join(matches)

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method because file scanning is quick.
        """
        return self.invoke(args, sly_data)
