.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

molecule
========

.. automodule:: manim_extensions.chemistry.molecule

Classes
-------

.. autosummary::
   :nosignatures:

   ~molecule.Molecule

Usage
-----

Load a MOL file and get a ready-to-add molecule mobject.

.. manim:: MoleculeScene
   :files: acetone_2d.mol
   :ref_classes: Molecule

   from manim import *
   from manim_extensions.chemistry.molecule import Molecule

   class MoleculeScene(Scene):
       def construct(self):
           molecule = Molecule().molecule_from_file("acetone_2d.mol")
           molecule.scale_to_fit_height(6)
           self.play(FadeIn(molecule))
           self.wait()

Modules
-------

.. autosummary::
   :nosignatures:

   ~abstract_molecule
   ~molecule

.. toctree::
   :hidden:
   :maxdepth: 1

   abstract_molecule
   molecule
