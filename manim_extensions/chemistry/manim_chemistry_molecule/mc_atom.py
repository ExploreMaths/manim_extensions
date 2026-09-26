# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Manim chemistry atom representation.

This module provides the MCAtom class for representing atoms in molecules.

"""

from typing import Any, Dict, Optional

import numpy as np

from .mc_element import MC_ELEMENT_DICT, MCElement


class MCAtom:
    """
    Abstraction of an atom in a molecule:
    - It's MCElement.
    - It's 3D coordinates.
    - The atoms bonded to it.
    - The bonds associated with it.
    - It's molecule.
    - It's index in the molecule.

    Parameters
    ----------
    element : :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom.MCElement`
        The chemical element of the atom.
    coords : :class:`numpy.array`, optional
        3D coordinates of the atom. Defaults to the origin.
    atoms : :class:`list`, optional
        List of bonded atoms. Defaults to an empty list.
    bonds : :class:`list`, optional
        List of bonds associated with the atom. Defaults to an empty list.
    molecule : :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_atom.MCAtom.MCMolecule`, optional
        The molecule the atom belongs to. Defaults to ``None``.
    molecule_index : :class:`int`, optional
        Index of the atom in the molecule. Defaults to ``None``.
    """

    def __init__(
        self,
        element: MCElement,
        coords: np.array = np.array([0, 0, 0]),
        atoms: Optional[list] = None,
        bonds: Optional[list] = None,
        molecule: Optional[None] = None,
        molecule_index: Optional[int] = None,
    ):
        """Initialize MCAtom with element, 3D coordinates, bonded atoms, bonds and molecule reference."""
        self.element = element
        self.coords = coords
        self.atoms = atoms or []
        self.bonds = bonds or []
        self.molecule = molecule
        self.molecule_index = molecule_index

    def add_atoms(self, atoms: Any):
        """
        Assigns bonded atoms to MCAtom.

        Parameters
        ----------
        atoms : MCAtom or List[MCAtom]
            Bonded atoms to assign.

        Raises
        ------
        Exception
            In case the atoms are not MCAtoms or a list.
        """
        if not atoms:
            pass

        if not isinstance(atoms, MCAtom) and not isinstance(atoms, list):
            raise Exception(
                f"Expected {MCAtom} or list of {MCAtom} when assigning atoms but received {atoms}"
            )

        if isinstance(self.atoms, list) and isinstance(atoms, MCAtom):
            self.atoms.append(atoms)

        if isinstance(self.atoms, list) and isinstance(atoms, list):
            if not all([isinstance(atom, MCAtom) for atom in atoms]):
                raise Exception(
                    f"Expected {MCAtom} or list of {MCAtom} when assigning atoms but received {atoms}"
                )

            self.atoms.extend(atoms)

        return self.atoms

    def add_bonds(self, bonds: Any):
        """Add one or more MCBond objects to the atom's bond list.

        Parameters
        ----------
        bonds : MCBond or List[MCBond]
            Bonds to assign to the atom.

        Raises
        ------
        Exception
            Raised when ``bonds`` is neither an MCBond nor a list of
            MCBonds.
        """
        from .mc_bond import MCBond

        if not bonds:
            pass

        if not isinstance(bonds, MCBond) and not isinstance(bonds, list):
            raise Exception(
                f"Expected {MCBond} or list of {MCBond} when assigning atoms but received {bonds}"
            )

        if isinstance(self.bonds, list) and isinstance(bonds, MCBond):
            self.bonds.append(bonds)

        if isinstance(self.bonds, list) and isinstance(bonds, list):
            if not all([isinstance(bond, MCBond) for bond in bonds]):
                raise Exception(
                    f"Expected {MCBond} or list of {MCBond} when assigning atoms but received {bonds}"
                )

            self.bonds.extend(bonds)

        return self.bonds

    def assign_molecule(self, molecule: Any):
        """Set the parent MCMolecule this atom belongs to.

        Parameters
        ----------
        molecule : MCMolecule
            The molecule the atom belongs to.

        Raises
        ------
        Exception
            Raised when ``molecule`` is not an MCMolecule.
        """
        from .mc_molecule import MCMolecule

        if not molecule:
            pass

        if not isinstance(molecule, MCMolecule):
            raise Exception(
                f"Expected {MCMolecule} when assigning molecule but received {molecule}"
            )

        self.molecule = molecule

        return self.molecule

    def assign_molecule_index(self, molecule_index: int):
        """Set the index of this atom within its parent molecule.

        Parameters
        ----------
        molecule_index : :class:`int`
            Index of the atom in the molecule.

        Raises
        ------
        Exception
            Raised when ``molecule_index`` is not an int.
        """
        if isinstance(molecule_index, None):
            pass

        if not isinstance(molecule_index, int):
            raise Exception(
                f"Expected {int} when assigning molecule_index but received {molecule_index}"
            )

        self.molecule_index = molecule_index

        return self.molecule_index

    @staticmethod
    def construct_from_atom_dict(
        atom_index: Any, atom_data_dict: Dict, elements_data_dict: Dict
    ):
        """
        Given an atom data dict from a parser, returns an MCAtom.

        Parameters
        ----------
        atom_dict : Dict
            See data_parser function from BaseParser.
        atom_index : Any
            Index of the atom in the molecule.
        atom_data_dict : Dict
            See data_parser function from BaseParser.
        elements_data_dict : Dict
            Dictionary of custom element data to merge over the
            default elements data.

        Output:
            MCAtom.

        Raises
        ------
        Exception
            Raised when ``atom_data_dict`` is not a dict, when it has no
            ``element`` entry, when the element is unknown, or when the
            coordinates are not numeric.
        """

        if not isinstance(atom_data_dict, dict):
            raise Exception(f"Expected {dict} but received {atom_data_dict}")

        element = atom_data_dict.get("element", None)

        if not element:
            raise Exception(
                f"Atom dict {atom_data_dict} does not contain element data."
            )

        if element not in MC_ELEMENT_DICT:
            raise Exception(
                f"Element {element} does not match any known element by human kind. Is that an alien element?"
            )

        mc_element_dict = MC_ELEMENT_DICT.copy()

        if elements_data_dict:
            mc_element_dict |= elements_data_dict

        mc_element = mc_element_dict.get(element)

        coords = atom_data_dict.get("coords")

        if not isinstance(coords, (np.ndarray, np.generic)) and not isinstance(
            coords, list
        ):
            raise Exception(f"Coordinates {coords} are not correct coordinates.")

        return MCAtom(element=mc_element, coords=coords, molecule_index=atom_index)