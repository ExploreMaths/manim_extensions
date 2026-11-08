# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for loading named molecules from SDF strings and files."""

import pytest

from manim_extensions.chemistry.twoD.molecule import NamedMolecule

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
def named_molecule():
    molecules = NamedMolecule.from_sdf_string("acetone", SDF)

    assert len(molecules) == 1
    return molecules[0]


def test_named_molecule_has_atoms_and_bonds(named_molecule):
    assert len(named_molecule.atoms) == 3
    assert len(named_molecule.bonds) == 2


def test_get_bonds_group(named_molecule):
    assert len(named_molecule.get_bonds()) >= 1


def test_numbering_returns_self(named_molecule):
    assert named_molecule.add_atom_numbering() is named_molecule
    assert named_molecule.add_bond_numbering() is named_molecule


def test_from_sdf_file(tmp_path):
    path = tmp_path / "acetone.sdf"
    path.write_text(SDF)

    molecules = NamedMolecule.from_sdf_file("acetone", str(path))

    assert len(molecules) == 1
    assert len(molecules[0].atoms) == 3
