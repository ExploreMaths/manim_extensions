# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Chemical formula representation for Manim chemistry.

This module provides the ChemicalFormula class for rendering chemical formulas.

"""

import re

from manim import DEFAULT_MOBJECT_TO_MOBJECT_BUFFER, DOWN, ManimColor, MarkupText, VGroup, WHITE


from typing import Any
class ChemicalFormula(MarkupText):
    """
    Mostly usefull for simple compounds like binary salts or oxoanions.

    Parameters
    ----------
    formula : :class:`str`
        The chemical formula to render, e.g. ``"H2O"``.
    metal_color : :class:`str`, optional
        Color of the metal element. Defaults to ``WHITE``.
    non_metal_color : :class:`str`, optional
        Color of the non-metal element. Defaults to ``WHITE``.
    oxygen_color : :class:`str`, optional
        Color of the oxygen element. Defaults to ``WHITE``.
    args
        Additional positional arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.ChemicalFormula.MarkupText`.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.ChemicalFormula.MarkupText`.
    """

    def __init__(
        self,
        formula: str,
        metal_color: str = WHITE,
        non_metal_color: str = WHITE,
        oxygen_color: str = WHITE,
        *args,
        **kwargs,
    ):
        """Initialize a chemical formula text with per-element colors and subscript numbers."""
        self.formula = formula
        self.metal_color = metal_color
        self.non_metal_color = non_metal_color
        self.oxygen_color = oxygen_color
        self.parsed_formula = self.parse_formula(self.formula)
        markup = self.make_markup(
            parsed_formula=self.parsed_formula,
            metal_color=self.metal_color,
            non_metal_color=self.non_metal_color,
            oxygen_color=self.oxygen_color,
        )

        super().__init__(markup, *args, **kwargs)

    def parse_formula(self, formula: str):
        """Parse a formula string into a dict mapping element symbols to their counts.

        Parameters
        ----------
        formula : :class:`str`
            The chemical formula to parse, e.g. ``"H2O"``.
        """
        FORMULA_PATTERN = r"([A-Z][a-z]*)(\d*)"
        elements = re.findall(FORMULA_PATTERN, formula)
        parsed_formula = {}
        for element, count in elements:
            count = int(count) if count else 1
            parsed_formula[element] = count

        return parsed_formula

    def make_markup(
        self,
        parsed_formula: Any,
        metal_color: str = WHITE,
        non_metal_color: str = WHITE,
        oxygen_color: str = WHITE,
    ):
        """Build Pango markup string with colored elements and subscripted counts.

        Parameters
        ----------
        parsed_formula : :class:`~typing.Any`
            Parsed formula mapping element symbols to their counts.
        metal_color : :class:`str`, optional
            Color of the metal element. Defaults to ``WHITE``.
        non_metal_color : :class:`str`, optional
            Color of the non-metal element. Defaults to ``WHITE``.
        oxygen_color : :class:`str`, optional
            Color of the oxygen element. Defaults to ``WHITE``.
        """
        parsed_list = enumerate(list(parsed_formula))
        markup = ""

        for index, atom in parsed_list:
            if atom == "O":
                markup += self.set_atom_color(atom, parsed_formula[atom], oxygen_color)
            elif index == 0:
                markup += self.set_atom_color(atom, parsed_formula[atom], metal_color)
            elif index == 1:
                markup += self.set_atom_color(
                    atom, parsed_formula[atom], non_metal_color
                )

        return markup

    def set_atom_color(self, atom: Any, subindex: Any, color: ManimColor):
        """Wrap an atom symbol and its subscript count in a colored span tag.

        Parameters
        ----------
        atom : :class:`~typing.Any`
            Element symbol of the atom.
        subindex : :class:`~typing.Any`
            Subscript count of the atom.
        color : :class:`~manim.utils.color.core.ManimColor`
            Color of the atom text.
        """
        colored_atom = f"<span fgcolor='{color}'>{atom}"

        if subindex > 1:
            colored_atom += f"<sub>{str(subindex)}</sub>"

        colored_atom += "</span>"

        return colored_atom


class NamedFormula(VGroup):
    """A chemical formula together with its name.

    Parameters
    ----------
    metal_name : :class:`str`
        Name of the metal element.
    non_metal_name : :class:`str`
        Name of the non-metal element.
    formula : :class:`str`
        The chemical formula to render.
    metal_color : :class:`str`, optional
        Color of the metal element. Defaults to ``WHITE``.
    non_metal_color : :class:`str`, optional
        Color of the non-metal element. Defaults to ``WHITE``.
    oxygen_color : :class:`str`, optional
        Color of the oxygen element. Defaults to ``WHITE``.
    font : :class:`str`, optional
        Font of the name text. Defaults to ``""``.
    spanish_structure : :class:`bool`, optional
        Whether to use the spanish name ordering (non-metal first).
        Defaults to ``False``.
    buff : :class:`float`, optional
        Distance between the formula and its name. Defaults to
        ``DEFAULT_MOBJECT_TO_MOBJECT_BUFFER``.
    direction
        Direction in which the name is placed relative to the formula.
        Defaults to :class:`~manim.constants.DOWN`.
    args
        Additional positional arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.NamedFormula.VGroup`.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.NamedFormula.VGroup`.

    Examples
    --------
    .. manim:: NamedFormulaExample
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.twoD.chemical_formula import NamedFormula

       class NamedFormulaExample(Scene):
           def construct(self):
               self.add(NamedFormula("Sodio", "Cloro", "NaCl",
                                     metal_color=BLUE, non_metal_color=GREEN))
    """

    def __init__(
        self,
        metal_name: str,
        non_metal_name: str,
        formula: str,
        metal_color: str = WHITE,
        non_metal_color: str = WHITE,
        oxygen_color: str = WHITE,
        font: str = "",
        spanish_structure: bool = False,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        direction: str = DOWN,
        *args,
        **kwargs,
    ):
        """Initialize a named formula with metal/non-metal names, colors and layout options."""
        super().__init__(*args, **kwargs)
        self.metal_name = metal_name
        self.non_metal_name = non_metal_name
        self.formula = formula
        self.metal_color = metal_color
        self.non_metal_color = non_metal_color
        self.oxygen_color = oxygen_color
        self.spanish_structure = spanish_structure
        self.font = font
        chemical_formula = ChemicalFormula(
            formula=self.formula,
            metal_color=self.metal_color,
            non_metal_color=self.non_metal_color,
            oxygen_color=self.oxygen_color,
            *args,
            **kwargs,
        )
        self.add(chemical_formula)
        self.name = self.make_name().next_to(
            chemical_formula, direction=direction, buff=buff
        )
        self.add(self.name)

    def make_name(self):
        """
        Not all languages use the same naming structure.
        For example, in english NaCl is Sodium (Na) Chloride (Cl)
        while in spanish it is Cloruro (Cl) Sódico (Na). Reimplement it
        as you need.
        """

        metal_text = None
        non_metal_text = None

        if self.metal_name:
            metal_text = f"<span fgcolor='{self.metal_color}'>{self.metal_name}</span>"

        if self.non_metal_name:
            non_metal_text = (
                f"<span fgcolor='{self.non_metal_color}'>{self.non_metal_name}</span>"
            )

        if self.spanish_structure:
            return MarkupText(
                " ".join(filter(None, [non_metal_text, metal_text])), font=self.font
            )

        return MarkupText(
            " ".join(filter(None, [metal_text, non_metal_text])), font=self.font
        )


class ComplexFormula(MarkupText):
    """
    Allows the creation of more complex molecular formulas
    using a dictionary. The key is the string to be written
    and the value is a color.

    Parameters
    ----------
    formula_dict : :class:`dict`
        Dictionary mapping formula strings to their colors.
    args
        Additional positional arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.ComplexFormula.MarkupText`.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.ComplexFormula.MarkupText`.
    """

    def __init__(self, formula_dict: dict, *args, **kwargs):
        """Initialize a complex formula from a dict of formula parts mapped to colors."""
        markup = ""
        for formula, color in formula_dict.items():
            markup += (
                f"<span fgcolor='{color}'>{self.make_formula_structure(formula)}</span>"
            )

        super().__init__(markup, *args, **kwargs)

    def add_tags_around_numbers(self, formula_part: Any):
        """Wrap trailing numbers in formula parts with HTML subscript tags.

        Parameters
        ----------
        formula_part : :class:`~typing.Any`
            Formula string to add subscript tags to.
        """
        pattern = r"([^\d\s]+)(\d+)"
        replacement = r"\1<sub>\2</sub>"
        result = re.sub(pattern, replacement, formula_part)
        return result

    def add_tags_around_charges(self, formula_part: Any):
        """Wrap charge notation (^{...}) with HTML superscript tags.

        Parameters
        ----------
        formula_part : :class:`~typing.Any`
            Formula string to add superscript tags to.
        """
        pattern = re.compile(r"(\w*?)\^\{([^}]+)\}")
        substitution = r"\1<sup>\2</sup>"
        result_string = re.sub(pattern, substitution, formula_part)

        return result_string

    def make_formula_structure(self, formula_part: Any):
        """Apply subscript and superscript formatting to a formula string.

        Parameters
        ----------
        formula_part : :class:`~typing.Any`
            Formula string to add subscript and superscript tags to.
        """
        result = self.add_tags_around_numbers(formula_part)
        result = self.add_tags_around_charges(result)

        return result


class NamedComplexFormula(VGroup):
    """
    Complex formula build with two dicts.

    Parameters
    ----------
    name_dict : :class:`dict`
        Dictionary mapping name strings to their colors.
    formula_dict : :class:`dict`
        Dictionary mapping formula strings to their colors.
    direction
        Direction in which the name is placed relative to the formula.
        Defaults to :class:`~manim.constants.DOWN`.
    buff : :class:`float`, optional
        Distance between the formula and its name. Defaults to
        ``DEFAULT_MOBJECT_TO_MOBJECT_BUFFER``.
    args
        Additional positional arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.NamedComplexFormula.VGroup`.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.twoD.chemical_formula.NamedComplexFormula.VGroup`.

    Examples
    --------
    .. manim:: NamedComplexFormulaExample
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.twoD.chemical_formula import NamedComplexFormula

       class NamedComplexFormulaExample(Scene):
           def construct(self):
               self.add(NamedComplexFormula(
                   {"Cloruro de sodio": BLUE},
                   {"NaCl": WHITE},
               ))
    """

    def __init__(
        self,
        name_dict: dict,
        formula_dict: dict,
        direction: str = DOWN,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        *args,
        **kwargs,
    ):
        """Initialize a named complex formula built from name and formula dictionaries."""
        self.name_dict = name_dict
        self.formula_dict = formula_dict
        super().__init__(*args, **kwargs)

        complex_formula = ComplexFormula(formula_dict)
        self.add(complex_formula)
        name = MarkupText(self.build_name()).next_to(complex_formula, direction, buff)

        self.add(name)

    def build_name(self):
        """Build colored markup text from the name dictionary entries."""
        markup = ""
        for name, color in self.name_dict.items():
            markup += f"<span fgcolor='{color}'>{name} </span>"

        return markup