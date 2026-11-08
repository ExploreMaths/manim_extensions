# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for three-dimensional chemical bonds."""

import numpy as np
import pytest
from manim import tempconfig

from manim_extensions.chemistry.element.element import Element
from manim_extensions.chemistry.threeD.threedatom import ThreeDAtom
from manim_extensions.chemistry.threeD.threedbond import ThreeDBond

CARBON = Element(symbol="C", name="Carbon", atomic_number=6, mass=12.011, color="#FFFFFF")
OXYGEN = Element(symbol="O", name="Oxygen", atomic_number=8, mass=15.999, color="#FF0000")


@pytest.fixture()
def atoms():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        first = ThreeDAtom(CARBON, coords=np.array([0.0, 0.0, 0.0]))
        second = ThreeDAtom(OXYGEN, coords=np.array([1.5, 0.0, 0.0]))
        first.index, second.index = 1, 2
        yield first, second


@pytest.mark.parametrize("bond_type", [1, 2, 3])
def test_bond_construction_per_order(atoms, bond_type):
    first, second = atoms

    bond = ThreeDBond(first, second, bond_type=bond_type)

    assert len(bond.submobjects) >= 1
