# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the 2D molecule animation builder."""

import pytest
from manim import Dot, Line, ORIGIN, PI, RED, RIGHT, Text, VGroup, tempconfig

from manim_extensions.chemistry.twoD.animations import GMAnimationBuilder
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


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


@pytest.fixture()
def builder():
    molecule = GraphMolecule.molecule_from_string(MOL, format="mol")
    return GMAnimationBuilder(
        molecule,
        atoms=VGroup(*molecule.vertices.values()),
        bonds=VGroup(*molecule.edges.values()),
    )


def test_builder_collects_atoms_and_bonds(builder):
    assert len(builder.atoms) == 3
    assert len(builder.bonds) == 2


def test_bonds_from_atoms_finds_matching_bond(builder):
    bond = builder.bonds_from_atoms(1, 2)

    assert isinstance(bond, tuple)


def test_bonds_from_atoms_raises_for_unknown_pair(builder):
    with pytest.raises(Exception):
        builder.bonds_from_atoms(1, 9)


def test_rotate_atoms_about_bond_returns_animations(builder):
    animations = builder.rotate_atoms_about_bond(1, 3, angle=PI / 4)

    assert len(animations) >= 1


@pytest.fixture()
def labeled_builder():
    molecule = GraphMolecule.molecule_from_string(MOL, format="mol")
    atom_mobjects = VGroup(*(VGroup(Dot(), Text("C")) for _ in range(3)))
    bond_mobjects = VGroup(*(Line(ORIGIN, RIGHT) for _ in range(2)))
    return GMAnimationBuilder(molecule, atoms=atom_mobjects, bonds=bond_mobjects)


def test_change_color_without_label_color(labeled_builder):
    animations = labeled_builder.change_color(atoms_color=RED)

    assert len(animations) >= 1


def test_change_color_with_labels_and_bonds(labeled_builder):
    animations = labeled_builder.change_color(
        atoms_color=RED, bonds_color=RED, label_color=RED
    )

    assert len(animations) >= 1
