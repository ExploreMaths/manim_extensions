# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""2D atom representation for Manim chemistry.

This module provides the MAtomObject class for representing atoms in 2D chemical structures.

"""

from manim import Dot, LEFT, ManimColor, MarkupText, RIGHT, VGroup, WHITE
import numpy as np
from typing import Dict, Any, Optional


class MAtomObject(VGroup):
    """A 2D visual representation of an atom in a chemical molecule.

    Parameters
    ----------
    coords : np.array, optional
        Position of the atom. Defaults to ``np.array([0, 0, 0])``.
    element : str, optional
        Chemical symbol of the element. Defaults to ``"H"``.
    explicit_carbons : bool, optional
        If True, carbon atoms display their element symbol. Defaults to
        ``False``.
    explicit_hydrogens : bool, optional
        If True, hydrogen atoms display their element symbol. Defaults to
        ``False``.
    bond_to : Dict[int, Any], optional
        Mapping of bonded atom indices to their elements. Defaults to
        ``{}``.
    representation_type : Optional[str], optional
        Representation of the atom label: ``'complete'`` (always show the
        symbol), ``'skeleton'`` (hide it), or ``'over_bond'`` (show it
        above the bond). When None it is inferred from the element.
    color : str, optional
        Color of the atom label. Defaults to ``WHITE``.
    charge : int, optional
        Formal charge of the atom. Defaults to ``0``.
    index : int, optional
        Index of the atom in the molecule. Defaults to ``0``.
    planar : bool, optional
        If True, forces the z coordinate of ``coords`` to zero. Defaults
        to ``True``.
    **kwargs
        Additional keyword arguments forwarded to
        :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: MAtomObjectExample
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.twoD.atom import MAtomObject

       class MAtomObjectExample(Scene):
           def construct(self):
               self.add(MAtomObject(element="O"))
    """
    def __str__(self):
        return f"MAtomObject of element {self.element}"

    def __repr__(self):
        return f"MAtomObject of element {self.element}"

    def __init__(
        self,
        coords: np.array = np.array([0, 0, 0]),
        element: str = "H",
        explicit_carbons: bool = False,
        explicit_hydrogens: bool = False,
        bond_to: Dict[int, Any] = {},
        representation_type: Optional[str] = None,
        color: str = WHITE,
        charge: int = 0,
        index: int = 0,
        planar: bool = True,
        **kwargs,
    ):
        """Initialize a 2D atom with element symbol, coords, bond info and display options."""
        VGroup.__init__(self, **kwargs)
        self.coords = coords
        self.element = element
        self.explicit_carbons = explicit_carbons
        self.explicit_hydrogens = explicit_hydrogens
        self.bond_to = bond_to
        self.representation_type = representation_type
        self.representation = self.set_representation(representation_type)
        self.charge = charge
        self.index = index
        self.planar = planar
        self.color = color
        self.atom = self.add_atom()

        if self.planar:
            self.coords[2] = 0

        if self.atom:
            self.add(self.atom)

        else:
            self.add(Dot(radius=0))
        self.move_to(self.coords)
        self.set_atom_color(self.color)

    def set_representation(self, representation_type: Any):
        """
        - 'complete': Adds the element symbol.
        - 'skeleton': Does not add the symbol
        - 'over_bond': Adds the symbol above the bond

        Parameters
        ----------
        representation_type : :class:`~typing.Any`
            Representation type of the atom.
        """
        if representation_type:
            return representation_type

        if self.element == "C":  # and not self.explicit_carbons:
            representation_type = "skeleton"

        elif self.element == "H":
            if self.explicit_hydrogens:
                representation_type = "complete"
            elif self.bond_to and "C" not in self.bond_to.values():
                representation_type = "complete"
            elif not self.explicit_hydrogens:  # TODO: Rethink this logic
                representation_type = "skeleton"
        else:
            representation_type = "complete"

        return representation_type

    def add_atom(self):
        """
        Adds an atom depending on the representation
        """
        if self.representation != "skeleton":
            return MarkupText(self.element).scale(0.8)

    def bonds_fulfilled(self):
        """Check if the atom has its expected minimum number of bonds."""
        minimum_bonds = {"O": 2, "S": 2, "N": 3, "P": 3}
        minimum_bond = minimum_bonds.get(self.element)
        if self.bond_to and minimum_bond:
            return len(self.bond_to) == minimum_bonds.get(self)

        return True

    def make_copy(self):
        """Create a copy of this atom preserving all properties and coordinates."""
        copy = MAtomObject(
            coords=self.coords,
            element=self.element,
            explicit_carbons=self.explicit_carbons,
            explicit_hydrogens=self.explicit_hydrogens,
            bond_to=self.bond_to,
            representation_type=self.representation_type,
            color=self.color,
            charge=self.charge,
            index=self.index,
            planar=self.planar,
        )
        return copy

    def rename_atom(self, new_element: Any, bonds_direction: Any):
        """Replace this atom's element with new_element and adjust position by bond direction.

        Parameters
        ----------
        new_element : :class:`~typing.Any`
            Element symbol of the new atom.
        bonds_direction : :class:`~typing.Any`
            Direction of the bond, used to shift the renamed atom.
        """
        self.element = new_element
        renamed_atom = self.make_copy()

        original_width = self.width
        new_width = renamed_atom.width

        width_difference = new_width - original_width
        if bonds_direction > 0:
            renamed_atom.shift(width_difference / 1.5 * RIGHT)

        else:
            renamed_atom.shift(width_difference / 1.5 * LEFT)

        return renamed_atom

    def copy_with_explicit_hydrogens(self):
        """Return a copy of this atom with explicit hydrogens enabled."""
        self.explicit_hydrogens = True

        return self.make_copy()

    def set_atom_color(self, color: ManimColor):
        """
        TODO: Add the color depending on cpk convention

        Parameters
        ----------
        color : :class:`~manim.utils.color.core.ManimColor`
            New color of the atom.
        """
        pass