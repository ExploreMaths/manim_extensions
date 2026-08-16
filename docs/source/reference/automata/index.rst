Automata
========

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
- :class:`~manim_extensions.automata.mobjects.automata_dependencies.state.State` and :class:`~manim_extensions.automata.mobjects.automata_dependencies.transitition.Transition` helpers for state and edge rendering.
- finite-state, nondeterministic, and pushdown examples.
- input token and machine-step rendering for state execution demos.
- animation helpers for demonstrating transitions and accepted strings.

Quick start
-----------

.. manim:: AutomataLibraryExample
   :save_last_frame:

   from manim import *
   from manim_extensions.automata import ManimAutomaton

   class AutomataLibraryExample(Scene):
       def construct(self):
           automaton = ManimAutomaton()
           self.add(automaton)

This library is most useful for:

* formal-language lectures,
* state-machine explanations,
* parsing and acceptance demonstrations,
* visual explanations of nondeterministic and stack-like transitions.

See the `original README <https://github.com/SeanNelsonIO/manim-automata/blob/main/README.md>`_
for more complete examples and API walkthroughs.

.. toctree::
   :hidden:

   mobjects
   animations
   dependencies
   functions