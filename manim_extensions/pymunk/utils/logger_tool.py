# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)

"""Logger utility for Pymunk physics simulations."""

__all__ = ["manim_pymunk_logger"]

import logging
import threading


class SingletonLogger:
    """Thread-safe singleton logger that provides a single shared logging
    instance for the manim-pymunk module with a console handler.
    """
    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Double-checked locking for thread safety
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super(SingletonLogger, cls).__new__(cls)
                    cls._instance._inherited_init()
        return cls._instance

    def _inherited_init(self):
        """Configure your logging logic here."""
        self.logger = logging.getLogger("MySingletonLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Avoid adding duplicate handlers
        if not self.logger.handlers:
            # 1. Define format
            log_format = "manim-pymunk:[%(levelname)s]:%(asctime)s:%(filename)s:%(message)s"
            date_format = "%Y-%m-%d %H-%M-%S"
            formatter = logging.Formatter(log_format, date_format)

            # 2. Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        """Return the singleton Python logging.Logger instance configured
        for the manim-pymunk module.
        """
        return self.logger

# For convenience, instantiate a global singleton
manim_pymunk_logger = SingletonLogger().get_logger()