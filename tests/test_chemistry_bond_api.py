# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the bond API shared by the 2D molecule builders."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.atom import MAtomObject
from manim_extensions.chemistry.twoD.bond import (
    DoubleBond,
    PlainCramBond,
    SimpleBond,
    TripleBond,
)


@pytest.fixture
def atoms():
    """Two carbon atoms one unit apart."""
    atom_a = MAtomObject(coords=np.array([0.0, 0.0, 0.0]), element="C", index=1)
    atom_b = MAtomObject(coords=np.array([1.0, 0.0, 0.0]), element="C", index=2)
    return atom_a, atom_b


BOND_CLASSES = [SimpleBond, DoubleBond, TripleBond, PlainCramBond]


@pytest.mark.parametrize("cls", BOND_CLASSES)
def test_atom_membership(cls, atoms):
    atom_a, atom_b = atoms
    bond = cls(atom_a, atom_b)

    assert bond.atoms_in_bond() == (atom_a, atom_b)
    assert bond.atom_is_in_bond(atom_a) is True
    assert bond.atom_is_in_bond(MAtomObject(coords=np.array([2.0, 0.0, 0.0]), element="C", index=3)) is False


@pytest.mark.parametrize("cls", BOND_CLASSES)
def test_bond_index_helpers(cls, atoms):
    atom_a, atom_b = atoms
    bond = cls(atom_a, atom_b, index=5)

    assert bond.get_bond_index_by_atom(atom_a) == bond.index
    assert bond.get_bond_index_by_atom(atom_b) == bond.index

    collected = bond.add_bond_index_by_atom_to_list(atom_a, [1, 2])
    assert isinstance(collected, list)


@pytest.mark.parametrize("cls", BOND_CLASSES)
def test_geometry_helpers(cls, atoms):
    atom_a, atom_b = atoms
    bond = cls(atom_a, atom_b)

    expected = bond.get_perpendicular_unit_vector(
        atom_a.get_center(), atom_b.get_center()
    )
    assert np.isfinite(expected).all()


@pytest.mark.parametrize("subtype", ["complete", "skeleton", "over_bond", None])
def test_subtypes(subtype, atoms):
    atom_a, atom_b = atoms
    bond = SimpleBond(atom_a, atom_b, subtype=subtype)

    assert bond.bond is not None


@pytest.mark.parametrize("cls", BOND_CLASSES)
def test_represents(cls, atoms):
    atom_a, atom_b = atoms
    bond = cls(atom_a, atom_b)

    text = str(bond)
    representation = repr(bond)

    assert isinstance(text, str)
    assert isinstance(representation, str)
