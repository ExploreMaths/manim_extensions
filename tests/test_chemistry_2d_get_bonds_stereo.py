# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for stereo bond handling inside MMoleculeObject.get_bonds."""

import numpy as np
import pytest
from manim import tempconfig

from manim_extensions.chemistry.twoD.bond import DashedCramBond, PlainCramBond, SimpleBond
from manim_extensions.chemistry.twoD.molecule import MMoleculeObject


def build_atoms():
    return {
        1: {
            "coords": np.array([0.0, 0.0, 0.0]),
            "element": "C",
            "bond_to": {2: "O", 3: "H", 4: "H", 5: "H", 6: "H"},
        },
        2: {"coords": np.array([1.2, 0.0, 0.0]), "element": "O", "bond_to": {1: "C"}},
        3: {"coords": np.array([0.0, 1.0, 0.0]), "element": "H", "bond_to": {1: "C"}},
        4: {"coords": np.array([0.0, -1.0, 0.0]), "element": "H", "bond_to": {1: "C"}},
        5: {"coords": np.array([-1.0, 0.0, 0.0]), "element": "H", "bond_to": {1: "C"}},
        6: {"coords": np.array([0.0, 0.0, 1.0]), "element": "H", "bond_to": {1: "C"}},
    }


def build_bonds():
    return {
        1: [
            {"to": 2, "type": 1},
            {"to": 3, "type": 1, "stereo": 1},
            {"to": 4, "type": 1, "stereo": 6},
            {"to": 5, "type": 1},
            {"to": 6, "type": 1},
        ]
    }


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_get_bonds_builds_wedge_and_hash_bonds():
    molecule = MMoleculeObject(atoms_dict=build_atoms(), bonds_dict=build_bonds())

    types = [type(bond) for bond in molecule.bonds]

    assert PlainCramBond in types
    assert DashedCramBond in types
    assert SimpleBond in types


def test_get_bonds_returns_vgroup_of_all_bonds():
    molecule = MMoleculeObject(atoms_dict=build_atoms(), bonds_dict=build_bonds())

    assert len(molecule.get_bonds()) == len(molecule.bonds_dict[1])


def test_get_atoms_returns_vdict_and_index_map():
    molecule = MMoleculeObject(atoms_dict=build_atoms(), bonds_dict=build_bonds())

    atoms, index_map = molecule.get_atoms()

    assert len(index_map) >= 2
    assert len(atoms) >= 2
