# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the Table/Row/Cell mobjects.

Indexing convention (per the docstring examples): row 0 is the header,
row 1 is the first data row; ``data[0]`` is always the header row.
"""


import pytest

from manim_extensions.table import Cell, Row, Table

# header + two data rows
DATA = [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]]


def _assert_anims(value):
    from manim.animation.animation import prepare_animation

    assert isinstance(value, list)
    for anim in value:
        # mutation methods may return .animate builders; both are playable
        prepare_animation(anim)


class TestCell:
    def test_construct(self):
        cell = Cell("hello")
        assert cell.get_value() == "hello"

    def test_set_value(self):
        cell = Cell("a")
        cell.set_value("b")
        assert cell.get_value() == "b"

    def test_font_and_border_color_setters(self):
        cell = Cell("a")
        cell.set_font_color("red")
        cell.set_border_color("blue")
        cell.set_background_color("green", opacity=0.3)


class TestRow:
    def test_construct(self):
        row = Row(["a", "b", "c"])
        assert len(row) == 3

    def test_getitem_and_get_cell(self):
        row = Row(["a", "b", "c"])
        assert row[1].get_value() == "b"
        assert row.get_cell(2).get_value() == "c"

    def test_iter(self):
        row = Row(["a", "b"])
        assert [c.get_value() for c in row] == ["a", "b"]


class TestTable:
    def test_data_first_row_is_header(self):
        table = Table(DATA)
        assert table.get_header_names() == ["Name", "Age"]
        assert len(table) == 2  # data rows only

    def test_construct_from_header_and_rows(self):
        table = Table(header=["a", "b"], rows=[["1", "2"], ["3", "4"]])
        assert table.get_header_names() == ["a", "b"]
        assert len(table) == 2

    def test_getitem_returns_data_row(self):
        table = Table(DATA)
        assert table[0][0].get_value() == "Alice"
        assert table[1][0].get_value() == "Bob"

    def test_get_cell_is_one_indexed(self):
        table = Table(DATA)
        # row 1 is the first data row (row 0 is the header)
        assert table.get_cell(1, 1).get_value() == "25"

    def test_get_row_is_one_indexed(self):
        table = Table(DATA)
        assert table.get_row(2)[0].get_value() == "Bob"

    def test_get_column_by_name(self):
        table = Table(DATA)
        column = table.get_column_by_name("Age")
        assert len(column) == 3  # header cell + one per data row

    def test_add_row(self):
        table = Table(DATA)
        new_row, anims = table.add_row(["Charlie", "35"])
        assert len(table) == 3
        assert new_row[0].get_value() == "Charlie"
        _assert_anims(anims)

    def test_delete_row(self):
        table = Table(DATA)
        removed, anims = table.delete_row(1)
        assert len(table) == 1
        _assert_anims(anims)

    def test_delete_header_row_raises(self):
        table = Table(DATA)
        with pytest.raises(ValueError, match="header"):
            table.delete_row(0)

    def test_delete_row_out_of_range(self):
        table = Table(DATA)
        with pytest.raises(IndexError):
            table.delete_row(99)

    def test_add_column(self):
        table = Table(DATA)
        new_col, shift_anims, fade_anims = table.add_column("City", ["NY", "Paris"])
        assert table.get_header_names() == ["Name", "Age", "City"]
        _assert_anims(shift_anims)
        _assert_anims(fade_anims)

    def test_add_column_wrong_length_raises(self):
        table = Table(DATA)
        with pytest.raises(ValueError, match="[Vv]alues"):
            table.add_column("City", ["NY", "Paris", "Extra"])

    def test_delete_column(self):
        table = Table(DATA)
        removed, shift_anims = table.delete_column(0)
        assert table.get_header_names() == ["Age"]

    def test_column_setters(self):
        table = Table(DATA)
        table.set_column_font_color(0, "yellow")
        table.set_column_background_color(1, "purple", opacity=0.2)
