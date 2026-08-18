# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Automata visualisation package.

This package exposes animated finite-state and pushdown automaton mobjects for
building teaching and algorithm visualisations in Manim.

"""

from .mobjects.manim_automaton import *
from .mobjects.manim_determinstic_finite_state_automaton import *
from .mobjects.manim_non_determinstic_finite_state_automaton import *
from .mobjects.manim_animations import *
from .mobjects.manim_pushdown_automaton import *

__all__ = ["ManimAutomaton", "ManimDeterminsticFiniteAutomaton", "ManimNonDeterminsticFiniteAutomaton", "ManimAnimations", "ManimPushDownAutomaton"]