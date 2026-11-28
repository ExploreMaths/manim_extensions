# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
# patched: document module-level constants

"""Logger utility for Pymunk physics simulations."""

from __future__ import annotations

# from typing import Any

__all__ = ["manim_pymunk_logger"]
import logging
import threading


class SingletonLogger:
    """Thread-safe singleton logger that provides a single shared logging
    instance for the manim-pymunk module with a console handler.

    Examples
    --------
    .. manim:: SingletonLoggerOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.pymunk.utils.logger_tool import SingletonLogger

       SingletonLoggerTarget = SingletonLogger

       class SingletonLoggerOverview(Scene):
           def construct(self):
               public = [n for n in dir(SingletonLoggerTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('SingletonLogger', font_size=36),
                   Text('module: manim_extensions.pymunk.utils.logger_tool', font_size=18, color=GREY),
                   Text('Thread-safe singleton logger that provides a single shared logging instance for the manim-pymunk module with a console handler', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.pymunk.utils.logger_tool import SingletonLogger

        logger = SingletonLogger()
        logger.info("physics scene ready")
    """

    _instance_lock = threading.Lock()
    _instance = None

    def __new__(cls, *args: object, **kwargs: object) -> "SingletonLogger":
        """Return the process-wide singleton logger instance.

        Parameters
        ----------
        *args
            Ignored constructor arguments.
        **kwargs
            Ignored constructor keyword arguments.

        Returns
        -------
            The process-wide singleton logger instance.
        """
        # Double-checked locking for thread safety
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super(SingletonLogger, cls).__new__(cls)
                    cls._instance._inherited_init()
        return cls._instance

    def _inherited_init(self) -> None:
        """Configure the singleton logger format, level and stream handler."""
        self.logger = logging.getLogger("MySingletonLogger")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        # Avoid adding duplicate handlers
        if not self.logger.handlers:
            # 1. Define format
            log_format = (
                "manim-pymunk:[%(levelname)s]:%(asctime)s:%(filename)s:%(message)s"
            )
            date_format = "%Y-%m-%d %H-%M-%S"
            formatter = logging.Formatter(log_format, date_format)

            # 2. Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """Return the singleton Python logging.Logger instance configured
        for the manim-pymunk module.

        Returns
        -------
            The singleton Python logging.Logger instance configured.
        """
        return self.logger


# For convenience, instantiate a global singleton
#: Logger shared by the manim-pymunk modules.
manim_pymunk_logger = SingletonLogger().get_logger()
