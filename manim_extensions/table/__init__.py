# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""
Manimal - Manim Community Edition Database Animation Extension

A clean, modular extension for Manim Community Edition (manim CE) to
animate database tables, rows, columns, and cells.

Usage:
    from manim_extensions.table import Table

    table = Table([
        ["first_name", "last_name", "age"],
        ["Philippe", "Oger", "26"],
        ["Renata", "Oger", "25"],
    ])
"""

from .table import Table
from .row import Row
from .cell import Cell

__all__ = ["Table", "Row", "Cell"]
__version__ = "0.1.0"
