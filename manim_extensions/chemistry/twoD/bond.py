# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""2D bond representation for Manim chemistry.

This module provides bond classes for representing chemical bonds in 2D.

"""

from manim import Line, Mobject, PI, Polygram, VGroup, VMobject, WHITE
import numpy as np
from .atom import MAtomObject


from typing import Any
class BaseMBondObject(VGroup):
    """Abstract base class for 2D chemical bond mobjects between two atoms.

    Parameters
    ----------
    from_atom : MAtomObject
        Atom at the start of the bond.
    to_atom : MAtomObject
        Atom at the end of the bond.
    type : int, optional
        Bond type: 1 for single, 2 for double, 3 for triple. Defaults to
        ``0``.
    subtype : str, optional
        Subtype of the bond (e.g. ``'shorter'``, ``'shorter_from'``,
        ``'shorter_to'``). Defaults to ``''``.
    color : str, optional
        Color of the bond. Defaults to ``WHITE``.
    index : int, optional
        Index of the bond in the molecule. Defaults to ``0``.
    **kwargs
        Additional keyword arguments forwarded to
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: BaseMBondObjectExample
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.chemistry.twoD.atom import MAtomObject
       from manim_extensions.chemistry.twoD.bond import BaseMBondObject, SimpleBond

       class BaseMBondObjectExample(Scene):
           def construct(self):
               # BaseMBondObject is abstract: create_line() must be
               # implemented by subclasses such as SimpleBond.
               carbon = MAtomObject(element="C")
               oxygen = MAtomObject(element="O", coords=np.array([1.6, 0, 0]))
               bond = SimpleBond(carbon, oxygen)
               assert isinstance(bond, BaseMBondObject)
               content = VGroup(carbon, oxygen, bond)
               content.scale_to_fit_width(6).move_to(ORIGIN)
               self.add(content)
    """
    def __str__(self):
        return f"MBondObject bonding {self.from_atom} with {self.to_atom}"

    def __repr__(self):
        return f"MBondObject bonding {self.from_atom} with {self.to_atom}"

    def __init__(
        self,
        from_atom: MAtomObject,
        to_atom: MAtomObject,
        type: int = 0,
        subtype: str = "",
        color: str = WHITE,
        index: int = 0,
        **kwargs,
    ):
        """Initialize a base bond between two atoms with type, subtype, color and index."""
        VGroup.__init__(self, **kwargs)
        self.from_atom = from_atom
        self.to_atom = to_atom
        self.type = type
        self.color = color
        self.subtype = self.define_subtype(subtype) or subtype
        self.bond = self.create_line()
        self.index = index
        self.add(self.bond)

    def define_subtype(self, subtype: str) -> str | bool:
        """
        Defines the subtype based on atoms' representations. Input options:
            - 'complete'
            - 'skeleton'
            - 'over_bond'

        Output options:
            - shorter: Does not touch the cener of the atoms.
            - shorter_from: Does not touch the center of the from atom.
            - shorter_to: Does not touch the center of the to atom.
            - None or false: Touches both atoms center

        Parameters
        ----------
        subtype : :class:`str`
            Subtype of the bond: ``'complete'``, ``'skeleton'`` or
            ``'over_bond'``.

        Returns
        -------
        :class:`str` or :class:`bool`
            One of ``'shorter'``, ``'shorter_from'``, ``'shorter_to'`` or
            ``False`` when the line touches both atom centers.
        """
        from_representation = self.from_atom.representation
        to_representation = self.to_atom.representation
        if from_representation == "complete":
            if to_representation == "complete":
                return "shorter"
            elif to_representation == "skeleton" or to_representation == "over_bond":
                return "shorter_from"

        if from_representation == "skeleton" or to_representation == "over_bond":
            if to_representation == "complete":
                return "shorter_to"
            elif to_representation == "skeleton" or to_representation == "over_bond":
                return False

        return False

    def atoms_in_bond(self):
        """Return a tuple of the two atoms connected by this bond."""
        return self.from_atom, self.to_atom

    def atom_is_in_bond(self, atom: Any):
        """Return True if the given atom is one of the two atoms in this bond.

        Parameters
        ----------
        atom : :class:`~typing.Any`
            Atom to check for membership in the bond.
        """
        if self.from_atom == atom or self.to_atom == atom:
            return True
        else:
            return False

    def get_bond_index_by_atom(self, atom: Any):
        """Return the bond's index if the atom is part of this bond, otherwise None.

        Parameters
        ----------
        atom : :class:`~typing.Any`
            Atom to check for membership in the bond.
        """
        if self.atom_is_in_bond(atom):
            return self.index

        return

    def add_bond_index_by_atom_to_list(self, atom: Any, list: list):
        """Append this bond's index to the given list if the atom is in the bond.

        Parameters
        ----------
        atom : :class:`~typing.Any`
            Atom to check for membership in the bond.
        list : :class:`list`
            List the bond index is appended to.
        """
        index = self.get_bond_index_by_atom(atom)

        if index is not None:
            list.append(index)

        return list

    def get_perpendicular_unit_vector(self, point_a: Any, point_b: Any):
        """Return a unit vector perpendicular to the bond direction, in the xy plane.

        Parameters
        ----------
        point_a : :class:`~typing.Any`
            Starting point of the bond.
        point_b : :class:`~typing.Any`
            Ending point of the bond.
        """
        direction = point_b - point_a
        if direction[0] == 0 and direction[1] == 0:
            perp_vector = np.cross(direction, np.array([0, 1, 0]))

        else:
            perp_vector = np.cross(direction, np.array([0, 0, 1]))

        return perp_vector / np.linalg.norm(perp_vector)

    def no_subtype(self):
        """
        To be implemented in every bond subclass.
        """
        pass

    def shorter_subtype(self):
        """
        To be implemented in every bond subclass.
        """
        pass

    def shorter_from_subtype(self):
        """
        To be implemented in every bond subclass.
        """
        pass

    def shorter_to_subtype(self):
        """
        To be implemented in every bond subclass.
        """
        pass

    def longer_subtype(self):
        """
        To be implemented in every bond subclass.
        """
        pass

    def create_line(self):
        """
        To be implemented in every bond subclass.
        """
        pass

    def get_vector(self):
        """
        All bonds should contain at least a Line. This line can return the corresponding vector.

        Raises
        ------
        exception
            Re-raised when the underlying line vector lookup fails.
        """
        try:
            return self[0].get_vector()

        except Exception as exception:
            raise exception


class SimpleBond(BaseMBondObject):
    """A single-line chemical bond between two atoms.

    Examples
    --------
    .. manim:: SimpleBondExample
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.chemistry.twoD.atom import MAtomObject
       from manim_extensions.chemistry.twoD.bond import SimpleBond

       class SimpleBondExample(Scene):
           def construct(self):
               carbon = MAtomObject(element="C")
               oxygen = MAtomObject(element="O", coords=np.array([1.6, 0, 0]))
               content = VGroup(carbon, oxygen, SimpleBond(carbon, oxygen))
               content.scale_to_fit_width(6).move_to(ORIGIN)
               self.add(content)
    """
    def no_subtype(self):
        """Return a full-length line connecting both atom centers."""
        return Line(self.from_atom.coords, self.to_atom.coords)

    def shorter_subtype(self):
        """Return a shorter line with buffer space at both atom ends."""
        return Line(self.from_atom.coords, self.to_atom.coords, buff=0.2)

    def shorter_from_subtype(self, direction: str):
        """Return a line shortened at the from-atom end, starting from the to atom.

        Parameters
        ----------
        direction : :class:`str`
            Direction from the to atom to the from atom.
        """
        return Line(self.to_atom.coords + direction * 0.8, self.to_atom.coords)

    def shorter_to_subtype(self, direction: str):
        """Return a line shortened at the to-atom end, starting from the from atom.

        Parameters
        ----------
        direction : :class:`str`
            Direction from the from atom to the to atom.
        """
        return Line(self.from_atom.coords, self.from_atom.coords - direction * 0.8)

    def longer_subtype(self):
        """Return a zero-length line at the from atom (degenerate bond)."""
        return Line(self.from_atom.coords, self.from_atom.coords)

    def create_line(self):
        """Build the bond line based on the configured subtype."""
        direction = self.from_atom.coords - self.to_atom.coords

        if not self.subtype:
            return self.no_subtype()

        else:
            subtypes = {
                "shorter": self.shorter_subtype(),
                "shorter_from": self.shorter_from_subtype(direction),
                "shorter_to": self.shorter_to_subtype(direction),
                "longer": self.longer_subtype(),
            }

            return subtypes.get(self.subtype) or VMobject()


class DoubleBond(BaseMBondObject):
    """A double bond between two atoms.

    Parameters
    ----------
    from_atom : :class:`~manim_extensions.chemistry.twoD.bond.DoubleBond.MAtomObject`
        The atom the bond starts from.
    to_atom : :class:`~manim_extensions.chemistry.twoD.bond.DoubleBond.MAtomObject`
        The atom the bond ends at.
    side : :class:`int`, optional
        Side of the double bond line. Defaults to 0.
    distance : :class:`float`, optional
        Distance between the two lines of the bond. Defaults to 0.15.
    double_bond_scale : :class:`float`, optional
        Scale applied to the secondary line of the bond. Defaults to 0.7.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.twoD.bond.DoubleBond.BaseMBondObject`.

    Examples
    --------
    .. manim:: DoubleBondExample
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.chemistry.twoD.atom import MAtomObject
       from manim_extensions.chemistry.twoD.bond import DoubleBond

       class DoubleBondExample(Scene):
           def construct(self):
               carbon = MAtomObject(element="C")
               oxygen = MAtomObject(element="O", coords=np.array([1.6, 0, 0]))
               content = VGroup(carbon, oxygen, DoubleBond(carbon, oxygen))
               content.scale_to_fit_width(6).move_to(ORIGIN)
               self.add(content)
    """

    def __init__(
        self, from_atom: Any, to_atom: Any, side: int = 0, distance: float = 0.15, double_bond_scale: float = 0.7, **kwargs
    ):
        """Initialize a double bond with side offset, line distance and scale parameters."""
        self.side = side
        self.distance = distance
        self.double_bond_scale = double_bond_scale
        super().__init__(from_atom, to_atom, **kwargs)

    def no_subtype(self):
        """Return two parallel lines: one full-length and one shorter offset line."""
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.15
        )  # TODO: Make this product value an option
        long_line = Line(self.from_atom.coords, self.to_atom.coords)
        short_line = Line(self.from_atom.coords, self.to_atom.coords, buff=0.15).shift(
            -unit_vector
        )  # TODO: Make the buff an option

        return VGroup(long_line, short_line)

    def shorter_subtype(self):
        """Return two parallel shortened lines offset perpendicularly from the bond axis."""
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.1
        )  # TODO: Make this product an option
        base_line = Line(self.from_atom.coords, self.to_atom.coords, buff=0.3).shift(
            unit_vector
        )  # Make this buff an option
        double_line = Line(self.from_atom.coords, self.to_atom.coords, buff=0.3).shift(
            -unit_vector
        )  # Make this buff an option

        return VGroup(base_line, double_line)

    def shorter_from_subtype(self, direction: str, from_surroundings: Any, to_surroundings: Any):
        """Return a double bond shortened at the from-atom end, with surroundings-aware layout.

        Parameters
        ----------
        direction : :class:`str`
            Direction from the to atom to the from atom.
        from_surroundings : :class:`~typing.Any`
            Whether the from atom has single bonds to hydrogens.
        to_surroundings : :class:`~typing.Any`
            Whether the to atom has single bonds to hydrogens.
        """
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.1
        )  # TODO: Make this product an option

        if not from_surroundings and not to_surroundings:
            base_line = (
                Line(self.to_atom.coords - 0.2 * direction, self.from_atom.coords)
                .scale(self.double_bond_scale)
                .shift(unit_vector)
            )
            double_line = base_line.copy().shift(-2 * unit_vector)

        else:
            base_line = Line(
                self.to_atom.coords, self.from_atom.coords - 0.25 * direction
            )
            double_line = (
                base_line.copy().scale(self.double_bond_scale).shift(1.5 * unit_vector)
            )  # TODO: Make this scale an option

        return VGroup(base_line, double_line)

    def shorter_to_subtype(self, direction: str, from_surroundings: Any, to_surroundings: Any):
        """Return a double bond shortened at the to-atom end, with surroundings-aware layout.

        Parameters
        ----------
        direction : :class:`str`
            Direction from the from atom to the to atom.
        from_surroundings : :class:`~typing.Any`
            Whether the from atom has single bonds to hydrogens.
        to_surroundings : :class:`~typing.Any`
            Whether the to atom has single bonds to hydrogens.
        """
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.1
        )  # TODO: Make this product an option

        if not from_surroundings and not to_surroundings:
            base_line = Line(
                self.from_atom.coords, self.to_atom.coords + 0.2 * direction
            ).shift(unit_vector)
            double_line = base_line.copy().shift(-2 * unit_vector)

        else:
            base_line = Line(
                self.from_atom.coords, self.to_atom.coords + 0.25 * direction
            )
            double_line = (
                base_line.copy().scale(self.double_bond_scale).shift(1.5 * unit_vector)
            )  # TODO: Make this scale an option

        return VGroup(base_line, double_line)

    def get_vector(self):
        """
        This contains a VGroup with two lines, we just get the vector from one of them.

        Raises
        ------
        exception
            Re-raised when the underlying line vector lookup fails.
        """
        try:
            return self[0][0].get_vector()

        except Exception as exception:
            raise exception

    def get_surroundings(self):
        """
        Checks the number of bonds of C atoms.
        Returns False if the C has a structure like central C in acetone:
            - Not bonded to H atoms.
            - Double bond to at least another atom.

        Otherwise returns True, resulting in a structure like the C with
        double bond to imidazole.

        TODO: Refactor this to make it more logical and way less verbose.
        """
        from_surroundings, to_surroundings = (False, False)
        if self.from_atom.bond_to:
            from_surroundings = (
                self.from_atom.element == "C"
                and len(self.from_atom.bond_to) < 4
                and "H" in self.from_atom.bond_to.values()
            )
        if self.to_atom.bond_to:
            to_surroundings = (
                self.to_atom.element == "C"
                and len(self.to_atom.bond_to) < 4
                and "H" in self.to_atom.bond_to.values()
            )

        return from_surroundings, to_surroundings

    def create_line(self):
        """Build the double bond VGroup based on the configured subtype."""
        from_surroundings, to_surroundings = self.get_surroundings()
        direction = self.from_atom.coords - self.to_atom.coords

        if not self.subtype:
            return self.no_subtype()

        else:
            subtypes = {
                "shorter": self.shorter_subtype(),
                "shorter_from": self.shorter_from_subtype(
                    direction=direction,
                    from_surroundings=from_surroundings,
                    to_surroundings=to_surroundings,
                ),
                "shorter_to": self.shorter_to_subtype(
                    direction,
                    from_surroundings=from_surroundings,
                    to_surroundings=to_surroundings,
                ),
            }

            return subtypes.get(self.subtype) or VMobject()


class TripleBond(BaseMBondObject):
    """A triple bond between two atoms.

    Parameters
    ----------
    from_atom : :class:`~manim_extensions.chemistry.twoD.bond.TripleBond.MAtomObject`
        The atom the bond starts from.
    to_atom : :class:`~manim_extensions.chemistry.twoD.bond.TripleBond.MAtomObject`
        The atom the bond ends at.
    side : :class:`int`, optional
        Side of the triple bond lines. Defaults to 0.
    distance : :class:`float`, optional
        Distance between the lines of the bond. Defaults to 0.3.
    triple_bond_scale : :class:`float`, optional
        Scale applied to the secondary lines of the bond. Defaults to 0.8.
    **kwargs
        Additional keyword arguments passed to :class:`~manim_extensions.chemistry.twoD.bond.TripleBond.BaseMBondObject`.

    Examples
    --------
    .. manim:: TripleBondExample
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.chemistry.twoD.atom import MAtomObject
       from manim_extensions.chemistry.twoD.bond import TripleBond

       class TripleBondExample(Scene):
           def construct(self):
               carbon = MAtomObject(element="C")
               oxygen = MAtomObject(element="O", coords=np.array([1.6, 0, 0]))
               content = VGroup(carbon, oxygen, TripleBond(carbon, oxygen))
               content.scale_to_fit_width(6).move_to(ORIGIN)
               self.add(content)
    """

    def __init__(
        self, from_atom: Any, to_atom: Any, side: int = 0, distance: float = 0.3, triple_bond_scale: float = 0.8, **kwargs
    ):
        """Initialize a triple bond with line distance and scale parameters."""
        self.distance = distance
        self.triple_bond_scale = triple_bond_scale
        super().__init__(from_atom, to_atom, **kwargs)

    def no_subtype(self):
        """Return three parallel lines forming a full triple bond."""
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.15
        )  # TODO: Make this value an option
        base_line = Line(self.from_atom.coords, self.to_atom.coords)
        double_line = base_line.copy().scale(self.triple_bond_scale).shift(unit_vector)
        triple_line = base_line.copy().scale(self.triple_bond_scale).shift(-unit_vector)

        return VGroup(base_line, double_line, triple_line)

    def shorter_subtype(self):
        """Return three parallel shortened lines forming a triple bond."""
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.15
        )  # TODO: Make this value an option
        base_line = Line(self.from_atom.coords, self.to_atom.coords, buff=0.25)
        double_line = base_line.copy().shift(unit_vector)
        triple_line = base_line.copy().shift(-unit_vector)

        return VGroup(base_line, double_line, triple_line)

    def shorter_from_subtype(self, direction: str):
        """Return a triple bond shortened at the from-atom end.

        Parameters
        ----------
        direction : :class:`str`
            Direction from the to atom to the from atom.
        """
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.15
        )  # TODO: Make this value an option
        base_line = Line(
            self.to_atom.coords - 0.1 * direction,
            self.to_atom.coords + 0.85 * direction,
        ).scale(self.triple_bond_scale)
        double_line = base_line.copy().scale(self.triple_bond_scale).shift(unit_vector)
        triple_line = base_line.copy().scale(self.triple_bond_scale).shift(-unit_vector)

        return VGroup(base_line, double_line, triple_line)

    def shorter_to_subtype(self, direction: str):
        """Return a triple bond shortened at the to-atom end.

        Parameters
        ----------
        direction : :class:`str`
            Direction from the from atom to the to atom.
        """
        unit_vector = (
            self.get_perpendicular_unit_vector(
                self.from_atom.coords, self.to_atom.coords
            )
            * 0.15
        )  # TODO: Make this value an option
        base_line = Line(
            self.from_atom.coords + 0.1 * direction,
            self.from_atom.coords - 0.85 * direction,
        ).scale(self.triple_bond_scale)
        double_line = base_line.copy().scale(self.triple_bond_scale).shift(unit_vector)
        triple_line = base_line.copy().scale(self.triple_bond_scale).shift(-unit_vector)

        return VGroup(base_line, double_line, triple_line)

    def longer_subtype(self, bond: Mobject, base_line: Mobject):
        """Add two offset parallel lines to form a triple bond from a base line.

        Parameters
        ----------
        bond : :class:`~manim.mobject.mobject.Mobject`
            Bond the lines are added to.
        base_line : :class:`~manim.mobject.mobject.Mobject`
            Base line the parallel lines are copied from.
        """
        bond.add(base_line)
        double_line = base_line.copy().scale(self.triple_bond_scale)
        triple_line = base_line.copy().scale(self.triple_bond_scale)
        pivot_line = (
            base_line.copy()
            .rotate(angle=PI / 2, about_point=base_line.get_center())
            .scale(self.distance)
        )
        double_line.move_to(pivot_line.get_end())
        triple_line.move_to(pivot_line.get_start())
        bond.add(double_line, triple_line)

    def create_line(self):
        """Build the triple bond VGroup based on the configured subtype."""
        direction = self.from_atom.coords - self.to_atom.coords

        if not self.subtype:
            return self.no_subtype()

        else:
            subtypes = {
                "shorter": self.shorter_subtype(),
                "shorter_from": self.shorter_from_subtype(direction=direction),
                "shorter_to": self.shorter_to_subtype(direction=direction),
            }

            return subtypes.get(self.subtype) or VMobject()

    def get_vector(self):
        """
        This contains a VGroup with two lines, we just get the vector from one of them.

        Raises
        ------
        exception
            Re-raised when the underlying line vector lookup fails.
        """
        try:
            return self[0][0].get_vector()

        except Exception as exception:
            raise exception


class PlainCramBond(BaseMBondObject):
    """A filled triangular wedge bond representing stereochemistry (coming out of the page).

    Examples
    --------
    .. manim:: PlainCramBondExample
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.chemistry.twoD.atom import MAtomObject
       from manim_extensions.chemistry.twoD.bond import PlainCramBond

       class PlainCramBondExample(Scene):
           def construct(self):
               carbon = MAtomObject(element="C")
               oxygen = MAtomObject(element="O", coords=np.array([1.6, 0, 0]))
               content = VGroup(carbon, oxygen, PlainCramBond(carbon, oxygen))
               content.scale_to_fit_width(6).move_to(ORIGIN)
               self.add(content)
    """
    def no_subtype(self):
        """Return a full triangular filled polygon representing a plain cram bond."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.to_atom.coords)
        pivot_line = (
            base_line.copy().rotate(angle=PI / 2).scale(0.3).shift(direction / 2)
        )
        cram_bond = Polygram(
            np.array([base_line.start, pivot_line.get_start(), pivot_line.get_end()]),
            color=self.color,
            fill_opacity=1,
        )

        return cram_bond

    def shorter_subtype(self):
        """Return a shortened triangular filled cram bond with buffer at both ends."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.to_atom.coords, buff=0.2)
        pivot_line = (
            base_line.copy().rotate(angle=PI / 2).scale(0.3).shift(direction / 2)
        )
        cram_bond = Polygram(
            np.array([base_line.start, pivot_line.get_start(), pivot_line.get_end()]),
            color=self.color,
            fill_opacity=1,
        )

        return cram_bond

    def shorter_from_subtype(self):
        """Return a triangular cram bond shortened at the from-atom end."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.to_atom.coords + direction * 0.2, self.to_atom.coords)
        pivot_line = (
            base_line.copy().rotate(angle=PI / 2).scale(0.4).shift(direction / 2)
        )
        cram_bond = Polygram(
            np.array([base_line.start, pivot_line.get_start(), pivot_line.get_end()]),
            color=self.color,
            fill_opacity=1,
        )

        return cram_bond

    def shorter_to_subtype(self):
        """Return a triangular cram bond shortened at the to-atom end."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.from_atom.coords + direction * 0.2)
        pivot_line = (
            base_line.copy().rotate(angle=PI / 2).scale(0.6).shift(direction / 2)
        )
        cram_bond = Polygram(
            np.array([base_line.start, pivot_line.get_start(), pivot_line.get_end()]),
            color=self.color,
            fill_opacity=1,
        )
        return cram_bond

    def longer_subtype(self):
        """Return a degenerate zero-length cram bond at the from atom."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.from_atom.coords)
        pivot_line = (
            base_line.copy().rotate(angle=PI / 2).scale(0.3).shift(direction / 2)
        )
        cram_bond = Polygram(
            np.array([base_line.start, pivot_line.get_start(), pivot_line.get_end()]),
            color=self.color,
            fill_opacity=1,
        )

        return cram_bond

    def create_line(self):
        """Build the plain cram bond polygon based on the configured subtype."""
        if not self.subtype:
            return self.no_subtype()

        else:
            subtypes = {
                "shorter": self.shorter_subtype(),
                "shorter_from": self.shorter_from_subtype(),
                "shorter_to": self.shorter_to_subtype(),
                "longer": self.longer_subtype(),
            }
            return subtypes.get(self.subtype) or VMobject()

    def get_vector(self):
        """Return the direction vector from the from-atom to the to-atom.

        Raises
        ------
        exception
            Re-raised when the underlying atom centers cannot be read.
        """
        try:
            atom_a, atom_b = self.atoms_in_bond()

            return atom_b.get_center() - atom_a.get_center()

        except Exception as exception:
            raise exception


class DashedCramBond(BaseMBondObject):
    """A dashed wedge bond representing stereochemistry (going into the page).

    Examples
    --------
    .. manim:: DashedCramBondExample
       :save_last_frame:

       import numpy as np
       from manim import *
       from manim_extensions.chemistry.twoD.atom import MAtomObject
       from manim_extensions.chemistry.twoD.bond import DashedCramBond

       class DashedCramBondExample(Scene):
           def construct(self):
               carbon = MAtomObject(element="C")
               oxygen = MAtomObject(element="O", coords=np.array([1.6, 0, 0]))
               content = VGroup(carbon, oxygen, DashedCramBond(carbon, oxygen))
               content.scale_to_fit_width(6).move_to(ORIGIN)
               self.add(content)
    """
    def add_dashed_cram_bond(self, base_line: Mobject, direction: str):
        """Build a dashed cram bond from progressively shorter perpendicular lines along the direction.

        Parameters
        ----------
        base_line : :class:`~manim.mobject.mobject.Mobject`
            Base line of the cram bond.
        direction : :class:`str`
            Direction of the cram bond.
        """
        pivot_line = base_line.copy().rotate(angle=PI / 2).scale(0.2)
        cram_bond = VGroup()
        direction_modulus = (
            direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2
        ) ** 0.5  # TODO: For sure numpy knows how to do this. Find how.
        increase = 0.05 / direction_modulus  # TODO: Change this 0.05 to be an option
        for i in range(
            int(direction_modulus * 5)
        ):  # TODO: Change this 5 to be an option
            cram_bond.add(Line(pivot_line.get_start(), pivot_line.get_end()))
            pivot_line.shift(direction * 0.16 / direction_modulus).scale(
                1 + increase / pivot_line.get_length()
            )  # TODO: Change this 5 to be an option
        return cram_bond

    def no_subtype(self):
        """Return a full-length dashed cram bond between both atoms."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.to_atom.coords)
        cram_bond = self.add_dashed_cram_bond(base_line=base_line, direction=direction)
        return cram_bond

    def shorter_subtype(self):
        """Return a shortened dashed cram bond with buffer space at both ends."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.to_atom.coords, buff=0.2)
        cram_bond = self.add_dashed_cram_bond(base_line=base_line, direction=direction)

        return cram_bond

    def shorter_from_subtype(self):
        """Return a dashed cram bond shortened at the from-atom end."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.to_atom.coords + direction * 0.2, self.to_atom.coords)
        cram_bond = self.add_dashed_cram_bond(base_line=base_line, direction=direction)

        return cram_bond

    def shorter_to_subtype(self):
        """Return a dashed cram bond shortened at the to-atom end."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.from_atom.coords + direction * 0.2)
        cram_bond = self.add_dashed_cram_bond(base_line=base_line, direction=direction)

        return cram_bond

    def longer_subtype(self):
        """Return a degenerate zero-length dashed cram bond at the from atom."""
        direction = self.to_atom.coords - self.from_atom.coords
        base_line = Line(self.from_atom.coords, self.from_atom.coords)
        cram_bond = self.add_dashed_cram_bond(base_line=base_line, direction=direction)

        return cram_bond

    def create_line(self):
        """Build the dashed cram bond VGroup based on the configured subtype."""
        if not self.subtype:
            return self.no_subtype()

        else:
            subtypes = {
                "shorter": self.shorter_subtype(),
                "shorter_from": self.shorter_from_subtype(),
                "shorter_to": self.shorter_to_subtype(),
                "longer": self.longer_subtype(),
            }

            return subtypes.get(self.subtype) or VMobject()

    def get_vector(self):
        """
        This contains a VGroup with two lines, we just get the vector from one of them.

        Raises
        ------
        exception
            Re-raised when the underlying line center lookup fails.
        """
        try:
            starting_line = self[0][0]
            ending_line = self[0][len(self[0]) - 1]
            return ending_line.get_center() - starting_line.get_center()

        except Exception as exception:
            raise exception