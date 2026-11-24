# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""SDF format parser for chemical files.

This module provides the :class:`~manim_extensions.chemistry.utils.parsers.sdf_parser.SDFParser` class for parsing SDF format chemical files.

"""

from typing import cast

# unlinked-class-ok: Molecules


from .base_parser import AtomsDict, BondsDict, FilePath, MoleculeData
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
    .. manim:: SDFParserOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.chemistry.utils.parsers.sdf_parser import SDFParser

       SDFParserTarget = SDFParser

       class SDFParserOverview(Scene):
           def construct(self):
               public = [n for n in dir(SDFParserTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('SDFParser', font_size=36),
                   Text('module: manim_extensions.chemistry.utils.parsers.sdf_parser', font_size=18, color=GREY),
                   Text('Parses sdf files. The sdf format is very similar to the mol format. It only contains some extra lines. By modifying the read file and removing those extra lines we can use the logic already implemented in manim_extensions.chemistry.utils.parsers.mol_parser.MolParser', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. nbcell::
       :files: acetone_2d.sdf

       from pprint import pprint

       parsed_sdf = SDFParser(filename="acetone_2d.sdf")
       pprint(parsed_sdf.molecular_data[0][0])

    .. nbcell::

       pprint(parsed_sdf.molecular_data[0][1])
    """

    @staticmethod
    def read_file(filename: FilePath) -> list[list[str]]:
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
        molecules_data: list[list[str]],
    ) -> list[tuple[AtomsDict, BondsDict]]:
        """Parse the molecules of an SDF file into a list of atoms and bonds dicts.

        Parameters
        ----------
        molecules_data
            Molecules of the SDF file as returned by :meth:`~manim_extensions.chemistry.utils.parsers.sdf_parser.SDFParser.read_file`.

        Returns
        -------
            List of ``(atoms_data, bonds_data)`` tuples, one per molecule.
        """
        return [
            cast(MoleculeData, MolParser.data_parser(data)) for data in molecules_data
        ]
