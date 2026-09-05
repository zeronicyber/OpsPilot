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
import time
import traceback
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Union

from neuro_san.interfaces.coded_tool import CodedTool

logger = logging.getLogger(__name__)


class LogSearch(CodedTool):
    """
    CodedTool implementation that searches the SAS Grid metadata log.
    """

    def __init__(self):
        """
        Constructs a log search tool.
        """
        repository_root = Path(__file__).resolve().parents[2]
        self.logs_directory = repository_root / "opspilot_data" / "logs"
        logger.debug("... OpsPilot log search initialized for %s ...", self.logs_directory)

    def invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        :param args: An argument dictionary whose keys are the parameters
                to the coded tool and whose values are the values passed for them
                by the calling agent. The dictionary expects:
                    "query": Text to find in the log. "search_term" is also
                        accepted for compatibility with callers using that name.

        :param sly_data: Private agent-hierarchy data. No keys are expected.

        :return: Matching log entries, or an error message.
        """
        start_time = time.perf_counter()
        try:
            query = args.get("query") or args.get("search_term")
            logger.debug("Current working directory: %s", Path.cwd())
            logger.debug("Query value received: %r", query)
            if not isinstance(query, str) or not query.strip():
                elapsed_seconds = time.perf_counter() - start_time
                return f"Error: No search query provided. elapsed_seconds={elapsed_seconds:.6f}"

            log_files = sorted(
                path for path in self.logs_directory.iterdir() if path.is_file() and path.suffix == ".log"
            )
            files_searched = [path.name for path in log_files]
            logger.debug("Log files being searched: %s", files_searched)
            query_lower = query.casefold()
            matches = []
            for log_file in log_files:
                with log_file.open("r", encoding="utf-8", errors="replace") as stream:
                    for line_number, line in enumerate(stream, start=1):
                        if query_lower in line.casefold():
                            matches.append(f"{log_file.name}:{line_number}: {line.rstrip()}")
                            if len(matches) == 25:
                                break
                if len(matches) == 25:
                    break

            elapsed_seconds = time.perf_counter() - start_time
            if not matches:
                return (
                    f"query={query!r}\n"
                    f"resolved_logs_directory={self.logs_directory}\n"
                    f"files_searched={files_searched}\n"
                    f"No matching log entries found\n"
                    f"elapsed_seconds={elapsed_seconds:.6f}"
                )
            return f"elapsed_seconds={elapsed_seconds:.6f}\n" + "\n".join(matches)
        except Exception as error:
            elapsed_seconds = time.perf_counter() - start_time
            return (
                f"ERROR TYPE: {type(error).__name__}\n"
                f"ERROR: {str(error)}\n"
                f"resolved_path={self.logs_directory}\n"
                f"elapsed_seconds={elapsed_seconds:.6f}\n\n"
                f"TRACEBACK:\n{traceback.format_exc()}"
            )

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method because file scanning is quick.
        """
        return self.invoke(args, sly_data)
