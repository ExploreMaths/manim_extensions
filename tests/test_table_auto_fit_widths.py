# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for auto-fitting table column widths during row/column edits."""

import pytest

from manim_extensions.table.table import Table


@pytest.fixture()
def table():
    return Table(
        [["h", "b"], ["a very long cell value", "c"], ["d", "e"]],
        auto_fit=True,
    )


def test_delete_row_recalculates_widths(table):
    deleted, animations = table.delete_row(1)

    assert deleted is not None
    assert len(animations) >= 2


def test_add_row_returns_row_and_animations(table):
    row, animations = table.add_row(["x", "y"])

    assert row is not None
    assert animations is not None


def test_add_column_returns_animations(table):
    animations = table.add_column("zzz", ["1", "2"])

    assert animations is not None


def test_column_lookup_by_name(table):
    column = table.get_column_by_name("h")

    assert column is not None
