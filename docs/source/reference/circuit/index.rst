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

.. toctree::
   :maxdepth: 1

   mobjects
   helpers
   functions
