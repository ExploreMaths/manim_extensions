# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the periodic table built from generated element CSV data."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.periodic_table.table_objects import (
    MElementObject,
    PeriodicTable,
)

HEADER = "AtomicNumber,AtomicMass,Name,Symbol,Color"


def _write_element_csv(path, numbers):
    lines = [HEADER]
    for number in numbers:
        lines.append(f"{number},{float(number)},Element{number},X,#909090")
    path.write_text("\n".join(lines) + "\n")
    return str(path)


@pytest.fixture(scope="module")
def data_file(tmp_path_factory):
    path = tmp_path_factory.mktemp("periodic") / "element_data.csv"
    return _write_element_csv(path, range(1, 119))


@pytest.fixture(scope="module")
def table(data_file):
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield PeriodicTable(data_file)


def test_table_loads_all_elements(table):
    assert len(table.table) >= 1


def test_table_elements_are_positioned(table):
    positions = table.elements_position_dict()

    assert len(positions) >= 1


def test_from_csv_file_data_reads_row(data_file):
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        element = MElementObject.from_csv_file_data(data_file, atomic_number=6)

    assert element.atomic_number == 6
