# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Configure readable console logging for the QR-code helpers.

The module installs ``rich.logging.RichHandler`` through
``logging.basicConfig`` so log records are readable in a terminal.  Logging
configuration normally belongs to the application; this module preserves the
vendored upstream behaviour and is not part of the public API.
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
