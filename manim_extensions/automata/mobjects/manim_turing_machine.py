# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Turing machine visualization.

This module provides the ManimTuringMachine class for visualizing Turing machines.

"""

from manim import *


class ManimTuringMachine(VGroup):
    """Visual Turing machine.

    Provides a basic visual representation of a Turing machine
    with a tape and read/write head.

    Examples
    --------
    .. manim:: ManimTuringMachineExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_turing_machine import ManimTuringMachine

       class ManimTuringMachineExample(Scene):
           def construct(self):
               tm = ManimTuringMachine()
               symbols = "0101"
               cells = VGroup(*(Square(1) for _ in symbols)).arrange(RIGHT, buff=0)
               for cell, symbol in zip(cells, symbols):
                   cell.add(MathTex(symbol).move_to(cell))
               tm.remove(tm.tape)
               tm.tape = cells
               tm.remove(tm.head)
               tm.head = Triangle().scale(0.4).next_to(cells[0], UP, buff=0.1)
               tm.add(tm.tape, tm.head)
               self.add(tm)
    """

    def __init__(self) -> None:
        """Initialize the ManimTuringMachine instance."""
        super().__init__()
        self.tape = VGroup()
        self.head = Triangle()
        self.add(self.tape, self.head)