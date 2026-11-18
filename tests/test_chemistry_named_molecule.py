# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the named-molecule wrapper and its geometry helpers."""

import numpy as np
import pytest

from manim_extensions.chemistry.twoD.molecule import MMoleculeObject, NamedMolecule

MOL = (
    "acetone\n"
    "  Mrv2014 03011512422D\n"
    "\n"
    "  6  5  0  0  0  0            999 V2000\n"
    "    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "    1.2990   -0.7500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "    2.5981    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "   -0.6495   -1.1250    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "   -0.6495    1.1250    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "    1.2990   -2.2500    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
    "  1  2  1\n"
    "  2  3  2\n"
    "  1  4  1\n"
    "  1  5  1\n"
    "  2  6  1\n"
    "M  END\n"
)


@pytest.fixture()
def named_molecule():
    molecule = MMoleculeObject.molecule_from_string(MOL, format="mol")
    return NamedMolecule("Acetone", molecule)


def test_named_molecule_collects_label(named_molecule):
    assert len(named_molecule.atoms) == 3
    assert len(named_molecule.bonds) == 2
    assert len(named_molecule.submobjects) == 2


def test_single_index_lookups(named_molecule):
    atom_position = named_molecule.find_atom_position_by_index(1)
    bond_center = named_molecule.find_bond_center_by_index(0)
    along_axis = named_molecule.find_position_along_bond_axis(0, 0.5)

    for value in (atom_position, bond_center, along_axis):
        assert isinstance(value, np.ndarray)
        assert value.shape[-1] == 3


def test_list_index_lookups(named_molecule):
    assert len(named_molecule.find_atoms_position_by_index([1, 2])) == 2
    assert len(named_molecule.find_bonds_center_by_index([0, 1])) == 2


def test_all_positions_are_mapped(named_molecule):
    assert len(named_molecule.find_all_atoms_positions()) == len(named_molecule.atoms)
    assert len(named_molecule.find_all_bonds_centers()) == len(named_molecule.bonds)


def test_numbering_and_rotation_return_self(named_molecule):
    assert named_molecule.add_atom_numbering() is named_molecule
    assert named_molecule.add_bond_numbering() is named_molecule
    assert named_molecule.rotate_bond(0) is named_molecule


def test_from_mol_file(tmp_path, named_molecule):
    path = tmp_path / "acetone.mol"
    path.write_text(MOL)

    loaded = NamedMolecule.from_mol_file("Acetone", str(path))

    assert len(loaded.atoms) >= len(named_molecule.atoms)
    assert len(loaded.bonds) >= len(named_molecule.bonds)


def test_named_molecule_reports_invalid_atom_index(named_molecule):
    with pytest.raises(KeyError):
        named_molecule.find_atom_position_by_index(999)


def test_named_molecule_reports_invalid_bond_index(named_molecule):
    with pytest.raises((IndexError, TypeError)):
        named_molecule.find_bond_center_by_index(999)


def test_named_molecule_reports_invalid_bond_axis_index(named_molecule):
    with pytest.raises((IndexError, TypeError)):
        named_molecule.find_position_along_bond_axis(999, 0.5)


class _RaisingMapping:
    def __init__(self, exc):
        self.exc = exc
        self.submob_dict = {"0": object()}

    def __getitem__(self, key):
        raise self.exc


def test_named_lookup_wraps_key_error_for_atoms(named_molecule):
    named_molecule.atoms = _RaisingMapping(KeyError("atom"))

    with pytest.raises(KeyError):
        named_molecule.find_atom_position_by_index(9)


def test_named_lookup_wraps_key_error_for_bonds(named_molecule):
    named_molecule.bonds = _RaisingMapping(KeyError("bond"))

    with pytest.raises(KeyError):
        named_molecule.find_bond_center_by_index(9)

    with pytest.raises(KeyError):
        named_molecule.find_position_along_bond_axis(9, 0.5)


def test_named_lookup_reraises_unexpected_atom_errors(named_molecule):
    named_molecule.atoms = _RaisingMapping(RuntimeError("unexpected"))

    with pytest.raises(RuntimeError):
        named_molecule.find_atom_position_by_index(0)


def test_base_lookup_wraps_key_error_and_reraises(named_molecule):
    molecule = named_molecule.molecule
    molecule.atoms = _RaisingMapping(KeyError("atom"))
    with pytest.raises(KeyError):
        molecule.find_atom_position_by_index(9)

    molecule.atoms = _RaisingMapping(RuntimeError("unexpected"))
    with pytest.raises(RuntimeError):
        molecule.find_atom_position_by_index(0)


def test_named_molecule_accepts_svg_name(tmp_path):
    from manim import SVGMobject

    svg = tmp_path / "name.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20">'
        '<circle cx="10" cy="10" r="8" fill="black"/></svg>'
    )
    molecule = MMoleculeObject.molecule_from_string(MOL, format="mol")

    named = NamedMolecule(SVGMobject(str(svg)), molecule)

    assert len(named.submobjects) == 2


def test_named_molecule_can_build_from_data_dict():
    molecule = MMoleculeObject.molecule_from_string(MOL, format="mol")

    named = NamedMolecule("Acetone", molecule)

    assert named.molecule is molecule


def test_base_lookup_wraps_bond_key_error(named_molecule):
    molecule = named_molecule.molecule
    molecule.bonds = _RaisingMapping(KeyError("bond"))

    with pytest.raises(KeyError):
        molecule.find_bond_center_by_index(9)

    with pytest.raises(KeyError):
        molecule.find_position_along_bond_axis(9, 0.5)


def test_named_molecule_constructs_base_from_dict(monkeypatch):
    import manim_extensions.chemistry.twoD.molecule as module

    source = MMoleculeObject.molecule_from_string(MOL, format="mol")

    class Dummy:
        def __new__(cls, *args, **kwargs):
            return source

    monkeypatch.setattr(module, "MMoleculeObject", Dummy)

    named = NamedMolecule("Acetone", {})

    assert named.molecule is source
