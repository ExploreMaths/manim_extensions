# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

""":class:`~manim_extensions.automata.mobjects.automata_dependencies.transition.Transition` representation for automata.

This module provides the :class:`~manim_extensions.automata.mobjects.automata_dependencies.transition.Transition` class for representing state transitions in automata.
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence
from typing import Protocol

from .state import State


class ReadSymbol(Protocol):
    r"""Protocol for a transition symbol that exposes its TeX source.

    Examples
    --------
    .. manim:: ReadSymbolScene
       :save_last_frame:

       from manim import *

       class ReadSymbolScene(Scene):
           def construct(self):
               self.add(MathTex(r"\rightarrow"))
    """

    tex_string: str


class Transition:
    """A transition between two states.

    Parameters
    ----------
    transition_from
        Origin state.
    transition_to
        Target state.

    Examples
    --------
    .. manim:: TransitionScene
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.automata_dependencies.state import State
       from manim_extensions.automata.mobjects.automata_dependencies.transition import Transition

       class TransitionScene(Scene):
           def construct(self):
               source = State("q0", Point())
               target = State("q1", Point().shift(RIGHT * 3))
               transition = Transition(source, target)
               self.add(Dot(), Arrow(ORIGIN, RIGHT * 3))
    """

    id_iter = itertools.count()

    #: Symbols read by this transition.
    read_symbols: Sequence[ReadSymbol] = ()

    def __init__(self, transition_from: State, transition_to: State) -> None:
        self.id = next(self.id_iter)
        self.transition_from = transition_from
        self.transition_to = transition_to
