# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for graph-molecule lookup error handling."""

import pytest

from manim_extensions.chemistry.twoD.graph_molecule import GraphMolecule

MOL = """acetone
     RDKit          2D

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2990    0.7500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.2990    0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
M  END
"""


@pytest.fixture()
def molecule():
    return GraphMolecule.molecule_from_string(MOL, format="mol")


def test_invalid_atom_index_raises(molecule):
    with pytest.raises((KeyError, AttributeError)):
        molecule.find_atom_position_by_index(99)


def test_invalid_bond_index_raises(molecule):
    with pytest.raises((KeyError, IndexError, AttributeError)):
        molecule.find_bond_center_by_index(99)


def test_invalid_bond_axis_raises(molecule):
    with pytest.raises((KeyError, IndexError, AttributeError)):
        molecule.find_position_along_bond_axis(99, 0.5)
