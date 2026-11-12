# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

""":class:`~manim_extensions.chemistry.molecule.molecule.Molecule` proxy class for Manim chemistry.

This module provides the :class:`~manim_extensions.chemistry.molecule.molecule.Molecule` class as a unified interface for different molecule types.

"""

from ..twoD import GraphMolecule

from manim import VGroup


class Molecule:
    r"""Works as a proxy between different types of molecules with the same methods.

    Supported types of molecules are:

    - :class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule`
    - :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`
    - :class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule`

    Parameters
    ----------
    molecule_class
        The molecule class to proxy to, such as :class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule`,
        :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` or :class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule`.

    Examples
    ---------
    .. manim:: GraphMoleculeFromMolecule
       :files: acetone_2d.mol
       :save_last_frame:

       from manim import *
       from pathlib import Path
       from manim_extensions.chemistry import GraphMolecule, Molecule

       class GraphMoleculeFromMolecule(Scene):
           def construct(self):
               molecule = Molecule(GraphMolecule).molecule_from_string(
                   Path("acetone_2d.mol").read_text(), format="mol"
               )
               label = Text(f"type: {type(molecule).__name__}").to_edge(UP)
               self.add(molecule)
               self.add(label)

    .. manim:: MMoleculeObjectFromMolecule
       :files: acetone_2d.mol
       :save_last_frame:

       from manim import *
       from pathlib import Path
       from manim_extensions.chemistry import MMoleculeObject, Molecule

       class MMoleculeObjectFromMolecule(Scene):
           def construct(self):
               molecule = Molecule(MMoleculeObject).molecule_from_string(
                   Path("acetone_2d.mol").read_text(), format="mol"
               )
               label = Text(f"type: {type(molecule).__name__}").to_edge(UP)
               self.add(molecule)
               self.add(label)
    """

    def __init__(self, molecule_class: type[GraphMolecule] = GraphMolecule):
        self.molecule_class = molecule_class

    def molecule_from_file(self, *args, **kwargs) -> GraphMolecule:
        """Delegate to the wrapped molecule class to construct a molecule from a file.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments forwarded to
            :meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.molecule_from_file`
            of the wrapped molecule class.

        Returns
        -------
            The computed result.
        """
        return self.molecule_class.molecule_from_file(*args, **kwargs)

    def multiple_molecules_from_file(self, *args, **kwargs) -> VGroup:
        """Delegate to the wrapped molecule class to construct multiple molecules from a file.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments forwarded to
            :meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.multiple_molecules_from_file`
            of the wrapped molecule class.

        Returns
        -------
            The computed result.
        """
        return self.molecule_class.multiple_molecules_from_file(*args, **kwargs)

    def molecule_from_string(self, *args, **kwargs) -> GraphMolecule:
        """Delegate to the wrapped molecule class to construct a molecule from a string.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments forwarded to
            :meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.molecule_from_string`
            of the wrapped molecule class.

        Returns
        -------
            The computed result.
        """
        return self.molecule_class.molecule_from_string(*args, **kwargs)

    def multiple_molecules_from_string(self, *args, **kwargs) -> VGroup:
        """Delegate to the wrapped molecule class to construct multiple molecules from a string.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments forwarded to
            :meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.multiple_molecules_from_string`
            of the wrapped molecule class.

        Returns
        -------
            The computed result.
        """
        return self.molecule_class.multiple_molecules_from_string(*args, **kwargs)

    def molecule_from_pubchem(self, *args, **kwargs) -> GraphMolecule:
        """Delegate to the wrapped molecule class to fetch a molecule from PubChem.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments forwarded to
            :meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.molecule_from_pubchem`
            of the wrapped molecule class.

        Returns
        -------
            The computed result.
        """
        return self.molecule_class.molecule_from_pubchem(*args, **kwargs)

    def mc_molecule_to_atoms_and_bonds(self, *args, **kwargs) -> tuple[dict, dict]:
        """Delegate to the wrapped molecule class to convert an :class:`~manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule.MCMolecule` to atoms and bonds.

        Parameters
        ----------
        **kwargs
            Additional keyword arguments forwarded to
            :meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.mc_molecule_to_atoms_and_bonds`
            of the wrapped molecule class.

        Returns
        -------
            The computed result.
        """
        return self.molecule_class.mc_molecule_to_atoms_and_bonds(*args, **kwargs)
