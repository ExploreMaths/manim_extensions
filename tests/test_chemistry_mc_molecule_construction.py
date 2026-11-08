# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for MCMolecule construction and hydrogen removal helpers."""

import pytest

from manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule import MCMolecule

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


def test_construct_from_file(tmp_path):
    path = tmp_path / "acetone.mol"
    path.write_text(MOL)

    molecule = MCMolecule.construct_from_file(str(path))

    assert molecule is not None


def test_remove_all_hydrogens_drops_hydrogen_atoms():
    molecule = MCMolecule.construct_from_string(MOL, format="mol")

    molecule.remove_all_hydrogens()

    assert all(atom.element.atomic_number != 1 for atom in molecule.atoms_by_index.values())


def test_remove_hydrogens_with_empty_list_is_noop():
    molecule = MCMolecule.construct_from_string(MOL, format="mol")
    count = len(molecule.atoms_by_index)

    molecule.remove_hydrogens([])

    assert len(molecule.atoms_by_index) == count
