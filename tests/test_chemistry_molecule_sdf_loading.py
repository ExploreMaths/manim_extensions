# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for loading and querying 2-D molecules from SDF strings."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject as Mol

SDF = """acetone
     RDKit          2D

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0000    1.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
M  END
"""


@pytest.fixture()
def molecule():
    molecules = Mol.from_sdf_string(SDF)

    assert len(molecules) == 1
    return molecules[0]


def test_sdf_molecule_has_atoms_and_bonds(molecule):
    assert len(molecule.atoms) == 3
    assert len(molecule.bonds) == 2


def test_bonds_group_is_built(molecule):
    assert len(molecule.bonds) == 2


def test_position_queries(molecule):
    atom_position = molecule.find_atom_position_by_index(1)
    bond_center = molecule.find_bond_center_by_index(0)
    along_axis = molecule.find_position_along_bond_axis(0, 0.5)

    assert isinstance(atom_position, np.ndarray)
    assert isinstance(bond_center, np.ndarray)
    assert isinstance(along_axis, np.ndarray)
    assert atom_position.shape[-1] == 3


def test_numbering_returns_self(molecule):
    assert molecule.add_atom_numbering() is molecule
    assert molecule.add_bond_numbering() is molecule


def test_complete_missing_hydrogens_keeps_molecule_usable(molecule):
    molecule.complete_missing_hydrogens()

    assert len(molecule.atoms) >= 3
