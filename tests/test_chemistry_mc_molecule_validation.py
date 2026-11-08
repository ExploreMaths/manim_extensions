# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for MCMolecule list validation and file-based construction."""

import pytest

from manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule import MCMolecule

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


def test_add_atoms_from_dict_rejects_non_list_atoms():
    molecule = MCMolecule()
    molecule.atoms = "not a list"

    with pytest.raises(Exception):
        molecule.add_atoms_from_atoms_dict({}, {})


def test_add_bonds_from_dict_rejects_non_list_bonds():
    molecule = MCMolecule()
    molecule.bonds = "not a list"

    with pytest.raises(Exception):
        molecule.add_bonds_from_bonds_dict({})


def test_add_connections_rejects_non_list_bonds():
    molecule = MCMolecule()
    molecule.bonds = "not a list"

    with pytest.raises(Exception):
        molecule.add_connections_between_atoms()


def test_construct_from_file_returns_molecule(tmp_path):
    path = tmp_path / "acetone.mol"
    path.write_text(MOL)

    molecule = MCMolecule.construct_from_file(str(path))

    assert len(molecule.atoms) == 3


def test_construct_from_string_returns_molecule():
    molecule = MCMolecule.construct_from_string(MOL, format="mol")

    assert len(molecule.atoms) == 3


def test_remove_hydrogens_on_empty_list_is_noop():
    molecule = MCMolecule()

    molecule.remove_hydrogens([])

    assert molecule.atoms is None or isinstance(molecule.atoms, list)
