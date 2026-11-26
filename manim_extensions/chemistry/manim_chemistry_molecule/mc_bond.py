# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""Manim chemistry bond representation.

This module provides the :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond` class for representing chemical bonds in molecules.

"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .mc_atom import MCAtom
    from .mc_molecule import MCMolecule

#: Mapping from bond order (`1`, `2`, `3`) to the bond type name.
BOND_TYPES = {
    1: "simple",
    2: "double",
    3: "triple",
}

#: Mapping from stereo bond code to the stereo type name.
STEREO_TYPES = {
    1: "plain_cram",
    2: "dash_cram",
}


class MCBond:
    """:class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond`: Abstraction of a bond in a molecule: Type of bond, from and to atoms.

    Parameters
    ----------
    bond_type
        Type of the bond: 1 for simple, 2 for double, 3 for triple.
    from_atom
        Atom the bond starts from.
    to_atom
        Atom the bond ends at.
    stereo
        Stereo type of the bond.
    molecule_index
        Index of the bond in the molecule.
    topology
        Topology of the bond.
    reacting_center_status
        Reacting center status of the bond.

    Examples
    --------
    .. manim:: MCBondOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.manim_chemistry_molecule.mc_bond import MCBond

       MCBondTarget = MCBond

       class MCBondOverview(Scene):
           def construct(self):
               public = [n for n in dir(MCBondTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('MCBond', font_size=36),
                   Text('module: manim_extensions.chemistry.manim_chemistry_molecule.mc_bond', font_size=18, color=GREY),
                   Text('manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond: Abstraction of a bond in a molecule: Type of bond, from and to atoms', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        import numpy as np
        from manim_extensions.chemistry.manim_chemistry_molecule.mc_atom import MCAtom
        from manim_extensions.chemistry.manim_chemistry_molecule.mc_bond import MCBond
        from manim_extensions.chemistry.manim_chemistry_molecule.mc_element import MC_ELEMENT_DICT

        atom_a = MCAtom(MC_ELEMENT_DICT["C"], coords=np.array([0.0, 0.0, 0.0]))
        atom_b = MCAtom(MC_ELEMENT_DICT["O"], coords=np.array([1.0, 0.0, 0.0]))
        bond = MCBond(bond_type=1, from_atom=atom_a, to_atom=atom_b)
    """

    def __init__(
        self,
        bond_type: int,
        from_atom: MCAtom | None = None,
        to_atom: MCAtom | None = None,
        stereo: int | None = None,
        molecule_index: int | None = None,
        topology: int | None = None,
        reacting_center_status: int | None = None,
    ) -> None:
        self.bond_type = bond_type
        self.from_atom = from_atom
        self.to_atom = to_atom
        self.stereo = stereo
        self.molecule_index = molecule_index
        self.topology = topology
        self.reacting_center_status = reacting_center_status

    def assign_from_atom(self, from_atom: MCAtom) -> Any:
        """Set the atom the bond originates from.



        from_atom
            Atom the bond starts from.




            The resulting value.
        """
        self.from_atom = from_atom

    def assign_to_atom(self, to_atom: MCAtom) -> Any:
        """Set the atom the bond points to.



        to_atom
            Atom the bond ends at.




            The resulting value.
        """
        self.to_atom = to_atom

    def assign_stereo(self, stereo: int | None) -> Any:
        """Set the stereochemistry type of the bond.



        stereo
            Stereo type of the bond.




            The resulting value.
        """
        self.stereo = stereo

    @staticmethod
    def construct_from_bond_dict(
        bond_index: int, bond_data_dict: dict[Any, Any], molecule: MCMolecule
    ) -> "MCBond":
        r"""
        Given a bond data dict from a parser, returns an :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond`.

        Parameters
        ----------
        bond_index
            Index of the bond in the molecule.
        bond_data_dict
            See data_parser function from :class:`~manim_extensions.chemistry.utils.parsers.base_parser.BaseParser`.
        molecule
            :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule`: Required to get the atoms by their index and
            create the :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_bond.MCBond` using :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom`\ s.

        Returns
        -------
            The constructed bond.

        Raises
        ------
        Exception
            Raised when ``bond_data_dict`` is not a dict, when it has no
            ``to_atom_index`` or ``from_atom_index`` entries, or when the
            bond type is unknown.
        """

        if not isinstance(bond_data_dict, dict):
            raise Exception(f"Expected {dict} but received {bond_data_dict}")

        bond_type = bond_data_dict.get("bond_type", None)

        if not bond_type:
            raise Exception(
                f"Bond with index {bond_index} does not contain bond type data. Bond data: {bond_data_dict}"
            )

        try:
            from_atom_index = bond_data_dict.get("from_atom_index", None)
            from_mc_atom = molecule.atoms_by_index[from_atom_index]

            to_atom_index = bond_data_dict.get("to_atom_index", None)
            to_mc_atom = molecule.atoms_by_index[to_atom_index]

        except Exception as error:
            raise Exception(
                f"Bond dict {bond_data_dict} does not contain the expected data for molecule {molecule}. Error: {error}"
            )

        return MCBond(
            bond_type=bond_type,
            from_atom=from_mc_atom,
            to_atom=to_mc_atom,
            molecule_index=bond_index,
            stereo=bond_data_dict.get("stereo"),
            topology=bond_data_dict.get("topology"),
            reacting_center_status=bond_data_dict.get("reacting_center_status"),
        )
