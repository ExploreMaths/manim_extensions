# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Automata visualisation package.

This package exposes animated finite-state and pushdown automaton mobjects for
building teaching and algorithm visualisations in Manim.
"""

from .mobjects.manim_automaton import *
from .mobjects.manim_deterministic_finite_state_automaton import *
from .mobjects.manim_non_deterministic_finite_state_automaton import *
from .mobjects.manim_animations import *
from .mobjects.manim_pushdown_automaton import *
from .mobjects.manim_turing_machine import *
from .mobjects.manim_state import *
from .mobjects.manim_transition import *
from .mobjects.manim_automaton_input import *

from .mobjects.manim_non_deterministic_finite_state_automaton import (
    nfa_automaton_json as _nfa_automaton_json,
)
from .mobjects.manim_pushdown_automaton import (
    pushdown_automaton_json as _pushdown_automaton_json,
)

#: Example non-deterministic finite automaton definition.
nfa_automaton_json = _nfa_automaton_json
#: Example pushdown automaton definition.
pushdown_automaton_json = _pushdown_automaton_json

__all__ = [
    "ManimAutomaton",
    "ManimDeterministicFiniteAutomaton",
    "ManimNondeterministicFiniteAutomaton",
    "ManimAnimations",
    "ManimPushDownAutomaton",
    "ManimTuringMachine",
    "ManimState",
    "ManimTransition",
    "ManimPushDownAutomatonTransition",
    "ManimAutomataInput",
    "Token",
    "PushDownAutomatonRule",
    "nfa_automaton_json",
    "pushdown_automaton_json",
]
