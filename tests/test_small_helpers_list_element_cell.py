# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for small container/element/table helper APIs."""

import pytest
from manim import Dot, Square, Text

from manim_extensions.chemistry.element.element import Element
from manim_extensions.machine_learning.utils.mobjects.list_group import ListGroup
from manim_extensions.table.cell import Cell

ELEMENT_CSV = """Symbol,Name,AtomicNumber,AtomicMass,Color
H,Hydrogen,1,1.008,#FFFFFF
O,Oxygen,8,15.999,#FF0000
"""


@pytest.fixture()
def csv_file(tmp_path):
    path = tmp_path / "elements.csv"
    path.write_text(ELEMENT_CSV)
    return str(path)


def test_list_group_insert_and_remove():
    group = ListGroup(Dot(), Square())

    group.insert(1, Text("x"))
    removed = group.remove_at_index(0)
    remaining = group.remove_at_indices([0])

    assert removed is not None
    assert isinstance(remaining, list)


def test_list_group_get():
    group = ListGroup(Dot(), Square())

    assert group.get(1) is not None


def test_element_from_csv_by_symbol(csv_file):
    element = Element.from_csv_file(csv_file, "O")

    assert element.symbol == "O"
    assert element.atomic_number == 8


def test_element_from_csv_by_number(csv_file):
    element = Element.from_csv_file(csv_file, 1)

    assert element.symbol == "H"


def test_element_from_csv_rejects_bad_reference(csv_file):
    with pytest.raises(Exception):
        Element.from_csv_file(csv_file, 200)


def test_element_repr():
    assert "H" in repr(Element())


def test_cell_resize_and_value_replace():
    cell = Cell("old")

    resized = cell.get_resized_copy(2.0)
    new_text = cell.set_value("new")

    assert resized.width == pytest.approx(2.0)
    assert new_text is not None
