# SPDX-FileCopyrightText: 2022 Hammad Nasir
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Contains enums used throughout the package."""

from enum import Enum


class MArrayElementComp(Enum):
    """Refers to individual component :class:`~manim.mobject.mobject.Mobject`\ s of :class:`~manim_extensions.data_structures.m_array.MArrayElement`.

    Examples
    --------
    .. manim:: MArrayElementCompOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.data_structures.m_enum import MArrayElementComp

       MArrayElementCompTarget = MArrayElementComp

       class MArrayElementCompOverview(Scene):
           def construct(self):
               public = [n for n in dir(MArrayElementCompTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('MArrayElementComp', font_size=36),
                   Text('module: manim_extensions.data_structures.m_enum', font_size=18, color=GREY),
                   Text('Refers to individual component manim.mobject.mobject.Mobject\ s of manim_extensions.data_structures.m_array.MArrayElement', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.data_structures.m_enum import MArrayElementComp

        component = MArrayElementComp.BODY
    """

    BODY = 0
    """:class:`~manim.mobject.geometry.polygram.Square` that represents the body."""

    VALUE = 1
    """:class:`~manim.mobject.text.text_mobject.Text` that represents the value."""

    INDEX = 2
    """:class:`~manim.mobject.text.text_mobject.Text` that represents the index."""

    LABEL = 3
    """:class:`~manim.mobject.text.text_mobject.Text` that represents the label."""


class MArrayDirection(Enum):
    """Serves as the direction for :class:`~manim_extensions.data_structures.m_array.MArray`.

    Examples
    --------
    .. manim:: MArrayDirectionOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.data_structures.m_enum import MArrayDirection

       MArrayDirectionTarget = MArrayDirection

       class MArrayDirectionOverview(Scene):
           def construct(self):
               public = [n for n in dir(MArrayDirectionTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('MArrayDirection', font_size=36),
                   Text('module: manim_extensions.data_structures.m_enum', font_size=18, color=GREY),
                   Text('Serves as the direction for manim_extensions.data_structures.m_array.MArray', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.data_structures.m_enum import MArrayDirection

        direction = MArrayDirection.RIGHT
    """

    UP = 0
    """Upward direction."""

    DOWN = 1
    """Downward direction."""

    RIGHT = 2
    """Rightward direction."""

    LEFT = 3
    """Leftward direction."""
