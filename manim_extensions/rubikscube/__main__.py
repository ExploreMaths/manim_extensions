# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Main module for Rubik's Cube extension.

This module provides the entry point for the Rubik's Cube extension.

"""

from manim_extensions.rubikscube import __version__


def main() -> None:
    """Entry point for the ``python -m manim_extensions.rubikscube`` command."""
    print("Manim Rubik's Cube v" + __version__ + "\n")


if __name__ == "__main__":
    main()