# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the 3-D bond mobjects."""

import numpy as np
import pytest

from manim_extensions.chemistry.element import Element
from manim_extensions.chemistry.threeD.threedatom import ThreeDAtom
from manim_extensions.chemistry.threeD.threedbond import ThreeDBond, ThreeDLine


@pytest.fixture()
def atoms():
    element = Element("C")
    return (
        ThreeDAtom(element=element, coords=np.array([0.0, 0.0, 0.0])),
        ThreeDAtom(element=element, coords=np.array([1.0, 0.0, 0.0])),
    )


def test_atom_positions(atoms):
    first, second = atoms

    assert np.allclose(first.coords, [0.0, 0.0, 0.0])
    assert np.allclose(second.coords, [1.0, 0.0, 0.0])


@pytest.mark.parametrize("bond_type", [1, 2, 3])
def test_bond_builds_submobjects(atoms, bond_type):
    first, second = atoms

    bond = ThreeDBond(first, second, bond_type)

    assert len(bond.submobjects) >= 1


def test_line_from_points():
    line = ThreeDLine(np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]))

    assert line is not None
