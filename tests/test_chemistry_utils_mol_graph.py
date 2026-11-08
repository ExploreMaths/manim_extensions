# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the mol-to-graph helper and localized element lookup."""

from manim_extensions.chemistry.utils.utils import get_element, mol_to_graph

MOL = """acetone
     RDKit          2D

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.0000    0.9000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0
  1  3  1  0
M  END
"""


def test_mol_to_graph_reads_atoms_and_bonds(tmp_path):
    path = tmp_path / "acetone.mol"
    path.write_text(MOL)

    atoms, bonds = mol_to_graph(str(path))

    assert len(atoms) == 3
    assert len(bonds) == 2
    assert "position" in atoms[1]


def test_get_element_spanish_language():
    element = get_element("C_ESP", language="ESP")

    assert element.symbol is not None
