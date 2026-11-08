# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests that drive every bond representation branch."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.atom import MAtomObject
from manim_extensions.chemistry.twoD.bond import (
    DoubleBond,
    PlainCramBond,
    SimpleBond,
    TripleBond,
)

BOND_CLASSES = [SimpleBond, DoubleBond, TripleBond, PlainCramBond]
REPRESENTATIONS = [None, "complete", "skeleton", "over_bond"]


def make_atom(x: float, representation=None, index: int = 1) -> MAtomObject:
    return MAtomObject(
        coords=np.array([x, 0.0, 0.0]),
        element="C",
        index=index,
        representation_type=representation,
    )


@pytest.mark.parametrize("cls", BOND_CLASSES)
@pytest.mark.parametrize("representation", REPRESENTATIONS)
def test_bond_with_uniform_representation(cls, representation):
    bond = cls(make_atom(0.0, representation, 1), make_atom(1.0, representation, 2))

    assert len(bond.submobjects) == 1


@pytest.mark.parametrize("cls", BOND_CLASSES)
@pytest.mark.parametrize(
    "from_repr, to_repr",
    [
        ("complete", "skeleton"),
        ("skeleton", "complete"),
        ("over_bond", "complete"),
    ],
)
def test_bond_with_mixed_representations(cls, from_repr, to_repr):
    bond = cls(make_atom(0.0, from_repr, 1), make_atom(1.0, to_repr, 2))

    assert len(bond.submobjects) == 1


@pytest.mark.parametrize("cls", BOND_CLASSES)
def test_get_vector_returns_line_vector(cls):
    bond = cls(make_atom(0.0, "complete", 1), make_atom(1.0, "skeleton", 2))

    vector = bond.get_vector()

    assert len(vector) == 3
