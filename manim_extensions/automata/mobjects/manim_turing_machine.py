# SPDX-FileCopyrightText: 2022 Sean Nelson
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *


class ManimTuringMachine(VGroup):
    """Visual Turing machine.

    .. note::

        This class is a placeholder.  The Turing machine visualisation has
        not been implemented yet.  Instantiating it raises
        :class:`~builtins.NotImplementedError`.

    Examples
    --------
    .. manim:: ManimTuringMachineExample
       :save_last_frame:

       from manim import *
       from manim_extensions.automata.mobjects.manim_turing_machine import ManimTuringMachine

       class ManimTuringMachineExample(Scene):
           def construct(self):
               try:
                   tm = ManimTuringMachine()
               except NotImplementedError as e:
                   label = Text(str(e), font_size=24)
                   self.add(label)
"""
    def __init__(self) -> None:
        """Initialize the ManimTuringMachine instance."""
        super().__init__()
        raise NotImplementedError("Not implemented!")