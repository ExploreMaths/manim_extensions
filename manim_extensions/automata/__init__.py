"""Automata visualisation package.

This package exposes animated finite-state and pushdown automaton mobjects for
building teaching and algorithm visualisations in Manim.

Examples
--------
.. manim:: AutomataPackageDocExample
   :save_last_frame:

   from manim import *
   from manim_extensions.automata import ManimDeterminsticFiniteAutomaton

   class AutomataPackageDocExample(Scene):
       def construct(self):
           dfa = ManimDeterminsticFiniteAutomaton()
           self.add(dfa)
"""

from .mobjects.manim_automaton import *
from .mobjects.manim_determinstic_finite_state_automaton import *
from .mobjects.manim_non_determinstic_finite_state_automaton import *
from .mobjects.manim_animations import *
from .mobjects.manim_pushdown_automaton import *

__all__ = ["ManimAutomaton", "ManimDeterminsticFiniteAutomaton", "ManimNonDeterminsticFiniteAutomaton", "ManimAnimations", "ManimPushDownAutomaton"]