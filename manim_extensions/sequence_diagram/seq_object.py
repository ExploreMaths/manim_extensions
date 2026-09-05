# SPDX-FileCopyrightText: 2023 Thomas Chen
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Sequence diagram object for Manim.

This module provides object class for sequence diagrams.

"""

from manim import *


class SeqObject(VGroup):
    """Named object shown inside a sequence diagram.

    Parameters
    ----------
        name : str
            Object name displayed inside the box.
        font_size : float, optional
            Font size of the label. Defaults to ``18``.

    Examples
    --------
    .. manim:: SeqObjectExample

       from manim import *
       from manim_extensions.sequence_diagram.seq_action import SeqAction
       from manim_extensions.sequence_diagram.seq_actor import SeqActor
       from manim_extensions.sequence_diagram.seq_object import SeqObject

       class SeqObjectExample(Scene):
           def construct(self):
               alice = SeqActor("Alice")
               bob = SeqActor("Bob")
               order = SeqObject("Order")
               self.play(*SeqAction.introduce_actors(alice, bob))
               self.play(*SeqAction.subject_gives_gift_to_target(alice, order, bob))
               self.play(*SeqAction.subject_gives_gift_to_target(bob, order, alice))
               self.wait()
    """

    def __init__(self, name: str, font_size: float = 18):
        """Initialize SeqObject."""
        self.obj_name = name
        obj_label = self.create_obj_label(font_size)
        obj_ctn = Rectangle(
            color="#00FF00", height=obj_label.height + 0.5, width=obj_label.width + 0.4
        )
        obj_label.align_to(obj_ctn, ORIGIN)
        super().__init__(obj_ctn, obj_label)

    def create_obj_label(self, font_size: float = 18):
        """Build the text label shown inside the object box.

        Parameters
        ----------
        font_size : float, optional
            Font size used for the label (default ``18``).

        Returns
        -------
        Text
            A white :class:`~manim.mobject.text.text_mobject.Text` mobject
            displaying the object name.
        """
        return Text(self.obj_name, font_size=font_size).set_color(WHITE)