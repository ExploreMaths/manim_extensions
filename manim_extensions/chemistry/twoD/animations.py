# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Animation utilities for 2D chemistry molecules.

This module provides the :class:`~manim_extensions.chemistry.twoD.animations.GMAnimationBuilder` class for building molecule animations.

"""

from manim import Animation, BLACK, ManimColor, PI, VGroup
from .graph_molecule import GraphMolecule


class GMAnimationBuilder:
    r"""Builds animations for a :class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule`.

    Parameters
    ----------
    molecule
        The molecule the animations are built for.
    atoms
        The atoms to animate.
    bonds
        The bonds to animate.

    Examples
    --------
    .. manim:: GMAnimationBuilderDocExample
       :files: dimethylpropane.mol

       from manim import *
       from manim_extensions.chemistry import GMAnimationBuilder, GraphMolecule

       class GMAnimationBuilderDocExample(Scene):
           def construct(self):
               molecule = GraphMolecule.molecule_from_file(
                   "dimethylpropane.mol",
                   label=True,
                   numeric_label=True,
                   ignore_hydrogens=False,
               )
               atoms_and_bonds = molecule.get_connected_atoms_and_bonds(1, 3)
               animation_builder = GMAnimationBuilder(
                   molecule=molecule,
                   atoms=atoms_and_bonds[0],
                   bonds=atoms_and_bonds[1],
               )
               self.play(Write(molecule))
               self.play(animation_builder.rotate_atoms_about_bond(1, 3))
               self.wait()
               self.play(
                   animation_builder.change_color(
                       atoms_color=BLUE, bonds_color=RED, label_color=PINK
                   )
               )
               self.wait()
    """

    def __init__(
        self,
        molecule: GraphMolecule,
        atoms: VGroup | None = None,
        bonds: VGroup | None = None,
    ):
        self.molecule = molecule
        self.atoms = atoms or self.molecule.vertices.values()
        self.atoms_copy = self.atoms.copy()
        self.bonds = bonds or self.molecule.edges.values()
        self.bonds_copy = self.bonds.copy()

    def bonds_from_atoms(self, atom_a: int, atom_b: int) -> tuple[int, int]:
        """Find and return the bond edge connecting two atom indices in the molecule.

        Parameters
        ----------
        atom_a
            Index of one of the atoms of the bond.
        atom_b
            Index of the other atom of the bond.

        Returns
        -------
            The computed result.

        Raises
        ------
        Exception
            Raised when no bond exists between ``atom_a`` and ``atom_b``.
        """
        for bond in self.molecule.edges:
            if atom_a in bond and atom_b in bond:
                return bond

        raise Exception(f"No bond found for atoms {atom_a}, {atom_b}")

    def rotate_atoms_about_bond(
        self, atom_a: int, atom_b: int, angle: float = PI / 4
    ) -> list[Animation]:
        """Return animations rotating atoms around the bond axis between atom_a and atom_b.

        Parameters
        ----------
        atom_a
            Index of one of the atoms of the bond.
        atom_b
            Index of the other atom of the bond.
        angle
            Angle of the rotation.

        Returns
        -------
            The computed result.
        """
        bond = self.bonds_from_atoms(atom_a=atom_a, atom_b=atom_b)
        axis = self.molecule.edges[bond].sheen_direction
        self.atoms_copy.rotate(axis=axis, angle=angle)

        return [
            atom.animate.move_to(atom_copy)
            for atom, atom_copy in zip(self.atoms, self.atoms_copy)
        ]

    def change_color(
        self,
        atoms_color: ManimColor = BLACK,
        bonds_color: ManimColor | None = None,
        label_color: ManimColor | None = None,
    ) -> list:
        """Return color-change animations for atoms, bonds and optionally atom labels.

        Parameters
        ----------
        atoms_color
            New color of the atoms.
        bonds_color
            New color of the bonds. If ``None``, bonds keep their color.

        label_color
            New color of the atom labels. If ``None``, labels keep their
            color.

        Returns
        -------
            A list of the results.
        """
        animations = []

        if label_color:
            for atom in self.atoms:
                animations.append(atom[0].animate.set_color(atoms_color))
                animations.append(atom[1].animate.set_color(label_color))

        else:
            for atom in self.atoms:
                animations.append(atom[0].animate.set_color(atoms_color))
                animations.append(atom[1].animate.set_color(atom[1].color))

        if bonds_color:
            for bond in self.bonds:
                animations.append(bond.animate.set_color(bonds_color))

        return animations
