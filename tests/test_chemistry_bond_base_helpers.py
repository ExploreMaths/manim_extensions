# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the base bond helpers and default no-op hooks."""

import numpy as np
import pytest
from manim import RIGHT, UP, tempconfig

from manim_extensions.chemistry.twoD.atom import MAtomObject
from manim_extensions.chemistry.twoD.bond import SimpleBond


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.fixture()
def bond():
    carbon_a = MAtomObject(coords=np.array([0.0, 0.0, 0.0]), element="C", index=1)
    carbon_b = MAtomObject(coords=np.array([1.0, 0.0, 0.0]), element="C", index=2)
    return SimpleBond(carbon_a, carbon_b, index=3)


def test_bond_index_returned_for_member_atom(bond):
    assert bond.get_bond_index_by_atom(bond.from_atom) == 3


def test_bond_index_is_none_for_foreign_atom(bond):
    other = MAtomObject(coords=np.array([3.0, 0.0, 0.0]), element="O", index=4)

    assert bond.get_bond_index_by_atom(other) is None


def test_add_index_only_when_atom_in_bond(bond):
    target = []

    bond.add_bond_index_by_atom_to_list(bond.from_atom, target)
    assert target == [3]

    foreign = MAtomObject(coords=np.array([3.0, 0.0, 0.0]), element="O", index=4)
    bond.add_bond_index_by_atom_to_list(foreign, target)

    assert target == [3]


def test_perpendicular_vector_for_vertical_direction(bond):
    vector = bond.get_perpendicular_unit_vector(UP * 2, UP * 5)

    assert np.isclose(np.linalg.norm(vector), 1.0)


def test_perpendicular_vector_for_horizontal_direction(bond):
    vector = bond.get_perpendicular_unit_vector(RIGHT * 0, RIGHT * 2 + UP * 0)

    assert vector is not None


def test_default_hooks_run_without_error(bond):
    bond.no_subtype()

    assert bond.bond is not None
