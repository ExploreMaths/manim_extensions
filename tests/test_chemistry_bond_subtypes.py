# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the bond subtype variants exposed by every bond class."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.atom import MAtomObject
from manim_extensions.chemistry.twoD.bond import (
    DashedCramBond,
    DoubleBond,
    PlainCramBond,
    SimpleBond,
    TripleBond,
)

BOND_CLASSES = [SimpleBond, DoubleBond, TripleBond, PlainCramBond, DashedCramBond]
CRAM_CLASSES = [PlainCramBond, DashedCramBond]


def make_bond(bond_cls):
    return bond_cls(
        MAtomObject(element="C", coords=np.zeros(3), index=1),
        MAtomObject(element="C", coords=np.array([1.5, 0.0, 0.0]), index=2),
    )


@pytest.mark.parametrize("bond_cls", BOND_CLASSES)
def test_default_and_short_subtypes(bond_cls):
    bond = make_bond(bond_cls)

    assert bond.no_subtype() is not None
    assert bond.shorter_subtype() is not None


@pytest.mark.parametrize("bond_cls", BOND_CLASSES)
def test_vector_of_bond(bond_cls):
    bond = make_bond(bond_cls)

    vector = bond.get_vector()

    assert vector.shape == (3,)


@pytest.mark.parametrize("bond_cls", CRAM_CLASSES)
def test_cram_bond_subtypes(bond_cls):
    bond = make_bond(bond_cls)

    assert bond.shorter_from_subtype() is not None
    assert bond.shorter_to_subtype() is not None
    assert bond.longer_subtype() is not None
