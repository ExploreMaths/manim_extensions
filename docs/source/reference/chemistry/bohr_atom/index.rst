.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

bohr_atom
=========

.. module:: manim_extensions.chemistry.bohr_atom

Classes
-------

.. autosummary::
   :nosignatures:

   ~bohr_atom.BohrAtom

Usage
-----

Draw a Bohr atom with a chosen number of protons, neutrons, and electrons.

.. manim:: BohrScene
   :ref_classes: BohrAtom

   from manim import *
   from manim_extensions.chemistry.bohr_atom import BohrAtom

   class BohrScene(Scene):
       def construct(self):
           atom = BohrAtom(e=14, p=14, n=10)
           self.play(FadeIn(atom))

Modules
-------

.. autosummary::
   :nosignatures:

   ~bohr_atom

.. toctree::
   :hidden:
   :maxdepth: 1

   bohr_atom
