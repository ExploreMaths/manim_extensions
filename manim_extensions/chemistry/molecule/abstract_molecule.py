# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Abstract molecule base class for Manim chemistry.

This module provides the :class:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule` class as a template for all molecule implementations.

"""

from manim import DOWN, Tex, Text, VGroup
from typing import Dict, Literal, Self
from manim.mobject.opengl.opengl_mobject import OpenGLGroup
from abc import abstractmethod


from ..utils import PubchemAPIManager
from ..manim_chemistry_molecule import MCMolecule
from manim.typing import Vector3D


class AbstractMolecule:
    """
    Abstract molecule class used as a template to create
    all the other molecule classes.

    Parameters
    ----------
    args
        Positional arguments passed to subclass implementations.
    **kwargs
        Additional keyword arguments passed to subclass implementations.
    """

    group_class = VGroup

    def __init__(self, *args, **kwargs): ...

    @classmethod
    def molecule_from_file(
        cls,
        filepath: str,
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict | None = None,
        *args,
        **kwargs,
    ) -> Self:
        """
        Reads a string and returns a single molecule from the parsed data.


        Parameters
        ----------
        filepath
            Path to the file.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data.
        **kwargs
            Additional keyword arguments passed to the molecule constructor.

        Returns
        -------
            :class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule` from the file.
        """
        mc_molecule = MCMolecule.construct_from_file(
            filepath=filepath,
            ignore_hydrogens=ignore_hydrogens,
            ignore_all_hydrogens=ignore_all_hydrogens,
            elements_data_dict=elements_data_dict,
        )
        if isinstance(mc_molecule, list):
            mc_molecule = mc_molecule[0]

        vertices, edges = cls.mc_molecule_to_atoms_and_bonds(mc_molecule=mc_molecule)
        return cls(vertices, edges, *args, **kwargs)

    @classmethod
    def multiple_molecules_from_file(
        cls,
        filepath: str,
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict | None = None,
        *args,
        **kwargs,
    ) -> OpenGLGroup | VGroup:
        """
        Reads a file and returns a collection of molecules from that file as a OpenGLGroup or :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

        Parameters
        ----------
        filepath
            Path to the molecule.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data.
        **kwargs
            Additional keyword arguments passed to the molecule constructor.

        Returns
        -------
            OpenGLGroup with the molecules inside.

        Raises
        ------
        Exception
            In case the mc_molecules parsed is not a list.
        """
        mc_molecules = MCMolecule.construct_multiples_from_file(
            filepath=filepath,
            ignore_hydrogens=ignore_hydrogens,
            ignore_all_hydrogens=ignore_all_hydrogens,
            elements_data_dict=elements_data_dict,
        )

        if not isinstance(mc_molecules, list):
            raise Exception(f"Expected a list of molecules. Received {mc_molecules}")

        mmolecules = cls.group_class()
        for mc_molecule in mc_molecules:
            atoms, bonds = cls.mc_molecule_to_atoms_and_bonds(mc_molecule=mc_molecule)
            mmolecules.add(cls(atoms, bonds, *args, **kwargs))

        return mmolecules

    @classmethod
    def molecule_from_string(
        cls,
        string: str,
        format: Literal["mol", "sdf", "asnt", "json", "xml"] = "json",
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict | None = None,
        *args,
        **kwargs,
    ) -> Self:
        """
        Reads a string and returns a single molecule from the parsed data.


        Parameters
        ----------
        string
            String with the molecule data.
        format
            Format of the data.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data.
        **kwargs
            Additional keyword arguments passed to the molecule constructor.

        Returns
        -------
            :class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule` from the string.
        """

        mc_molecule = MCMolecule.construct_from_string(
            string=string,
            format=format,
            ignore_hydrogens=ignore_hydrogens,
            ignore_all_hydrogens=ignore_all_hydrogens,
            elements_data_dict=elements_data_dict,
        )
        if isinstance(mc_molecule, list):
            mc_molecule = mc_molecule[0]

        vertices, edges = cls.mc_molecule_to_atoms_and_bonds(mc_molecule=mc_molecule)
        return cls(vertices, edges, *args, **kwargs)

    @classmethod
    def multiple_molecules_from_string(
        cls,
        string: str,
        format: Literal["mol", "sdf", "asnt", "json", "xml"] = "json",
        ignore_hydrogens: bool = True,
        ignore_all_hydrogens: bool = False,
        elements_data_dict: dict | None = None,
        *args,
        **kwargs,
    ) -> OpenGLGroup:
        """
        Reads a file and returns a collection of molecules from that file as a OpenGLGroup.

        Parameters
        ----------
        string
            String with the molecule data.
        format
            Format of the data.
        ignore_hydrogens
            Whether to remove hydrogens bonded to carbon atoms.

        ignore_all_hydrogens
            Whether to remove every hydrogen atom.
        elements_data_dict
            Dictionary of custom element data.
        **kwargs
            Additional keyword arguments passed to the molecule constructor.

        Returns
        -------
            OpenGLGroup with the molecules inside.

        Raises
        ------
        Exception
            In case the mc_molecules parsed is not a list.
        """

        mc_molecules = MCMolecule.construct_multiples_from_string(
            string=string,
            format=format,
            ignore_hydrogens=ignore_hydrogens,
            ignore_all_hydrogens=ignore_all_hydrogens,
            elements_data_dict=elements_data_dict,
        )

        if not isinstance(mc_molecules, list):
            raise Exception(f"Expected a list of molecules. Received {mc_molecules}")

        mmolecules = OpenGLGroup()
        for mc_molecule in mc_molecules:
            atoms, bonds = cls.mc_molecule_to_atoms_and_bonds(mc_molecule=mc_molecule)
            mmolecules.add(cls(atoms, bonds, *args, **kwargs))

        return mmolecules

    @classmethod
    def molecule_from_pubchem(
        cls,
        cid: str | None = None,
        name: str | None = None,
        smiles: str | None = None,
        inchi: str | None = None,
        three_d: bool = False,
        elements_data_dict: dict | None = None,
        *args,
        **kwargs,
    ) -> Self:
        """
        Generates a :class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule` from an identifier using PubChem API.

        Parameters
        ----------
        cid
            :class:`~manim_extensions.chemistry.molecule.molecule.Molecule` cid.
        name
            :class:`~manim_extensions.chemistry.molecule.molecule.Molecule` name.
        smiles
            :class:`~manim_extensions.chemistry.molecule.molecule.Molecule` SMILES.
        inchi
            :class:`~manim_extensions.chemistry.molecule.molecule.Molecule` InChi.
        three_d
            Whether to use three-dimensional data of the molecule.

        elements_data_dict
            Dictionary of custom element data.
        **kwargs
            Additional keyword arguments passed to the molecule constructor.

        Returns
        -------
            GraphMolecule.
        """
        pubchem_api_manager = PubchemAPIManager(
            cid=cid, name=name, smiles=smiles, inchi=inchi, three_d=three_d
        )

        return cls.molecule_from_string(
            string=pubchem_api_manager.get_molecule(),
            format="json",
            elements_data_dict=elements_data_dict,
            *args,
            **kwargs,
        )

    @classmethod
    @abstractmethod
    def mc_molecule_to_atoms_and_bonds(
        cls, mc_molecule: MCMolecule
    ) -> tuple[Dict, Dict]:
        """
        Transforms the structure of a mc_molecule to a (vertices, edges) tuple.

        The tuple has the following structure:

        .. code-block:: text

           Vertices: {<atom_index>: MCAtom}
           Edges: {(<from_atom_index>, <to_atom_index>): MCBond}

        Parameters
        ----------
        mc_molecule
            The :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule` object to transform.

        Returns
        -------
            A tuple containing atoms and bonds dictionaries.
        """
        ...

    def add_molecule_name(
        self,
        name: Text | Tex | str,
        direction: Vector3D = DOWN,
        buff: float = 0.5,
        scale: float = 0.75,
    ) -> Self:
        r"""Adds the name of the molecule.

        Parameters
        ----------
        name
            Name of the molecule. Can either be a string, a Manim Tex or a Manim Text.
        direction
            Position where to set the molecule name.
        buff
            Distance between the name and the molecule.
        scale
            Scale of the text.

        Returns
        -------
            The object itself, for method chaining.


        Examples
        ----------
        .. manim:: MMoleculeWithName
           :files: acetone_2d.mol
           :save_last_frame:

            from manim import *
            from pathlib import Path
            from manim_extensions.chemistry import MMoleculeObject

            class MMoleculeWithName(Scene):
                def construct(self):
                    molecule = MMoleculeObject.molecule_from_string(
                        Path("acetone_2d.mol").read_text(), format="mol"
                    )
                    self.add(molecule)
                    molecule.add_molecule_name(name="Acetone")
                    self.add(molecule[-1])

        .. manim:: GraphMoleculeWithName
           :files: acetone_2d.mol
           :save_last_frame:

            from manim import *
            from pathlib import Path
            from manim_extensions.chemistry import GraphMolecule

            class GraphMoleculeWithName(Scene):
                def construct(self):
                    molecule = GraphMolecule.molecule_from_string(
                        Path("acetone_2d.mol").read_text(), format="mol"
                    )
                    self.add(molecule)
                    molecule.add_molecule_name(name="Acetone")
                    self.add(molecule.submobjects[-1])
        """

        if isinstance(name, str):
            name = Text(name)

        name.scale(scale).next_to(self, direction=direction, buff=buff)
        self.add(name)
        return self
