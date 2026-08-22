# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


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
               self.add(tm)
    """

    def __init__(self) -> None:
        """Initialize the ManimTuringMachine instance."""
        super().__init__()
        self.tape = VGroup()
        self.head = Triangle()
        self.add(self.tape, self.head)
