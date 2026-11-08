# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the PubChem XML and JSON molecule parsers."""

import json

import numpy as np
import pytest

from manim_extensions.chemistry.utils.parsers.json_parser import JSONParser
from manim_extensions.chemistry.utils.parsers.xml_parser import XMLParser


def xml_molecule(coords_z=True):
    conformer = {
        "PC-Conformer_x": {"PC-Conformer_x_E": ["0.0", "1.2"]},
        "PC-Conformer_y": {"PC-Conformer_y_E": ["0.0", "0.4"]},
    }
    if coords_z:
        conformer["PC-Conformer_z"] = {"PC-Conformer_z_E": ["0.0", "0.3"]}

    return {
        "PC-Compound_atoms": {
            "PC-Atoms": {
                "PC-Atoms_aid": {"PC-Atoms_aid_E": ["1", "2"]},
                "PC-Atoms_element": {
                    "PC-Element": [{"@value": "C"}, {"@value": "O"}]
                },
            }
        },
        "PC-Compound_coords": {
            "PC-Coordinates": {"PC-Coordinates_conformers": {"PC-Conformer": conformer}}
        },
        "PC-Compound_bonds": {
            "PC-Bonds": {
                "PC-Bonds_aid1": {"PC-Bonds_aid1_E": ["1"]},
                "PC-Bonds_aid2": {"PC-Bonds_aid2_E": ["2"]},
                "PC-Bonds_order": {"PC-BondType": [{"#text": "2"}]},
            }
        },
    }


JSON_MOLECULE = {
    "atoms": {"aid": [1, 2], "element": [6, 8]},
    "coords": [
        {"conformers": [{"x": [0.0, 1.2], "y": [0.0, 0.4], "z": [0.0, 0.3]}]}
    ],
    "bonds": {"aid1": [1], "aid2": [2], "order": [2]},
}


@pytest.mark.parametrize("coords_z", [True, False])
def test_xml_parse_molecule_data(coords_z):
    atoms, bonds = XMLParser.parse_molecule_data(xml_molecule(coords_z))

    assert set(atoms) == {1, 2}
    assert atoms[1]["element"] == "C"
    assert atoms[1]["coords"].shape == (3,)
    assert bonds[0]["bond_type"] == 2


def test_xml_extract_atoms_rejects_bad_structure():
    with pytest.raises(Exception):
        XMLParser.extract_atoms_data({"PC-Compound_atoms": {"PC-Atoms": "bad"}})


def test_xml_data_parser_needs_xmltodict():
    with pytest.raises(Exception):
        XMLParser.data_parser("<PC-Compounds></PC-Compounds>")


def test_json_data_parser_single_molecule():
    data = json.dumps({"molecule": [JSON_MOLECULE]})

    parsed = JSONParser.data_parser(data)

    assert len(parsed) == 1
    atoms, bonds = parsed[0]
    assert atoms[1]["element"] == "C"
    assert atoms[2]["element"] == "O"
    assert isinstance(atoms[1]["coords"], np.ndarray)
    assert bonds[0]["to_atom_index"] == 2


def test_json_extract_atoms_without_z():
    molecule = {
        "atoms": {"aid": [1], "element": [6]},
        "coords": [{"conformers": [{"x": [0.0], "y": [0.0]}]}],
        "bonds": {"aid1": [], "aid2": [], "order": []},
    }

    atoms, bonds = JSONParser.parse_single_molecule_data(molecule)

    assert atoms[1]["coords"].tolist() == [0.0, 0.0, 0.0]
    assert bonds == {}


@pytest.mark.parametrize(
    "molecule",
    [
        {"atoms": "bad"},
        {"atoms": {"aid": [], "element": [6]}},
        {"atoms": {"aid": [1], "element": []}},
        {"atoms": {"aid": [1], "element": [6]}, "coords": [0]},
        {"atoms": {"aid": [1], "element": [6]}, "coords": [{"conformers": [0]}]},
        {"atoms": {"aid": [1], "element": [6]}, "coords": [], "bonds": "bad"},
    ],
)
def test_json_extract_requires_valid_data(molecule):
    with pytest.raises(Exception):
        JSONParser.parse_single_molecule_data(molecule)
