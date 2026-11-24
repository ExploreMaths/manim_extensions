.. SPDX-FileCopyrightText: 2022 Sean Nelson
.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

mobjects
========

.. module:: manim_extensions.automata.mobjects

Usage
-----

Build a deterministic finite automaton from a JFLAP XML file and add it to a scene.

.. manim:: DFAScene
   :save_last_frame:
   :ref_classes: ManimdeterministicFiniteAutomaton

   from manim import *
   from manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton import (
       ManimdeterministicFiniteAutomaton,
   )

   class DFAScene(Scene):
       def construct(self):
           dfa = ManimdeterministicFiniteAutomaton()
           dfa.scale_to_fit_width(9)
           self.add(dfa)

Modules
-------

.. autosummary::
   :nosignatures:

   ~automata_dependencies
   ~manim_animations
   ~manim_automaton
   ~manim_automaton_input
   ~manim_cli
   ~manim_deterministic_finite_state_automaton
   ~manim_non_deterministic_finite_state_automaton
   ~manim_pushdown_automaton
   ~manim_state
   ~manim_transition
   ~manim_turing_machine

.. toctree::
   :hidden:
   :maxdepth: 1

   automata_dependencies/index
   manim_animations
   manim_automaton
   manim_automaton_input
   manim_cli
   manim_deterministic_finite_state_automaton
   manim_non_deterministic_finite_state_automaton
   manim_pushdown_automaton
   manim_state
   manim_transition
   manim_turing_machine
