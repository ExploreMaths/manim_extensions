# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the ASNT molecule data parser."""

from manim_extensions.chemistry.utils.parsers.asnt_parser import ASNTParser

COORD = "{2, 1, 0}"


def build_lines(bond_types=("1", "1"), pad=10):
    lines = [
        "atoms",
        "{",
        "1",
        "2",
        "}",
        "{",
        "C",
        "O",
        "}",
        "}",
        "bonds",
        "aid1",
        "1",
        "2",
        "}",
        "aid2",
        "2",
        "1",
        "}",
        "aid2",
        *bond_types,
        "}",
        "conformers",
        "{",
        "x",
        *([COORD] * pad),
    ]
    return lines


def test_data_parser_returns_atoms_and_bonds():
    atoms, bonds = ASNTParser.data_parser(build_lines())

    assert set(atoms) == {1, 2}
    assert atoms[1]["element"] == "C"
    assert atoms[2]["element"] == "O"
    assert atoms[1]["coords"].shape[-1] == 3
    assert len(bonds) == 2


def test_bond_type_mapping_is_applied():
    _, bonds = ASNTParser.data_parser(build_lines(bond_types=("double", "triple")))

    assert bonds[0]["bond_type"] == 2
    assert bonds[1]["bond_type"] == 3


def test_unknown_bond_type_falls_back_to_single():
    _, bonds = ASNTParser.data_parser(build_lines(bond_types=("9", "1")))

    assert bonds[0]["bond_type"] == 1


def test_replace_stuff_rewrites_tokens():
    assert ASNTParser.replace_stuff("atoms") == '"atoms"'
    assert ASNTParser.replace_stuff("{2, 1, 0}") == "[2, 1, 0]"
    assert ASNTParser.replace_stuff("}") == "}"
