# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""
This module is used to log messages to the console.

It's main purpose is make the logging output more readable by using the rich library.
One might argue, that a library should do any styling to the logging output, which I think is a valid for most cases.
"""

import logging
from rich.logging import RichHandler

#: Logging format used by the package logger.
_FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=_FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(show_path=False)],
)

_log = logging.getLogger("rich")

if __name__ == "__main__":  # pragma: no cover - manual logging check
    _log.info("This is an info message")
    _log.warning("This is a warning message")
    _log.error("This is an error message")
    _log.critical("This is a critical message")
