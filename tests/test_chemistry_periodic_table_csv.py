# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the periodic table built from the element CSV data."""

import pytest
from manim import tempconfig

from manim_extensions.chemistry.periodic_table.table_objects import PeriodicTable

DATA_FILE = "element_data.csv"


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.fixture(scope="module")
def table():
    return PeriodicTable(DATA_FILE)


def test_table_loads_all_elements(table):
    assert len(table.table) >= 1


def test_table_elements_are_positioned(table):
    positions = table.elements_position_dict()

    assert len(positions) >= 1
