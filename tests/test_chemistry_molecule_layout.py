# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the 2-D molecule layout built from a MOL block."""

import pytest

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject

MOL = """acetone
     RDKit          2D

  6  5  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2990    0.7500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2990    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    1.5000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -2.0000    0.0000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    1.5000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
  3  4  1  0
  3  5  1  0
  1  6  1  0
M  END
"""


@pytest.fixture(scope="module")
def molecule():
    return MMoleculeObject.molecule_from_string(MOL, format="mol")


def test_atoms_and_bonds_are_built(molecule):
    assert len(molecule.atoms) == 3
    assert len(molecule.bonds) == 2


def test_default_layout_has_submobjects(molecule):
    assert len(molecule.submobjects) > 0


def test_explicit_carbons_and_hydrogens():
    molecule = MMoleculeObject.molecule_from_string(
        MOL, format="mol", explicit_carbons=True, explicit_hydrogens=True
    )

    assert molecule is not None


def test_atom_and_bond_numbering():
    molecule = MMoleculeObject.molecule_from_string(
        MOL, format="mol", add_atoms_numbering=True, add_bonds_numbering=True
    )

    assert molecule is not None


def test_representation_type_variants():
    for representation in (None, "2d", "3d"):
        molecule = MMoleculeObject.molecule_from_string(
            MOL, format="mol", representation_type=representation
        )
        assert molecule is not None
