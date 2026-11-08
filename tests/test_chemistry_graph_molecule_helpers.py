# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the geometry and traversal helpers of :class:`GraphMolecule`."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.graph_molecule import GraphMolecule

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


@pytest.fixture()
def molecule():
    return GraphMolecule.molecule_from_string(MOL, format="mol")


def test_atom_positions(molecule):
    single = molecule.find_atom_position_by_index(1)
    many = molecule.find_atoms_position_by_index([1, 2])

    assert isinstance(single, np.ndarray)
    assert len(many) == 2


def test_bond_positions(molecule):
    bond_key = next(iter(molecule.bonds))

    center = molecule.find_bond_center_by_index(bond_key)
    along = molecule.find_position_along_bond_axis(bond_key, 0.5)
    many = molecule.find_bonds_center_by_index([bond_key])

    assert isinstance(center, np.ndarray)
    assert isinstance(along, np.ndarray)
    assert len(many) == 1


def test_all_positions_are_mapped(molecule):
    assert len(molecule.find_all_atoms_positions()) == len(molecule.vertices)
    assert len(molecule.find_all_bonds_centers()) == len(molecule.bonds)


def test_connectivity_helpers(molecule):
    assert len(molecule.get_connected_atoms(1, 3)) > 0
    assert len(molecule.get_atoms_vgroup_from_index([1, 2])) == 2
    assert len(molecule.get_bonds_from_atoms_indices([1, 2, 3])) > 0


def test_labels_and_groups(molecule):
    labels = molecule.make_labels({1: None}, True, "white")

    assert isinstance(labels, dict)
