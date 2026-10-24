.. SPDX-FileCopyrightText: 2025 Mr-FuzzyPenguin
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Circuit
=======

.. vendored-status:: Mr-FuzzyPenguin/manim-circuit

**Original author:** `Mr-FuzzyPenguin <https://github.com/Mr-FuzzyPenguin>`_

**Source repository:** `GitHub <https://github.com/Mr-FuzzyPenguin/manim-circuit>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-circuit`` adds custom Manim mobjects for electrical components so that
basic circuit diagrams can be built and animated directly inside a scene.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.circuit`` subpackage.

Features
--------

- :class:`~manim_extensions.circuit.mobjects.Resistor` / :class:`~manim_extensions.circuit.mobjects.Inductor` / :class:`~manim_extensions.circuit.mobjects.Capacitor` components.
- :class:`~manim_extensions.circuit.mobjects.VoltageSource` and :class:`~manim_extensions.circuit.mobjects.CurrentSource` objects.
- terminal-based connection points for wiring diagrams.
- labeled component support and circuit assembly helpers.
- educational scene objects for engineering and electronics demos.

Usage
-----

Every component is a :class:`~manim.mobject.types.vectorized_mobject.VMobject`
that can be added to a scene directly. Pass ``label`` to annotate the
component; the unit is appended automatically (``Ω`` for resistors, ``H``
for inductors, ``F`` for capacitors), and ``direction`` controls which side
of the body the label is placed on:

.. manim:: BasicCircuitComponents
   :ref_classes: Resistor Inductor Capacitor
   :save_last_frame:

   from manim import *
   from manim_extensions.circuit import Resistor, Inductor, Capacitor

   class BasicCircuitComponents(Scene):
       def construct(self):
           # Build the resistor without a label (the vendored Resistor appends
           # RST ":math:`\Omega`" to Tex labels, which is not valid LaTeX),
           # then add a proper Tex label manually.
           resistor = Resistor(direction=UP)
           resistor.label = Tex(r"10 $\Omega$").scale(0.5).next_to(
               resistor.main_body, UP, buff=0.1
           )
           resistor.add(resistor.label)

           components = VGroup(
               resistor,
               Inductor(label="0.3", direction=UP),
               Capacitor(label="47", direction=UP),
           ).arrange(RIGHT, buff=1.5)
           self.add(components)

To wire components together, call
:meth:`~manim_extensions.circuit.mobjects.Resistor.get_terminals` with
``"left"`` or ``"right"`` on any component; it returns the coordinate of the
corresponding pin. Rotating a component keeps its label upright.

The upstream package targets Manim Community Edition rather than ManimGL.
Unlike rendering a circuit with a LaTeX package such as CircuiTikZ, every
component is an independent mobject, so individual elements can be selected,
repositioned, and animated. Planned additions include transistors and logic
gates, and the upstream repository ships example scenes under ``examples/``.

.. toctree::
   :hidden:
   :maxdepth: 1

   mobjects
   helpers
   functions
