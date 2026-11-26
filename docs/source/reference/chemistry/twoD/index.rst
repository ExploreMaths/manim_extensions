.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

twoD
====

.. automodule:: manim_extensions.chemistry.twoD

Usage
-----

Load a MOL file into a flat graph molecule, or build one from atom and bond dictionaries.

.. manim:: GraphMoleculeScene
   :files: acetone_2d.mol
   :ref_classes: GraphMolecule

   from manim import *
   from manim_extensions.chemistry.twoD import GraphMolecule

   class GraphMoleculeScene(Scene):
       def construct(self):
           molecule = GraphMolecule.molecule_from_file("acetone_2d.mol")
           molecule.scale_to_fit_height(6)
           self.play(FadeIn(molecule))

Modules
-------

.. autosummary::
   :nosignatures:

   ~animations
   ~atom
   ~bond
   ~chemical_formula
   ~graph_molecule
   ~molecule

.. toctree::
   :hidden:
   :maxdepth: 1

   animations
   atom
   bond
   chemical_formula
   graph_molecule
   molecule
