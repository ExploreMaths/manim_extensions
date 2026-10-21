.. SPDX-FileCopyrightText: 2022 Sean Nelson
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Automata
========

.. vendored-status:: SeanNelsonIO/manim-automata

**Original author:** `Sean Nelson <https://github.com/SeanNelsonIO>`_

**Source repository:** `GitHub <https://github.com/SeanNelsonIO/manim-automata>`_

**License:** MIT (see the upstream repository for the full license text)

``manim-automata`` is a finite-state-machine toolkit for Manim. It is designed
for teaching automata, machine execution, and state transitions in a clear,
scene-ready format.

The code is bundled inside ``manim_extensions`` as the
``manim_extensions.automata`` subpackage.

Features
--------

- :class:`~manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton` – main automaton display object.
- :class:`~manim_extensions.automata.mobjects.automata_dependencies.state.State` and :class:`~manim_extensions.automata.mobjects.automata_dependencies.transition.Transition` helpers for state and edge rendering.
- finite-state, nondeterministic, and pushdown examples.
- input token and machine-step rendering for state execution demos.
- animation helpers for demonstrating transitions and accepted strings.

.. toctree::
   :maxdepth: 1

   mobjects
   animations
   dependencies
   classes
   constants
   functions
