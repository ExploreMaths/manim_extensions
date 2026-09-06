# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Animation utilities for 2D chemistry molecules.

This module provides the GMAnimationBuilder class for building molecule animations.

"""


from manim import *
from .graph_molecule import GraphMolecule


class GMAnimationBuilder:
    """Builds animations for a :class:`~manim_extensions.chemistry.twoD.animations.GMAnimationBuilder.GraphMolecule`.

    Parameters
    ----------
    molecule : :class:`~manim_extensions.chemistry.twoD.animations.GMAnimationBuilder.GraphMolecule`
        The molecule the animations are built for.
    atoms : :class:`~manim_extensions.chemistry.twoD.animations.GMAnimationBuilder.VGroup`, optional
        The atoms to animate. Defaults to all vertices of the molecule.
    bonds : :class:`~manim_extensions.chemistry.twoD.animations.GMAnimationBuilder.VGroup`, optional
        The bonds to animate. Defaults to all edges of the molecule.

    Examples
    --------
    .. manim:: GMAnimationBuilderDocExample

        from manim import *
        from manim_extensions.chemistry import GMAnimationBuilder, GraphMolecule

        mol_file_data = (
            "10041\n"
            "  -OEChem-04292315533D\n"
            "\n"
            " 17 16  0     0  0  0  0  0  0999 V2000\n"
            "    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "   -1.3467    0.3727    0.6364 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    0.8961    1.2449   -0.0677 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "   -0.2359   -0.5385   -1.4183 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    0.6864   -1.0791    0.8496 C   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "   -1.2106    0.7613    1.6520 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "   -1.8616    1.1428    0.0510 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "   -2.0095   -0.4977    0.6985 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    1.8669    1.0100   -0.5184 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    1.0828    1.6532    0.9319 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    0.4318    2.0348   -0.6688 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "   -0.8737   -1.4294   -1.4026 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "   -0.7257    0.2109   -2.0501 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    0.7093   -0.8138   -1.8996 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    0.8684   -0.7234    1.8699 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    1.6524   -1.3666    0.4196 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "    0.0693   -1.9822    0.9165 H   0  0  0  0  0  0  0  0  0  0  0  0\n"
            "  1  2  1  0  0  0  0\n"
            "  1  3  1  0  0  0  0\n"
            "  1  4  1  0  0  0  0\n"
            "  1  5  1  0  0  0  0\n"
            "  2  6  1  0  0  0  0\n"
            "  2  7  1  0  0  0  0\n"
            "  2  8  1  0  0  0  0\n"
            "  3  9  1  0  0  0  0\n"
            "  3 10  1  0  0  0  0\n"
            "  3 11  1  0  0  0  0\n"
            "  4 12  1  0  0  0  0\n"
            "  4 13  1  0  0  0  0\n"
            "  4 14  1  0  0  0  0\n"
            "  5 15  1  0  0  0  0\n"
            "  5 16  1  0  0  0  0\n"
            "  5 17  1  0  0  0  0\n"
            "M  END\n"
        )
        with open("dimethylpropane.mol", "w") as mol_file:
            mol_file.write(mol_file_data)

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

    def bonds_from_atoms(self, atom_a, atom_b):
        for bond in self.molecule.edges:
            if atom_a in bond and atom_b in bond:
                return bond

        raise Exception(f"No bond found for atoms {atom_a}, {atom_b}")

    def rotate_atoms_about_bond(self, atom_a, atom_b, angle=PI / 4):
        bond = self.bonds_from_atoms(atom_a=atom_a, atom_b=atom_b)
        axis = self.molecule.edges[bond].sheen_direction
        self.atoms_copy.rotate(axis=axis, angle=angle)

        return [
            atom.animate.move_to(atom_copy)
            for atom, atom_copy in zip(self.atoms, self.atoms_copy)
        ]

    def change_color(self, atoms_color=BLACK, bonds_color=None, label_color=None):
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