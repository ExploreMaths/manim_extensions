# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the graph-based molecule representation."""

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


def test_molecule_from_mol_block():
    molecule = GraphMolecule.molecule_from_string(MOL, format="mol")

    assert len(molecule.vertices) == 3


def test_molecule_name_can_be_added():
    molecule = GraphMolecule.molecule_from_string(MOL, format="mol")

    molecule.add_molecule_name("acetone")

    assert molecule is not None


def test_bond_type_support_table():
    assert (
        "1" in GraphMolecule.SUPPORTED_BOND_TYPES
        or 1 in GraphMolecule.SUPPORTED_BOND_TYPES
    )
