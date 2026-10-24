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

Usage
-----

The upstream plugin was funded by the University of Leeds. It currently
relies on `JFLAP <https://www.jflap.org>`_ files (``.jff``) to describe the
automaton; future updates are planned to let automata be built directly
without JFLAP.

Pass a JFLAP XML file to
:class:`~manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton`,
create a mobject for the input string with
:meth:`~manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton.construct_automaton_input`,
and play the generated step animations returned by
:meth:`~manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton.play_string`:

.. manim:: AutomatonStringAcceptance
   :ref_classes: ManimAutomaton ManimdeterministicFiniteAutomaton ManimAnimations

   from manim import *
   from manim_extensions.automata import (
       ManimAnimations,
       ManimdeterministicFiniteAutomaton,
   )

   class AutomatonStringAcceptance(Scene):
       def construct(self):
           dfa = ManimdeterministicFiniteAutomaton()
           self.add(dfa)
           dfa.manim_automata_input = dfa.construct_automaton_input("11")
           dfa.set_default_position_of_input_string()
           self.play(FadeIn(dfa.manim_automata_input))
           animations = ManimAnimations()
           q0 = dfa.get_initial_state()
           q2 = dfa.get_state("q2")
           self.play(animations.animate_highlight_state(q0))
           self.play(animations.animate_highlight_state(q2))
           result = "ACCEPTED" if dfa.check_automaton_result([q2]) else "REJECTED"
           verdict = Text(
               result, color=GREEN if result == "ACCEPTED" else RED
           ).next_to(dfa.manim_automata_input, UP)
           self.play(FadeIn(verdict))

Custom animations
^^^^^^^^^^^^^^^^^

Subclass :class:`~manim_extensions.automata.mobjects.manim_animations.ManimAnimations`
to override the animation methods, then pass an instance through the
``manim_animations`` argument:

.. code-block:: python

   from manim_extensions.automata import ManimAutomaton, ManimAnimations


   class CustomManimAnimations(ManimAnimations):

       def __init__(self) -> None:
           super().__init__()


   class Automaton(MovingCameraScene):
       def construct(self):
           manim_animations_instance = CustomManimAnimations()
           manim_automaton = ManimAutomaton(
               xml_file='example_machine.jff',
               manim_animations=manim_animations_instance,
           )

The upstream repository ships an ``manim_automata_examples`` directory with
finite-state, nondeterministic, and pushdown example scenes, and a helper
file listing every animation method that can be overridden. Example videos
for a `finite-state machine <https://youtu.be/beKkjIGdeQc>`_ and a
`nondeterministic finite-state machine <https://youtu.be/woaldsYmsHM>`_ are
linked from the README.

.. toctree::
   :hidden:
   :maxdepth: 1

   mobjects
   animations
   dependencies
   classes
   constants
   functions
