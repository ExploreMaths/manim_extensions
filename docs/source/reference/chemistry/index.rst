.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Chemistry
=========

.. module:: manim_extensions.chemistry

.. vendored-status:: UnMolDeQuimica/manim-Chemistry

**Original author:** `UMDQ <https://github.com/UnMolDeQuimica>`_

**Source repository:** `GitHub <https://github.com/UnMolDeQuimica/manim-Chemistry>`_

**License:** MIT

``manim-Chemistry`` is a chemistry visualisation toolkit for Manim. It
provides periodic-table elements, 2-D / 3-D molecule rendering, Bohr atoms,
orbital diagrams, and a PubChem API client for fetching molecular data.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.chemistry`` subpackage.

.. inheritance-diagram:: manim_extensions.chemistry.utils.parsers.asnt_parser.ASNTParser manim_extensions.chemistry.twoD.bond.BaseMBondObject manim_extensions.chemistry.bohr_atom.bohr_atom.BohrAtom manim_extensions.chemistry.twoD.chemical_formula.ChemicalFormula manim_extensions.chemistry.twoD.chemical_formula.ComplexFormula manim_extensions.chemistry.twoD.bond.DoubleBond manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule manim_extensions.chemistry.utils.parsers.json_parser.JSONParser manim_extensions.chemistry.twoD.atom.MAtomObject manim_extensions.chemistry.periodic_table.table_objects.MElementObject manim_extensions.chemistry.twoD.molecule.MMoleculeObject manim_extensions.chemistry.utils.parsers.mol_parser.MolParser manim_extensions.chemistry.twoD.chemical_formula.NamedComplexFormula manim_extensions.chemistry.twoD.chemical_formula.NamedFormula manim_extensions.chemistry.twoD.molecule.NamedMolecule manim_extensions.chemistry.orbitals.orbitals.Orbital manim_extensions.chemistry.periodic_table.table_objects.PeriodicTable manim_extensions.chemistry.utils.parsers.sdf_parser.SDFParser manim_extensions.chemistry.twoD.bond.SimpleBond manim_extensions.chemistry.threeD.threedatom.ThreeDAtom manim_extensions.chemistry.threeD.threedbond.ThreeDBond manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule manim_extensions.chemistry.twoD.bond.TripleBond manim_extensions.chemistry.utils.parsers.xml_parser.XMLParser manim_extensions.chemistry.future_classes.future_classes.Hole manim_extensions.chemistry.future_classes.future_classes.Electron manim_extensions.chemistry.future_classes.future_classes.Element manim_extensions.chemistry.future_classes.future_classes.ElementFrame manim_extensions.chemistry.future_classes.future_classes.NPNTransistor manim_extensions.chemistry.future_classes.future_classes.BatterySchema manim_extensions.chemistry.future_classes.future_classes.MOSFETTransistor manim_extensions.chemistry.future_classes.future_classes.BatterySide manim_extensions.chemistry.orbitals.orbitals.OrbitalBase manim_extensions.chemistry.orbitals.orbitals.OrbitalPositive manim_extensions.chemistry.orbitals.orbitals.OrbitalNegative manim_extensions.chemistry.threeD.threedbond.ThreeDCylinder manim_extensions.chemistry.threeD.threedbond.ThreeDLine manim_extensions.chemistry.threeD.utils.OpenGLSphere manim_extensions.chemistry.twoD.bond.PlainCramBond manim_extensions.chemistry.twoD.bond.DashedCramBond manim_extensions.chemistry.twoD.graph_molecule.SimpleLine manim_extensions.chemistry.twoD.graph_molecule.DoubleLine manim_extensions.chemistry.twoD.graph_molecule.TripleLine manim_extensions.chemistry.utils.file_handler.IncorrectFormat manim_extensions.chemistry.utils.parsers.base_parser.BaseParser
   :parts: 1

Features
--------

- :class:`~manim_extensions.chemistry.element.element.Element` – chemical
  element data model (symbol, name, atomic number, mass, colour, etc.).
- :class:`~manim_extensions.chemistry.periodic_table.table_objects.PeriodicTable`
  – full periodic-table layout as a Manim mobject.
- :class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` – 2-D
  molecule from a file or SMILES string.
- :class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule` –
  graph-based molecule representation using ``networkx``.
- :class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule` –
  interactive 3-D molecule viewer.
- :class:`~manim_extensions.chemistry.bohr_atom.bohr_atom.BohrAtom` – Bohr
  atomic model animation.
- :class:`~manim_extensions.chemistry.orbitals.orbitals.Orbital` – atomic
  orbital visualisation.
- :class:`~manim_extensions.chemistry.molecule.molecule.Molecule` – unified
  facade that loads molecules from files, strings, or PubChem.
- :class:`~manim_extensions.chemistry.utils.pubchem_api.PubchemAPIManager` –
  PubChem REST API client.

Usage
-----

The toolkit pairs Manim with chemical data files (``.mol``, ``.sdf``,
``.json``, ``.asnt`` and ``.xml``) plus a small set of useful classes. By
design it avoids third-party chemistry libraries such as RDKit, Mendeleev,
PyMOL, or Open Babel to keep maintenance light; PubChem is the only bundled
external data source, and users may still combine the toolkit with those
libraries on their own.

2-D molecules
^^^^^^^^^^^^^

Build a 2-D molecule from a ``.mol`` file with
AbstractMolecule.molecule_from_file():

.. code-block:: python

   from manim import *
   from manim_extensions.chemistry import MMoleculeObject

   class TwoDMoleculeScene(Scene):
       def construct(self):
           morphine = MMoleculeObject.molecule_from_file("morphine.mol")
           self.add(morphine)

Double bonds can land on the wrong side after parsing. Pass
``add_bonds_numbering=True`` to overlay the bond numbering given by the
``.mol`` file (the numbering is the file's own, not the chemical structure),
then rotate the offending bonds by index with ``rotate_bonds=[7, 20]``.
Hydrogens bonded to carbon are hidden by default; pass
``ignore_hydrogens=False`` to keep them, or ``ignore_all_hydrogens=True`` to
drop every hydrogen.

Attach a name to a molecule with
:class:`~manim_extensions.chemistry.twoD.molecule.NamedMolecule`, which groups
the diagram with a title text:

.. code-block:: python

   named_molecule = NamedMolecule.molecule_from_file(
       name="Morphine", filename="morphine.mol")

Graph molecules
^^^^^^^^^^^^^^^

:class:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule` is
built on Manim's ``Graph`` (and thus on ``networkx``), so substructures can be
selected and animated. Load one from a file and add element or numeric atom
labels:

.. code-block:: python

   from manim import *
   from manim_extensions.chemistry import GraphMolecule

   class GraphMoleculeExample(Scene):
       def construct(self):
           graph_molecule = GraphMolecule.molecule_from_file(
               mol_file="morphine.mol", label=True, numeric_label=True)
           self.add(graph_molecule)

Select the atoms and bonds between two atom indices with
:meth:`~manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule.get_connected_atoms_and_bonds`
and recolor or rotate that part with
:class:`~manim_extensions.chemistry.twoD.animations.GMAnimationBuilder`:

.. code-block:: python

   molecule = GraphMolecule.molecule_from_file(
       "dimethylpropane.mol", label=True, numeric_label=True)
   atoms_and_bonds = molecule.get_connected_atoms_and_bonds(1, 3)
   animation_builder = GMAnimationBuilder(
       molecule=molecule, atoms=atoms_and_bonds[0],
       bonds=atoms_and_bonds[1])
   self.play(animation_builder.rotate_atoms_about_bond(1, 3))
   self.play(animation_builder.change_color(
       atoms_color=BLUE, bonds_color=RED, label_color=PINK))

3-D molecules
^^^^^^^^^^^^^

:class:`~manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule`
renders with the OpenGL renderer. Besides a molecule file it needs a CSV with
per-element data; the expected columns are ``AtomicNumber``, ``Name``,
``Symbol``, ``AtomicMass`` and ``Color``. Build it with
``ThreeDMolecule.from_mol_file(filename, source_csv)`` and render the scene
with ``--renderer=opengl`` (or ``config.renderer = "opengl"``).

Periodic table
^^^^^^^^^^^^^^

Draw a single element frame from a CSV data file:

.. code-block:: python

   carbon = MElementObject.from_csv_file_data(
       filename="Elementos.csv", atomic_number=6)

Compose the whole periodic table, using CPK coloring:

.. code-block:: python

   self.add(PeriodicTable(data_file="Elementos.csv"))

Atomic orbitals
^^^^^^^^^^^^^^^

Only atomic orbitals are supported (molecular orbitals are out of scope).
Select the ``l`` and ``m`` quantum numbers; render with the OpenGL renderer:

.. code-block:: python

   orbital = Orbital(l=1, m=-1)

Bohr diagrams
^^^^^^^^^^^^^

Set the numbers of electrons, protons, and neutrons:

.. code-block:: python

   diagram = BohrAtom(e=14, p=14, n=10)

Loading molecules from PubChem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fetch a molecule straight from PubChem by ``cid``, ``name``, ``smiles`` or
``inchi`` with
:meth:`~manim_extensions.chemistry.molecule.abstract_molecule.AbstractMolecule.molecule_from_pubchem`:

.. code-block:: python

   molecule = GraphMolecule.molecule_from_pubchem(name="morphine")

Pass ``three_d=True`` to obtain 3-D data (render with the OpenGL renderer).

Parsing and position helpers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The low-level parsers ``mol_parser_string``, ``mol_parser``,
``sdf_parser_string`` and ``sdf_parser`` return raw atom/bond data;
:class:`~manim_extensions.chemistry.twoD.molecule.MMoleculeObject` also
exposes ``from_mol_string`` / ``from_sdf_string`` classmethods for loading
directly from strings, and ``multiple_molecules_from_file`` for files holding
several molecules.

For layout work, molecule objects expose
``find_atom_position_by_index``, ``find_atoms_position_by_index``,
``find_all_atoms_positions``, ``find_bond_center_by_index``,
``find_bonds_center_by_index`` and ``find_all_bonds_centers`` to retrieve
atom and bond coordinates.

See the `upstream documentation <https://manim-chemistry.readthedocs.io/en/latest/>`_
for the reference manual and further quickstart examples.

Command-line interface
----------------------

The chemistry subpackage ships a small command-line client for
downloading molecule files from PubChem. See :doc:`cli` for the full
guide with examples of every option.

Chemical element data — atomic number, mass, colour and other properties —
plus module-level constants.

Modules
-------

.. autosummary::
   :nosignatures:

   ~bohr_atom
   ~cli
   ~element
   ~future_classes
   ~manim_chemistry_molecule
   ~molecule
   ~orbitals
   ~periodic_table
   ~threeD
   ~twoD
   ~utils

Constants
---------

.. autodata:: manim_extensions.chemistry.MC_ELEMENT_DICT
   :no-value:

.. toctree::
   :hidden:
   :maxdepth: 1

   bohr_atom/index
   cli
   element/index
   future_classes/index
   manim_chemistry_molecule/index
   molecule/index
   orbitals/index
   periodic_table/index
   threeD/index
   twoD/index
   utils/index
