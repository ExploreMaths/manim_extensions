.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

threeD
======

.. module:: manim_extensions.chemistry.threeD

Usage
-----

Render a molecule in 3D. The package requires the OpenGL renderer, and atom/bond dictionaries can come from :class:`~manim_extensions.chemistry.utils.file_handler.FileHandler`.

.. code-block:: python

   from manim import *
   from manim_extensions.chemistry.threeD import ThreeDMolecule
   from manim_extensions.chemistry.utils import FileHandler

   config.renderer = "opengl"
   atoms, bonds = FileHandler("acetone_2d.mol").parsed_atoms_bonds_data()

   class ThreeDSceneDemo(ThreeDScene):
       def construct(self):
           molecule = ThreeDMolecule(atoms, bonds)
           self.add(molecule)

Modules
-------

.. autosummary::
   :nosignatures:

   ~threedatom
   ~threedbond
   ~threedmolecule
   ~utils

.. toctree::
   :hidden:
   :maxdepth: 1

   threedatom
   threedbond
   threedmolecule
   utils
