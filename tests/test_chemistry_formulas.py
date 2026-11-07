# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the chemistry formula mobjects."""

import pytest
from manim import BLUE, DOWN, GREEN, RED, UP, WHITE

from manim_extensions.chemistry.twoD.chemical_formula import (
    ChemicalFormula,
    ComplexFormula,
    NamedComplexFormula,
    NamedFormula,
)


@pytest.mark.parametrize(
    "formula",
    ["H2O", "NaCl", "Fe2O3", "CaCO3", "Mg(OH)2"],
)
def test_chemical_formula_renders_known_compounds(formula):
    mob = ChemicalFormula(formula)

    assert mob.formula == formula
    assert mob.width > 0
    assert mob.height > 0


def test_chemical_formula_parse_and_markup():
    mob = ChemicalFormula("Fe2O3", metal_color=BLUE, oxygen_color=RED)

    assert mob.parsed_formula == {"Fe": 2, "O": 3}
    assert "Fe" in mob.make_markup(mob.parsed_formula, metal_color=BLUE, oxygen_color=RED)


@pytest.mark.parametrize("formula", ["H2O", "CO2"])
def test_chemical_formula_colours_each_element(formula):
    mob = ChemicalFormula(
        formula,
        metal_color=BLUE,
        non_metal_color=GREEN,
        oxygen_color=RED,
    )

    assert mob.metal_color is BLUE
    assert mob.non_metal_color is GREEN
    assert mob.oxygen_color is RED


def test_complex_formula_keeps_parenthesised_groups():
    mob = ComplexFormula({"Ca": BLUE, "(OH)2": RED})

    assert mob.width > 0
    assert mob.height > 0


@pytest.mark.parametrize("direction", [DOWN, UP])
@pytest.mark.parametrize("spanish_structure", [True, False])
def test_named_formula_layout(direction, spanish_structure):
    mob = NamedFormula(
        "Sodio",
        "Cloro",
        "NaCl",
        metal_color=BLUE,
        non_metal_color=GREEN,
        direction=direction,
        spanish_structure=spanish_structure,
    )

    assert mob.metal_name == "Sodio"
    assert mob.non_metal_name == "Cloro"
    assert mob.formula == "NaCl"
    assert len(mob.submobjects) >= 2


def test_named_formula_defaults_to_white():
    mob = NamedFormula("Sodio", "Cloro", "NaCl")

    assert mob.metal_color is WHITE
    assert mob.non_metal_color is WHITE


def test_named_complex_formula_pairs_name_with_group():
    mob = NamedComplexFormula(
        {"Calcio": BLUE},
        {"Ca": BLUE, "(OH)2": RED},
    )

    assert mob.name_dict == {"Calcio": BLUE}
    assert mob.formula_dict == {"Ca": BLUE, "(OH)2": RED}
    assert len(mob.submobjects) >= 2
