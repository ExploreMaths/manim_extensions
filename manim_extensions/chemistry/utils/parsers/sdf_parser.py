# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""SDF format parser for chemical files.

This module provides the :class:`~manim_extensions.chemistry.utils.parsers.sdf_parser.SDFParser` class for parsing SDF format chemical files.

"""

# unlinked-class-ok: Molecules

from typing import List

from .base_parser import AtomsDict, BondsDict, FilePath
from .mol_parser import MolParser


class SDFParser(MolParser):
    """Parses sdf files.
    The sdf format is very similar to the mol format. It only contains some
    extra lines. By modifying the read file and removing those extra lines we
    can use the logic already implemented in :class:`~manim_extensions.chemistry.utils.parsers.mol_parser.MolParser`.

    The main difference between an sdf file and a mol file is an sdf file
    supports having multiple molecules, so we are returning a list of molecules
    instead of a single molecule.

    Examples
    --------
    .. nbcell::
       :files: acetone_2d.sdf

       parsed_sdf = SDFParser(filename="acetone_2d.sdf")
       print(parsed_sdf.molecular_data[0][0])

    .. nbcell::

       print(parsed_sdf.molecular_data[0][1])

    """

    @staticmethod
    def read_file(filename: FilePath) -> List[List[str]]:
        """
        sdf files might contain multiple molecules, so we return a list of list
        of string when reading a file.

        Parameters
        ----------
        filename
            Path of the sdf file.

        Returns
        -------
            List with all the molecules data.
        """
        with open(filename) as file:
            sdf_file_data = file.read()

        sdf_molecules = sdf_file_data.split("$$$$")
        return [molecule.split("\n") for molecule in sdf_molecules if molecule.strip()]

    @staticmethod
    def data_parser(
        molecules_data: List[List[str]],
    ) -> List[tuple[AtomsDict, BondsDict]]:
        """Parse the molecules of an SDF file into a list of atoms and bonds dicts.

        Parameters
        ----------
        molecules_data
            Molecules of the SDF file as returned by :meth:`~manim_extensions.chemistry.utils.parsers.sdf_parser.SDFParser.read_file`.

        Returns
        -------
            List of ``(atoms_data, bonds_data)`` tuples, one per molecule.
        """
        return [MolParser.data_parser(data) for data in molecules_data]
