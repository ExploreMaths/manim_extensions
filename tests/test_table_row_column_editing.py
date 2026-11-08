# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for row and column editing on :class:`~manim_extensions.table.table.Table`."""

import pytest

from manim_extensions.table.table import Table


@pytest.fixture()
def table():
    return Table([["a", "b"], ["c", "d"], ["e", "f"]])


def test_delete_row(table):
    table.delete_row(1)

    assert table is not None


def test_add_column(table):
    result = table.add_column("g", ["h", "i"])

    assert result is not None


def test_delete_column(table):
    table.delete_column(1)

    assert table is not None


def test_column_and_header_setters(table):
    table.set_column_font_color(1, "red")
    table.set_column_background_color(1, "grey")
    table.set_header_background_color("blue")
    table.set_header_font_color("white")
    table.set_column_border_color(1, "black", 0.1)

    assert table is not None
