# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Main module for Rubik's Cube extension.

This module provides the entry point for the Rubik's Cube extension.
"""

from typing import Any

from . import __version__


def main() -> Any:
    """Entry point for the ``python -m manim_extensions.rubikscube`` command.

    Returns
    -------
        The resulting value.
    """
    print("Manim Rubik's Cube v" + __version__ + "\n")


if __name__ == "__main__":  # pragma: no cover - module entry point
    main()
