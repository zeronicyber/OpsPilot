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
        self.log_file = Path(__file__).parents[2] / "opspilot_data" / "logs" / "sasgrid_metadata.log"
        logger.debug("... OpsPilot log search initialized for %s ...", self.log_file)

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
        try:
            query = args.get("query") or args.get("search_term")
            logger.debug("Current working directory: %s", Path.cwd())
            logger.debug("Query value received: %r", query)
            if not isinstance(query, str) or not query.strip():
                return "Error: No search query provided."

            logger.debug("Log file path being searched: %s", self.log_file)
            query_lower = query.casefold()
            with self.log_file.open("r", encoding="utf-8") as stream:
                matches = [line.rstrip() for line in stream if query_lower in line.casefold()]

            if not matches:
                return f"No log entries found for '{query}'."
            return "\n".join(matches)
        except Exception as error:
            return f"ERROR: {str(error)}\n\n{traceback.format_exc()}"

    async def async_invoke(self, args: Dict[str, Any], sly_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Delegates to the synchronous invoke method because file scanning is quick.
        """
        return self.invoke(args, sly_data)
