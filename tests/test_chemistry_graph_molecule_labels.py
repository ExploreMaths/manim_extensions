# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for graph molecule labels, bond types and connected atom groups."""

import pytest
from manim import tempconfig

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


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.fixture()
def molecule():
    return GraphMolecule.molecule_from_string(MOL, format="mol")


@pytest.mark.parametrize("bond_type", [1, 2, 3])
def test_select_bond_type_returns_line_class(molecule, bond_type):
    assert molecule.select_bond_type(bond_type) is not None


def test_invalid_bond_type_raises(molecule):
    with pytest.raises(Exception):
        molecule.select_bond_type(7)


def test_connected_atoms_walk_through_chain(molecule):
    atoms = molecule.get_connected_atoms(1, 3)

    assert isinstance(atoms, list)


def test_connected_atoms_v_group(molecule):
    group = molecule.get_connected_atoms_v_group(1, 3)

    assert group is not None


def test_connected_atoms_and_bonds(molecule):
    group = molecule.get_connected_atoms_and_bonds(1, 3)

    assert group is not None
