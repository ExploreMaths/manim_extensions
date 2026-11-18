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

    assert all(
        atom.element.atomic_number != 1 for atom in molecule.atoms_by_index.values()
    )


def test_remove_hydrogens_with_empty_list_is_noop():
    molecule = MCMolecule.construct_from_string(MOL, format="mol")
    count = len(molecule.atoms_by_index)

    molecule.remove_hydrogens([])

    assert len(molecule.atoms_by_index) == count


def test_construct_from_file_accepts_list_payload(monkeypatch, tmp_path):
    from manim_extensions.chemistry import FileHandler

    path = tmp_path / "x.mol"
    path.write_text(MOL)
    monkeypatch.setattr(FileHandler, "parsed_atoms_bonds_data", lambda self: [({}, {})])
    monkeypatch.setattr(
        MCMolecule, "construct_from_data_dict", lambda *args, **kwargs: object()
    )

    assert MCMolecule.construct_from_file(str(path)) is not None


def test_construct_multiple_from_file_iterates_payload(monkeypatch, tmp_path):
    from manim_extensions.chemistry import FileHandler

    path = tmp_path / "x.mol"
    path.write_text(MOL)
    monkeypatch.setattr(
        FileHandler, "parsed_atoms_bonds_data", lambda self: [({}, {}), ({}, {})]
    )
    monkeypatch.setattr(
        MCMolecule, "construct_from_data_dict", lambda *args, **kwargs: object()
    )

    result = MCMolecule.construct_multiples_from_file(str(path))

    assert len(result) == 2


def test_construct_from_string_accepts_list_payload(monkeypatch):
    from manim_extensions.chemistry import FileHandler

    monkeypatch.setattr(FileHandler, "parse_from_string", lambda **kwargs: [({}, {})])
    monkeypatch.setattr(
        MCMolecule, "construct_from_data_dict", lambda *args, **kwargs: object()
    )

    assert MCMolecule.construct_from_string("C", format="mol") is not None


def test_construct_multiple_from_string_iterates_payload(monkeypatch):
    from manim_extensions.chemistry import FileHandler

    monkeypatch.setattr(
        FileHandler, "parse_from_string", lambda **kwargs: [({}, {}), ({}, {})]
    )
    monkeypatch.setattr(
        MCMolecule, "construct_from_data_dict", lambda *args, **kwargs: object()
    )

    result = MCMolecule.construct_multiples_from_string("C", format="mol")

    assert len(result) == 2


def test_remove_all_hydrogens_after_keeping_hydrogens():
    molecule = MCMolecule.construct_from_string(
        MOL, format="mol", ignore_hydrogens=False
    )

    molecule.remove_all_hydrogens()

    assert all(
        atom.element.atomic_number != 1 for atom in molecule.atoms_by_index.values()
    )


def test_construct_from_data_dict_can_drop_all_hydrogens():
    result = MCMolecule.construct_from_string(
        MOL, format="mol", ignore_all_hydrogens=True
    )

    assert all(
        atom.element.atomic_number != 1 for atom in result.atoms_by_index.values()
    )


def test_remove_hydrogens_handles_to_atom_matches():
    molecule = MCMolecule.construct_from_string(
        MOL, format="mol", ignore_hydrogens=False
    )
    before = len(molecule.atoms_by_index)
    first = molecule.atoms[0].molecule_index

    molecule.remove_hydrogens([first])

    assert len(molecule.atoms_by_index) < before


def test_remove_hydrogens_without_bonds_returns_early():
    from types import SimpleNamespace

    molecule = MCMolecule()
    molecule.atoms_by_index = {0: SimpleNamespace()}
    molecule.atoms = []
    molecule.bonds = []

    molecule.remove_hydrogens([0])

    assert molecule.atoms == []
