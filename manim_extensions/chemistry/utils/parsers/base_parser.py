# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Base parser class for chemical file formats.

This module provides the BaseParser abstract class for parsing chemical files.

"""

from abc import ABC, abstractmethod
import os
from typing import Any, Union


#: Path-like value accepted by the parsers: a string, raw bytes or a PathLike.
FilePath = Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]
#: Parsed atoms data: ``{atom_index: {property: value}}``.
AtomsDict = dict[int, dict[str, Any]]
#: Parsed bonds data: ``{bond_index: {property: value}}``.
BondsDict = dict[int, dict[str, Any]]
#: Parsed data of a single molecule.
MoleculeData = tuple[AtomsDict, BondsDict]
#: Parsed data of one or more molecules.
ParsedData = Union[MoleculeData, list[MoleculeData]]


class BaseParser(ABC):
    """Initializes the parser given a file name.

    This is a base class that must be extended on child classes.

    The purposes of the parser classes are:

    - Read a file with chemical data.
    - Parse the file to extract the atoms and bonds data.
    - Return a dictionary with the atoms and bonds data.

    Parameters
    ----------
    filename : :class:`str`, :class:`~manim_extensions.chemistry.utils.parsers.base_parser.BaseParser.bytes` or Path-like
        Path to the file to parse.

    """

    def __init__(self, filename: FilePath) -> None:
        """Read and parse the chemistry file."""
        self.file_data: Any = self.read_file(filename)
        parsed_data = self.parse_file_data()
        if isinstance(parsed_data, list):
            self.molecular_data: list[MoleculeData] | None = parsed_data
            self.atoms_data: AtomsDict | None = None
            self.bonds_data: BondsDict | None = None

        else:
            self.molecular_data = None
            self.atoms_data, self.bonds_data = parsed_data

    @staticmethod
    @abstractmethod
    def read_file(filename: FilePath) -> Any:
        """
        Reads the file and converts it to a string.

        Parameters
        ----------
        filename : :data:`~manim_extensions.chemistry.utils.parsers.base_parser.FilePath`
            Path to the file to parse.

        Returns
        -------
        str
            String with the file data.
        """
        ...

    @staticmethod
    @abstractmethod
    def data_parser(data: Any) -> ParsedData:
        """Parses the atoms and bonds data and returns a tuple of dictionaries with each data.

        The atom data follows the structure:

            {<atom_index>: {"element": <atom_element>, "position": [<x_pos>, <y_pos>, <z_pos>]}}

        The bond data follows the structure:

            {<bond_index>: {"from_atom_index": <from_atom_index>, "to_atom_index": <to_atom_index>, "bond_type": <bond_type>}}

        Parameters
        ----------
        data : :class:`~typing.Any`
            Raw file data as returned by :meth:`~manim_extensions.chemistry.utils.parsers.base_parser.BaseParser.read_file`.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.ParsedData`
            Parsed ``(atoms_data, bonds_data)`` tuple, or a list of such
            tuples for multi-molecule formats.
        """
        ...

    def parse_file_data(self) -> ParsedData:
        """
        Receives the file data as a string and uses the string_parser.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.ParsedData`
            (atom_data, bond_data)
        """
        return self.data_parser(self.file_data)

    @property
    def molecule_data(self) -> ParsedData:
        """
        Returns molecule data: atoms_data and bonds_data.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.ParsedData`
            Parsed molecule data.

        Raises
        ------
        Exception
            Raised when the atoms data, bonds data, and molecular data are
            all missing or invalid.
        """

        if self.atoms_data and self.bonds_data:
            return self.atoms_data, self.bonds_data

        elif self.molecular_data:
            return self.molecular_data

        raise Exception(
            f"Atoms data, bonds data and molecular data are not correct: {self.atoms_data} {self.bonds_data} {self.molecular_data}"
        )

    @property
    def atoms(self) -> AtomsDict | None:
        """
        Returns atoms data.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.AtomsDict` or None
            Parsed atoms data.
        """

        return self.atoms_data

    @property
    def bonds(self) -> BondsDict | None:
        """
        Returns bonds data.

        Returns
        -------
        :data:`~manim_extensions.chemistry.utils.parsers.base_parser.BondsDict` or None
            Parsed bonds data.
        """

        return self.bonds_data

