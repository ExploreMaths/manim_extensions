# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""2D molecule representation for Manim chemistry.

This module provides the :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` class for rendering molecules in 2D.
"""

from __future__ import annotations
from typing import Any, cast

import logging


from manim import (
    DOWN,
    GREEN,
    MarkupText,
    MathTex,
    ORIGIN,
    PI,
    RED,
    SVGMobject,
    VMobject,
    VDict,
    VGroup,
)
from ..utils import (
    mol_parser,
    mol_parser_string,
    sdf_parser,
    sdf_parser_string,
)
from ..manim_chemistry_molecule import MCMolecule
from ..molecule import AbstractMolecule

from .atom import MAtomObject
from .bond import (
    BaseMBondObject,
    DashedCramBond,
    DoubleBond,
    PlainCramBond,
    SimpleBond,
    TripleBond,
)
from manim.typing import Point3D

_logger = logging.getLogger(__name__)


class MMoleculeObject(VGroup, AbstractMolecule):
    r"""Represents a molecule in a similar fashion as it is done in academia.

    .. doc-example-covers: get_bonds


    Parameters
    ----------
    atoms_dict
        Dictionary with the atom data of the molecule.
    bonds_dict
        Dictionary with the bond data of the molecule.
    representation_type
        Type of atom representation.
    explicit_carbons
        Whether to explicitly show carbon atoms.
    explicit_hydrogens
        Whether to explicitly show hydrogen atoms.
    planar
        Whether the molecule is rendered in 2D.
    add_atoms_numbering
        Whether to add numbering to the atoms.
    add_bonds_numbering
        Whether to add numbering to the bonds.
    rotate_bonds
        Bonds to rotate.
    **kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    ---------
    .. manim:: MMoleculeFromFile
       :files: acetone_2d.mol

       from manim import *
       from manim_extensions.chemistry import MMoleculeObject

       class MMoleculeFromFile(Scene):
           def construct(self):
               mmolecule = MMoleculeObject.molecule_from_file("acetone_2d.mol")
               mmolecule.scale(1.6)
               self.play(Write(mmolecule))
               self.play(Indicate(mmolecule.bonds[0]))
               self.wait()

    .. manim:: MMoleculeFromString
       :files: acetone_2d.mol
       :save_last_frame:

       from manim import *
       from pathlib import Path
       from manim_extensions.chemistry import MMoleculeObject

       class MMoleculeFromString(Scene):
           def construct(self):
               mmolecule = MMoleculeObject.molecule_from_string(
                   Path("acetone_2d.mol").read_text(), format="mol"
               )
               self.add(mmolecule)
               mmolecule.add_atom_numbering()
               self.add(mmolecule[-1])
    """

    def __init__(
        self,
        atoms_dict: dict[Any, Any],
        bonds_dict: dict[Any, Any],
        representation_type: str | None = None,
        explicit_carbons: bool = False,
        explicit_hydrogens: bool = False,
        planar: bool = True,
        add_atoms_numbering: bool = False,
        add_bonds_numbering: bool = False,
        rotate_bonds: list[Any] = [],
        **kwargs: Any,
    ) -> None:
        VGroup.__init__(self, **kwargs)
        self.atoms_dict: dict[Any, Any] = atoms_dict
        self.bonds_dict: dict[Any, Any] = bonds_dict
        self.representation_type = representation_type
        self.explicit_carbons = explicit_carbons
        self.explicit_hydrogens = explicit_hydrogens
        self.planar = planar
        self.atoms: Any
        self.atoms_by_index: dict[Any, Any]
        self.atoms, self.atoms_by_index = self.get_atoms()
        self.bonds: VGroup = self.get_bonds()
        self.add(self.atoms, self.bonds)
        if add_atoms_numbering:
            self.add_atom_numbering()
        if add_bonds_numbering:
            self.add_bond_numbering()
        self.rotate_bond(rotate_bonds)
        self.complete_missing_hydrogens()
        self.move_to(ORIGIN)

    def get_atoms(self) -> tuple[VDict, dict[Any, MAtomObject]]:
        """Build :class:`~manim_extensions.chemistry.twoD.atom.MAtomObject` instances from the atoms dict and return them as :class:`~manim.mobject.types.vectorized_mobject.VDict` + index dict.

        Returns
        -------
            A tuple of the results.
        """
        atoms = VDict()
        atoms_by_index = {}
        for index, atom in self.atoms_dict.items():
            matom = MAtomObject(
                coords=atom["coords"],
                element=atom["element"],
                explicit_carbons=self.explicit_carbons,
                explicit_hydrogens=self.explicit_hydrogens,
                representation_type=cast(Any, self.representation_type),
                planar=self.planar,
                bond_to=atom.get("bond_to"),
                index=index,
            )
            atoms.add([(index, matom)])
            atoms_by_index[index] = matom
        return atoms, atoms_by_index

    def get_bonds(self) -> VGroup:
        """Build bond mobjects (single/double/triple/cram) from the bonds dict and return a VGroup.

        Returns
        -------
            A :class:`~manim.mobject.types.vectorized_mobject.VGroup` instance representing the result.
        """
        bonds = VGroup()
        bond_index = 0
        new_bond: BaseMBondObject
        for index, bond_list in self.bonds_dict.items():
            for bond in bond_list:
                # TODO: Add logic to check type of bond
                bond_type = int(bond.get("type", 1))
                from_atom = self.atoms_by_index[index]
                to_atom = self.atoms_by_index[bond.get("to")]
                if from_atom.element == "H" or to_atom.element == "H":
                    stereo = bond.get("stereo")

                    if stereo:
                        if int(stereo) == 1 or int(stereo) == 4:
                            self.atoms[from_atom.index] = (
                                from_atom.copy_with_explicit_hydrogens()
                            )
                            self.atoms[to_atom.index] = (
                                to_atom.copy_with_explicit_hydrogens()
                            )
                            from_atom = self.atoms[from_atom.index]
                            to_atom = self.atoms[to_atom.index]
                            new_bond = PlainCramBond(
                                from_atom=from_atom,
                                to_atom=to_atom,
                                index=bond_index,
                                type=bond_type,
                            )

                            bond_index += 1
                            bonds.add(new_bond)

                        elif int(stereo) == 6:
                            self.atoms[from_atom.index] = (
                                from_atom.copy_with_explicit_hydrogens()
                            )
                            self.atoms[to_atom.index] = (
                                to_atom.copy_with_explicit_hydrogens()
                            )
                            from_atom = self.atoms[from_atom.index]
                            to_atom = self.atoms[to_atom.index]
                            new_bond = DashedCramBond(
                                from_atom=from_atom,
                                to_atom=to_atom,
                                index=bond_index,
                                type=bond_type,
                            )

                            bond_index += 1
                            bonds.add(new_bond)

                        else:
                            continue
                    # you don't need not x and not y
                    # just use De Morgan's law ! (syntactic detail, doesn't change code)
                    elif (from_atom.explicit_hydrogens) or (to_atom.explicit_hydrogens):
                        # make bonds to explicit hydrogens
                        # TODO: clean repetitive code
                        self.atoms[from_atom.index] = (
                            from_atom.copy_with_explicit_hydrogens()
                        )
                        self.atoms[to_atom.index] = (
                            to_atom.copy_with_explicit_hydrogens()
                        )
                        from_atom = self.atoms[from_atom.index]
                        to_atom = self.atoms[to_atom.index]
                        new_bond = SimpleBond(
                            from_atom=from_atom,
                            to_atom=to_atom,
                            index=bond_index,
                            type=bond_type,
                        )

                        bond_index += 1
                        bonds.add(new_bond)
                        continue
                    # patched: a hydrogen bond with no stereo information and no
                    # explicit hydrogens used to be dropped silently.
                    else:
                        new_bond = SimpleBond(
                            from_atom=from_atom,
                            to_atom=to_atom,
                            index=bond_index,
                            type=bond_type,
                        )
                        bond_index += 1
                        bonds.add(new_bond)

                else:
                    if bond_type == 2 or bond_type == 5 or bond_type == 7:
                        new_bond = DoubleBond(  # TODO: Add function inside bond to create it from data
                            from_atom=from_atom,
                            to_atom=to_atom,
                            index=bond_index,
                            type=bond_type,
                        )
                    elif bond_type == 3:
                        new_bond = TripleBond(
                            from_atom=from_atom,
                            to_atom=to_atom,
                            index=bond_index,
                            type=bond_type,
                        )
                    else:
                        if bond.get("stereo"):
                            if int(bond.get("stereo")) == 1:
                                new_bond = PlainCramBond(
                                    from_atom=from_atom,
                                    to_atom=to_atom,
                                    index=bond_index,
                                    type=bond_type,
                                )

                            else:
                                new_bond = DashedCramBond(
                                    from_atom=from_atom,
                                    to_atom=to_atom,
                                    index=bond_index,
                                    type=bond_type,
                                )
                        else:
                            new_bond = SimpleBond(
                                from_atom=from_atom,
                                to_atom=to_atom,
                                index=bond_index,
                                type=bond_type,
                            )
                    bond_index += 1
                    bonds.add(new_bond)

        return bonds

    def add_atom_numbering(self) -> "MMoleculeObject":
        """Add numeric index labels next to each atom and return self.

        Returns
        -------
            The object itself, for method chaining.
        """
        numbering = VGroup()
        for atom in self.atoms:
            if not self.explicit_hydrogens:
                if atom.element != "H":
                    numbering.add(
                        MarkupText(str(atom.index))
                        .scale(0.5)
                        .move_to(atom.coords)
                        .set_color(RED)
                    )
            else:
                numbering.add(
                    MarkupText(str(atom.index))
                    .scale(0.5)
                    .move_to(atom.coords)
                    .set_color(RED)
                )

        self.add(numbering)

        return self

    def add_bond_numbering(self) -> "MMoleculeObject":
        """Add numeric index labels next to each bond and return self.

        Returns
        -------
            The object itself, for method chaining.
        """
        numbering = VGroup()
        for bond in self.bonds:
            if (
                not cast(Any, bond.from_atom).explicit_hydrogens
                and not cast(Any, bond.to_atom).explicit_hydrogens
            ):
                if (
                    cast(Any, bond.from_atom).element != "H"
                    and cast(Any, bond.to_atom).element != "H"
                ):
                    numbering.add(
                        MarkupText(str(bond.index))
                        .set_color(GREEN)
                        .move_to(bond.get_center())
                        .scale(0.5)
                    )

        self.add(numbering)

        return self

    def rotate_bond(self, rotate_bonds: int | list[int]) -> "MMoleculeObject":
        """Rotate specified bonds 180 degrees around their own axis and return self.

        Parameters
        ----------
        rotate_bonds
            Bond index or list of bond indices to rotate.

        Returns
        -------
            The object itself, for method chaining.
        """
        if isinstance(rotate_bonds, int):
            rotate_bonds = [rotate_bonds]

        for bond in rotate_bonds:
            line = cast(Any, self.bonds[bond][0][0])
            direction = line.end - line.start
            self.bonds[bond].rotate(PI, about_point=line.get_center(), axis=direction)

        return self

    def complete_missing_hydrogens(self) -> Any:
        """Append implicit hydrogen labels to atoms that don't fulfill their minimum bond count.

        Returns
        -------
            The resulting value.
        """
        supported_atoms = ["O", "S", "N", "P"]

        for atom in self.atoms:
            if atom.element not in supported_atoms:
                continue

            total_bonds = len(atom.bond_to)
            bonds_direction = 0
            if not atom.bonds_fulfilled():
                minimum_bonds: dict[str, int] = {"O": 2, "S": 2, "N": 3, "P": 3}
                for bond in cast(Any, self.bonds):
                    if bond.atom_is_in_bond(atom) and 0 < bond.type <= 4:
                        total_bonds += bond.type - 1
                        bonds_direction += (
                            cast(Any, bond.to_atom).coords[0]
                            - cast(Any, bond.from_atom).coords[0]
                        )

                minimum = minimum_bonds.get(atom.element, 0)
                if total_bonds < minimum:
                    needed_hydrogens = minimum - total_bonds
                    if bonds_direction < 0:
                        if needed_hydrogens > 1:
                            self.atoms[atom.index] = atom.rename_atom(
                                f"H<sub>{needed_hydrogens}</sub>" + atom.element,
                                bonds_direction,
                            )
                        else:
                            self.atoms[atom.index] = atom.rename_atom(
                                "H" + atom.element, bonds_direction
                            )
                    else:
                        if needed_hydrogens > 1:
                            self.atoms[atom.index] = atom.rename_atom(
                                atom.element + f"H<sub>{needed_hydrogens}</sub>",
                                bonds_direction,
                            )
                        else:
                            self.atoms[atom.index] = atom.rename_atom(
                                atom.element + "H", bonds_direction
                            )

    @staticmethod
    def from_mol_file(filename: str, *args: Any, **kwargs: Any) -> "MMoleculeObject":
        """Create an :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` by parsing a .mol file.

        Parameters
        ----------
        filename
            Path to the .mol file.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` instance representing the result.
        """
        atoms, bonds = mol_parser(filename)
        return MMoleculeObject(atoms, bonds, *args, **kwargs)

    @staticmethod
    def from_mol_string(
        mol_string: str, *args: Any, **kwargs: Any
    ) -> "MMoleculeObject":
        """Create an :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` by parsing a mol-format string.

        Parameters
        ----------
        mol_string
            String with the molecule data in mol format.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` instance representing the result.
        """
        # patched: the parser wants the lines of a MOL block, but the public
        # entry point is documented as taking the whole string.
        lines = mol_string.splitlines() if isinstance(mol_string, str) else mol_string
        atoms, bonds = mol_parser_string(lines)
        return MMoleculeObject(atoms, bonds, *args, **kwargs)

    @staticmethod
    def from_sdf_file(
        filename: str, *args: Any, **kwargs: Any
    ) -> "list[MMoleculeObject]":
        r"""Create a list of :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`\ s by parsing an .sdf file.

        Parameters
        ----------
        filename
            Path to the .sdf file.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A list of the results.
        """
        molecules = sdf_parser(filename)
        moleculeObjects = []
        for molecule in molecules:
            atoms, bonds = molecule
            moleculeObjects.append(MMoleculeObject(atoms, bonds, *args, **kwargs))
        return moleculeObjects

    @staticmethod
    def from_sdf_string(
        sdf_string: str, *args: Any, **kwargs: Any
    ) -> "list[MMoleculeObject]":
        r"""Create a list of :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`\ s by parsing an sdf-format string.

        Parameters
        ----------
        sdf_string
            String with the molecule data in sdf format.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A list of the results.
        """
        molecules = sdf_parser_string(sdf_string)
        moleculeObjects = []
        for molecule in molecules:
            atoms, bonds = molecule
            moleculeObjects.append(MMoleculeObject(atoms, bonds, *args, **kwargs))
        return moleculeObjects

    def find_atom_position_by_index(self, atom_index: int) -> Point3D:
        """Returns the position of a single atom given its index.

        Parameters
        ----------
        atom_index
            Index of the atom inside the :class:`~manim.mobject.types.vectorized_mobject.VDict`.

        Returns
        -------
            :class:`~manim_extensions.algorithm.array.Array` with the [x, y, z] coordinates of the atom.

        Raises
        ------
        KeyError
            Raised when ``atom_index`` is not a valid atom index.
        Exception
            Re-raised when the atom lookup fails otherwise.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           print(molecule.find_atom_position_by_index(1))
        """
        try:
            atom = self.atoms[atom_index]
            return cast(Point3D, atom.get_center())

        except KeyError as key_error:
            _logger.warning(f"Atom index {atom_index} is not valid for molecule {self}")
            _logger.warning(f"Valid indices are: {self.atoms.submob_dict.keys()}")
            raise key_error

        except Exception as exception:
            raise exception

    def find_atoms_position_by_index(self, atoms_index_list: list[Any]) -> list[Any]:
        """Returns the position of multiple atoms given their indices.

        Parameters
        ----------
        atoms_index_list
            List of atoms indices to be gotten.

        Returns
        -------
            List of the atoms positions.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           from pprint import pprint

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           pprint(molecule.find_atoms_position_by_index([1,2,3]))
        """
        atoms_positions = []
        for atom_index in atoms_index_list:
            atoms_positions.append(
                self.find_atom_position_by_index(atom_index=atom_index)
            )

        return atoms_positions

    def find_bond_center_by_index(self, bond_index: int) -> Point3D:
        """Returns the [x, y, z] coordinates of a bond given a bond index.

        Parameters
        ----------
        bond_index
            Index of the bond.

        Returns
        -------
            [x, y, z] coordinates of bond center.

        Raises
        ------
        KeyError
            Raised when ``bond_tuple`` is not a valid bond index.
        Exception
            Re-raised when the bond lookup fails otherwise.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           print(molecule.find_bond_center_by_index(1))
        """
        try:
            bond = self.bonds[bond_index]
            return bond.get_center()

        except KeyError as key_error:
            _logger.warning(f"Bond index {bond_index} is not valid for molecule {self}")
            raise key_error

        except Exception as exception:
            raise exception

    def find_position_along_bond_axis(
        self, bond_index: int, position_buff: float
    ) -> Point3D:
        """Returns a position along the bond axis given a bond index and depending on a position_buff.
        A value of 1 will return one end of the bond. A value of -1 will return the other end.
        All values in between return positions at some point of the middle of the bond, being 0 the center.
        Values bigger or lower that 1 and -1 will return positions outside the bond.

        Parameters
        ----------
        bond_index
            Index of the bond.
        position_buff
            Position buff.

        Returns
        -------
            [x, y, z] coordinates of the final position selected.

        Raises
        ------
        KeyError
            Raised when ``bond_tuple`` is not a valid bond index.
        """

        try:
            bond = self.bonds[bond_index]

        except KeyError as key_error:
            _logger.warning(f"Bond index {bond_index} is not valid for molecule {self}")
            _logger.warning(
                f"Valid indices are: {cast(Any, self.bonds.submob_dict).keys()}"
            )
            raise key_error

        bond_vector = bond.get_vector()
        bond_center = bond.get_center()

        return cast(Point3D, bond_center + bond_vector * position_buff * 0.5)

    def find_bonds_center_by_index(self, bonds_index_list: list[Any]) -> list[Any]:
        """Returns the position of multiple bonds given their indices.

        Parameters
        ----------
        bonds_index_list
            List of bonds indices to be gotten.

        Returns
        -------
            List of the bonds positions.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           from pprint import pprint

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           pprint(molecule.find_bonds_center_by_index([1, 2, 3]))
        """
        bonds_positions = []
        for bond_index in bonds_index_list:
            bonds_positions.append(
                self.find_bond_center_by_index(bond_index=bond_index)
            )

        return bonds_positions

    def find_all_atoms_positions(self) -> dict[Any, Any]:
        """Return a dict mapping every atom index to its current position.

        Returns
        -------
            Dictionary mapping atom indices to their positions.
        """
        atoms_positions = {}
        for atom_index in self.atoms.submob_dict.keys():
            atoms_positions[atom_index] = self.find_atom_position_by_index(
                atom_index=atom_index
            )

        return atoms_positions

    def find_all_bonds_centers(self) -> dict[Any, Any]:
        """Return a dict mapping every bond index to its center position.

        Returns
        -------
            Dictionary mapping bond indices to their center positions.
        """
        bonds_positions = {}
        for bond_index, _ in enumerate(self.bonds):
            bonds_positions[bond_index] = self.find_bond_center_by_index(
                bond_index=bond_index
            )

        return bonds_positions

    @classmethod
    def mc_molecule_to_atoms_and_bonds(
        cls, mc_molecule: MCMolecule
    ) -> tuple[dict[Any, Any], dict[Any, Any]]:
        """Transforms the structure of a mc_molecule to a (vertices, edges) tuple.

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
        atoms = {}
        for index, atom in mc_molecule.atoms_by_index.items():
            bond_to = {}
            for bond in atom.bonds:
                # TODO: This patches an issue with from_atom and to_atom but does not solve it completely.
                # Fix later the root cause
                from_atom_ref = cast(Any, bond.from_atom)
                to_atom_ref = cast(Any, bond.to_atom)
                if from_atom_ref.molecule_index == index:
                    bond_to[to_atom_ref.molecule_index] = to_atom_ref.element.symbol

                else:
                    bond_to[from_atom_ref.molecule_index] = from_atom_ref.element.symbol

            atom_data = {
                "coords": atom.coords,
                "element": atom.element.symbol,
                "bond_to": bond_to,
            }

            atoms[index] = atom_data

        bonds = {}
        for atom_index in atoms.keys():
            atom_bonds = []
            for bond in mc_molecule.bonds:
                if atom_index == cast(Any, bond.to_atom).molecule_index:
                    atom_bonds.append(
                        {
                            "to": cast(Any, bond.from_atom).molecule_index,
                            "type": bond.bond_type,
                            "stereo": bond.stereo,
                            "topology": bond.topology,
                            "reacting_center_status": bond.reacting_center_status,
                        }
                    )
            if atom_bonds:
                bonds[atom_index] = atom_bonds

        return atoms, bonds


class NamedMolecule(VGroup):
    r"""A molecule together with its name.

    Parameters
    ----------
    name
        The name of the molecule. Can be a string or a :class:`~manim.mobject.svg.svg_mobject.SVGMobject`.
    molecule_data
        An :class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule.MMoleculeObject` or the molecule data to construct one.
    direction
        Direction in which the name is placed relative to the molecule.

    buff
        Distance between the molecule and its name.
    tex
        Whether to render the name with :class:`~manim.mobject.text.tex_mobject.MathTex`.
    font
        Font of the name text.
    args
        Additional positional arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.
    **kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: NamedMoleculeScene
       :files: acetone_2d_named.mol
       :save_last_frame:

       from manim import *
       from pathlib import Path
       from manim_extensions.chemistry import NamedMolecule

       class NamedMoleculeScene(Scene):
           def construct(self):
               named_molecule = NamedMolecule.from_mol_file(
                   name="Acetone", filename="acetone_2d_named.mol"
               )
               self.add(named_molecule)
    """

    def __init__(
        self,
        name: str,
        molecule_data: MMoleculeObject | dict[str, Any],
        direction: Point3D = DOWN,
        buff: float = 1,
        tex: bool = False,
        font: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if isinstance(molecule_data, MMoleculeObject):
            self.molecule = molecule_data

        else:
            self.molecule = MMoleculeObject(molecule_data, *args, **kwargs)

        name_text: VMobject
        extra_kwargs = dict(kwargs)
        extra_kwargs.pop("font", None)
        if isinstance(name, SVGMobject):
            name_text = name

        elif tex:
            name_text = MathTex(name, *args, **extra_kwargs)
        else:
            name_text = cast(Any, MarkupText)(name, *args, font=font, **extra_kwargs)

        name_text.next_to(self.molecule, direction, buff)

        super().__init__(cast(Any, self.molecule), name_text, **kwargs)
        self.atoms = self.molecule.atoms
        self.bonds = self.molecule.bonds

    @staticmethod
    def from_mol_file(
        name: str,
        filename: str,
        direction: Point3D = DOWN,
        buff: float = 1,
        tex: bool = False,
        font: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> "NamedMolecule":
        """Create a :class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule` from a .mol file and a name string.

        Parameters
        ----------
        name
            Name of the molecule.
        filename
            Path to the .mol file.
        direction
            Direction in which the name is placed relative to the molecule.

        buff
            Distance between the molecule and its name.
        tex
            Whether to render the name with :class:`~manim.mobject.text.tex_mobject.MathTex`.
        font
            Font of the name text.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A :class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule` instance representing the result.
        """
        molecule = MMoleculeObject.from_mol_file(filename, *args, **kwargs)
        extra_kwargs = {
            key: value
            for key, value in kwargs.items()
            if key not in {"direction", "buff", "tex", "font"}
        }
        call_kwargs: dict[str, Any] = {
            "direction": direction,
            "buff": buff,
            "tex": tex,
            "font": font,
        }
        call_kwargs.update(extra_kwargs)
        return NamedMolecule(name, molecule, *args, **call_kwargs)

    @staticmethod
    def from_mol_string(
        name: str,
        mol_str: str,
        direction: Point3D = DOWN,
        buff: float = 1,
        tex: bool = False,
        font: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> "NamedMolecule":
        """Create a :class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule` from a mol-format string and a name string.

        Parameters
        ----------
        name
            Name of the molecule.
        mol_str
            String with the molecule data in mol format.
        direction
            Direction in which the name is placed relative to the molecule.

        buff
            Distance between the molecule and its name.
        tex
            Whether to render the name with :class:`~manim.mobject.text.tex_mobject.MathTex`.
        font
            Font of the name text.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A :class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule` instance representing the result.
        """
        molecule = MMoleculeObject.from_mol_string(mol_str, *args, **kwargs)

        call_kwargs: dict[str, Any] = {
            "direction": direction,
            "buff": buff,
            "tex": tex,
            "font": font,
        }
        call_kwargs.update(cast(Any, kwargs))
        return NamedMolecule(name, molecule, *args, **call_kwargs)

    @staticmethod
    def from_sdf_file(
        name: str,
        filename: str,
        direction: Point3D = DOWN,
        buff: float = 1,
        tex: bool = False,
        font: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> "list[NamedMolecule]":
        r"""Create a list of :class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule`\ s from an .sdf file with a shared base name.

        Parameters
        ----------
        name
            Base name of the molecules.
        filename
            Path to the .sdf file.
        direction
            Direction in which the name is placed relative to the molecule.

        buff
            Distance between the molecule and its name.
        tex
            Whether to render the name with :class:`~manim.mobject.text.tex_mobject.MathTex`.
        font
            Font of the name text.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A list of the results.
        """
        molecules = MMoleculeObject.from_sdf_file(filename, *args, **kwargs)
        named_molecules = []
        for index, molecule in enumerate(molecules):
            named_molecules.append(
                cast(Any, NamedMolecule)(
                    name + f"_{index}",
                    molecule,
                    direction=direction,
                    buff=buff,
                    tex=tex,
                    font=font,
                    *args,
                    **kwargs,
                )
            )
        return named_molecules

    @staticmethod
    def from_sdf_string(
        name: str,
        sdf_str: str,
        direction: Point3D = DOWN,
        buff: float = 1,
        tex: bool = False,
        font: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> "list[NamedMolecule]":
        r"""Create a list of :class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule`\ s from an sdf-format string with a shared base name.

        Parameters
        ----------
        name
            Base name of the molecules.
        sdf_str
            String with the molecule data in sdf format.
        direction
            Direction in which the name is placed relative to the molecule.

        buff
            Distance between the molecule and its name.
        tex
            Whether to render the name with :class:`~manim.mobject.text.tex_mobject.MathTex`.
        font
            Font of the name text.
        **kwargs
            Additional keyword arguments passed to
            :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject`.

        Returns
        -------
            A list of the results.
        """
        molecules = MMoleculeObject.from_sdf_string(sdf_str, *args, **kwargs)
        named_molecules = []
        for index, molecule in enumerate(molecules):
            named_molecules.append(
                cast(Any, NamedMolecule)(
                    name + f"_{index}",
                    molecule,
                    direction=direction,
                    buff=buff,
                    tex=tex,
                    font=font,
                    *args,
                    **kwargs,
                )
            )
        return named_molecules

    def rotate_bond(self, bonds: int | list[Any]) -> "NamedMolecule":
        """Rotate specified bonds on the inner molecule and return self.

        Parameters
        ----------
        bonds
            Bond index or list of bond indices to rotate.

        Returns
        -------
            The object itself, for method chaining.
        """
        self.molecule = self.molecule.rotate_bond(bonds)

        return self

    def add_bond_numbering(self) -> "NamedMolecule":
        """Add bond numbering to the inner molecule and return self.

        Returns
        -------
            The object itself, for method chaining.
        """
        self.molecule = self.molecule.add_bond_numbering()
        self.molecule[-1].move_to(self.molecule[1].get_center())

        return self

    def add_atom_numbering(self) -> "NamedMolecule":
        """Add atom numbering to the inner molecule and return self.

        Returns
        -------
            The object itself, for method chaining.
        """
        # Atom numbering is not working correctly.
        self.molecule = self.molecule.add_atom_numbering()
        self.molecule[-1].move_to(self.molecule[0].get_center())

        return self

    def find_atom_position_by_index(self, atom_index: int) -> Point3D:
        """Returns the position of a single atom given its index.

        Parameters
        ----------
        atom_index
            Index of the atom inside the :class:`~manim.mobject.types.vectorized_mobject.VDict`.

        Returns
        -------
            :class:`~manim_extensions.algorithm.array.Array` with the [x, y, z] coordinates of the atom.

        Raises
        ------
        KeyError
            Raised when ``atom_index`` is not a valid atom index.
        Exception
            Re-raised when the atom lookup fails otherwise.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           print(molecule.find_atom_position_by_index(1))
        """
        try:
            atom = self.atoms[atom_index]
            return cast(Point3D, atom.get_center())

        except KeyError as key_error:
            _logger.warning(f"Atom index {atom_index} is not valid for molecule {self}")
            _logger.warning(f"Valid indices are: {self.atoms.submob_dict.keys()}")
            raise key_error

        except Exception as exception:
            raise exception

    def find_atoms_position_by_index(self, atoms_index_list: list[Any]) -> list[Any]:
        """Returns the position of multiple atoms given their indices.

        Parameters
        ----------
        atoms_index_list
            List of atoms indices to be gotten.

        Returns
        -------
            List of the atoms positions.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           from pprint import pprint

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           pprint(molecule.find_atoms_position_by_index([1,2,3]))
        """
        atoms_positions = []
        for atom_index in atoms_index_list:
            atoms_positions.append(
                self.find_atom_position_by_index(atom_index=atom_index)
            )

        return atoms_positions

    def find_bond_center_by_index(self, bond_index: int) -> Point3D:
        """Returns the [x, y, z] coordinates of a bond given a bond index.

        Parameters
        ----------
        bond_index
            Index of the bond.

        Returns
        -------
            [x, y, z] coordinates of bond center.

        Raises
        ------
        KeyError
            Raised when ``bond_tuple`` is not a valid bond index.
        Exception
            Re-raised when the bond lookup fails otherwise.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           print(molecule.find_bond_center_by_index(1))
        """
        try:
            bond = self.bonds[bond_index]
            return bond.get_center()

        except KeyError as key_error:
            _logger.warning(f"Bond index {bond_index} is not valid for molecule {self}")
            _logger.warning(
                f"Valid indices are: {cast(Any, self.bonds.submob_dict).keys()}"
            )
            raise key_error

        except Exception as exception:
            raise exception

    def find_position_along_bond_axis(
        self, bond_index: int, position_buff: float
    ) -> Point3D:
        """Returns a position along the bond axis given a bond index and depending on a position_buff.
        A value of 1 will return one end of the bond. A value of -1 will return the other end.
        All values in between return positions at some point of the middle of the bond, being 0 the center.
        Values bigger or lower that 1 and -1 will return positions outside the bond.

        Parameters
        ----------
        bond_index
            Index of the bond.
        position_buff
            Position buff.

        Returns
        -------
            [x, y, z] coordinates of the final position selected.

        Raises
        ------
        KeyError
            Raised when ``bond_tuple`` is not a valid bond index.
        """

        try:
            bond = self.bonds[bond_index]

        except KeyError as key_error:
            _logger.warning(f"Bond index {bond_index} is not valid for molecule {self}")
            _logger.warning(
                f"Valid indices are: {cast(Any, self.bonds.submob_dict).keys()}"
            )
            raise key_error

        bond_vector = bond.get_vector()
        bond_center = bond.get_center()

        return cast(Point3D, bond_center + bond_vector * position_buff * 0.5)

    def find_bonds_center_by_index(self, bonds_index_list: list[Any]) -> list[Any]:
        """Returns the position of multiple bonds given their indices.

        Parameters
        ----------
        bonds_index_list
            List of bonds indices to be gotten.

        Returns
        -------
            List of the bonds positions.

        Examples
        --------
        .. nbcell::
           :files: dimethylpropane.mol

           from pprint import pprint

           molecule = MMoleculeObject.molecule_from_file("dimethylpropane.mol")
           pprint(molecule.find_bonds_center_by_index([1, 2, 3]))
        """
        bonds_positions = []
        for bond_index in bonds_index_list:
            bonds_positions.append(
                self.find_bond_center_by_index(bond_index=bond_index)
            )

        return bonds_positions

    def find_all_atoms_positions(self) -> dict[Any, Any]:
        """Return a dict mapping every atom index to its current position.

        Returns
        -------
            Dictionary mapping atom indices to their positions.
        """
        atoms_positions = {}
        for atom_index in self.atoms.submob_dict.keys():
            atoms_positions[atom_index] = self.find_atom_position_by_index(
                atom_index=atom_index
            )

        return atoms_positions

    def find_all_bonds_centers(self) -> dict[Any, Any]:
        """Return a dict mapping every bond index to its center position.

        Returns
        -------
            Dictionary mapping bond indices to their center positions.
        """
        bonds_positions = {}
        for bond_index, _ in enumerate(self.bonds):
            bonds_positions[bond_index] = self.find_bond_center_by_index(
                bond_index=bond_index
            )

        return bonds_positions
