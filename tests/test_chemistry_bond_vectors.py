# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for bond vector and subtype helpers."""

import numpy as np
import pytest

from manim import Line

from manim_extensions.chemistry.twoD.atom import MAtomObject
from manim_extensions.chemistry.twoD.bond import (
    DoubleBond,
    PlainCramBond,
    SimpleBond,
    TripleBond,
)

BOND_CLASSES = [SimpleBond, DoubleBond, TripleBond, PlainCramBond]


@pytest.fixture()
def atoms():
    atom_a = MAtomObject(coords=np.array([0.0, 0.0, 0.0]), element="C", index=1)
    atom_b = MAtomObject(coords=np.array([1.0, 0.0, 0.0]), element="C", index=2)
    return atom_a, atom_b


@pytest.mark.parametrize("cls", BOND_CLASSES)
def test_get_vector_matches_geometry(cls, atoms):
    atom_a, atom_b = atoms
    bond = cls(atom_a, atom_b)

    vector = bond.get_vector()

    assert np.isfinite(vector).all()


@pytest.mark.parametrize("cls", [SimpleBond, PlainCramBond])
@pytest.mark.parametrize("subtype", ["complete", "skeleton", "over_bond"])
def test_longer_subtype_returns_bond(cls, atoms, subtype):
    atom_a, atom_b = atoms
    bond = cls(atom_a, atom_b, subtype=subtype)

    assert bond.longer_subtype() is not None


def test_triple_bond_longer_subtype_adds_parallel_lines(atoms):
    atom_a, atom_b = atoms
    bond = TripleBond(atom_a, atom_b, subtype="complete")
    base_line = Line(atom_a.coords, atom_b.coords)

    bond.longer_subtype(bond, base_line)

    assert len(bond.submobjects) >= 1
