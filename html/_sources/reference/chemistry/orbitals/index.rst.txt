.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

orbitals
========

.. module:: manim_extensions.chemistry.orbitals

Classes
-------

.. autosummary::
   :nosignatures:

   ~orbitals.Orbital
   ~orbitals.OrbitalBase
   ~orbitals.OrbitalNegative
   ~orbitals.OrbitalPositive

Usage
-----

Draw a hydrogen-like orbital. This package uses the OpenGL renderer for its surfaces.

.. code-block:: python

   from manim import *
   from manim_extensions.chemistry.orbitals import Orbital

   config.renderer = "opengl"

   class OrbitalScene(ThreeDScene):
       def construct(self):
           orbital = Orbital(n=2, l=1, m=0, size=3)
           self.add(orbital)

Modules
-------

.. autosummary::
   :nosignatures:

   ~orbitals

.. toctree::
   :hidden:
   :maxdepth: 1

   orbitals
