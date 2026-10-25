# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Manim chemistry bond representation.

This module provides the MCBond class for representing chemical bonds in molecules.

"""

from __future__ import annotations

from typing import Dict, Optional, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from .mc_atom import MCAtom
    from .mc_molecule import MCMolecule

BOND_TYPES = {
    1: "simple",
    2: "double",
    3: "triple",
}

STEREO_TYPES = {
    1: "plain_cram",
    2: "dash_cram",
}


class MCBond:
    """
    MCBond: Abstraction of a bond in a molecule: Type of bond, from and to atoms.

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
    """

    def __init__(
        self,
        bond_type: int,
        from_atom: Optional[MCAtom]=None,
        to_atom: Optional[MCAtom]=None,
        stereo: Optional[int] = None,
        molecule_index: Optional[int] = None,
        topology: Optional[int] = None,
        reacting_center_status: Optional[int] = None,
    ):
        """Initialize MCBond with bond type, connected atoms, stereo info and metadata."""
        self.bond_type = bond_type
        self.from_atom = from_atom
        self.to_atom = to_atom
        self.stereo = stereo
        self.molecule_index = molecule_index
        self.topology = topology
        self.reacting_center_status = reacting_center_status

    def assign_from_atom(self, from_atom: MCAtom):
        """Set the atom the bond originates from.

        Parameters
        ----------
        from_atom
            Atom the bond starts from.
        """
        self.from_atom = from_atom

    def assign_to_atom(self, to_atom: MCAtom):
        """Set the atom the bond points to.

        Parameters
        ----------
        to_atom
            Atom the bond ends at.
        """
        self.to_atom = to_atom

    def assign_stereo(self, stereo: Optional[int]):
        """Set the stereochemistry type of the bond.

        Parameters
        ----------
        stereo
            Stereo type of the bond.
        """
        self.stereo = stereo

    @staticmethod
    def construct_from_bond_dict(bond_index: int, bond_data_dict: Dict, molecule: MCMolecule) -> Self:
        """
        Given a bond data dict from a parser, returns an MCBond.

        Parameters
        ----------
        bond_index
            Index of the bond in the molecule.
        bond_data_dict
            See data_parser function from BaseParser.
        molecule
            MCMolecule: Required to get the atoms by their index and
            create the MCBond using MCAtoms.

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