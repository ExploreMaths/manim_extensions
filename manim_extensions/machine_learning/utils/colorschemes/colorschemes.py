# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: document module-level constants

"""Color schemes for neural network visualization."""

from manim import BLACK, BLUE, ORANGE, WHITE, ManimColor
from dataclasses import dataclass


@dataclass
class ColorScheme:
    """Color palette used by the machine learning visualizations.

    Parameters
    ----------
    primary_color
        Main color of the visualization (e.g. neurons and edges).
    secondary_color
        Secondary color (e.g. axes and supporting elements).
    active_color
        Color used to highlight active elements during animations.
    text_color
        Color of titles and labels.
    background_color
        Scene background color; applied to ``manim.config`` when the
        scheme is activated.

    Examples
    --------
    .. manim:: ColorSchemeOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.utils.colorschemes.colorschemes import ColorScheme

       ColorSchemeTarget = ColorScheme

       class ColorSchemeOverview(Scene):
           def construct(self):
               public = [n for n in dir(ColorSchemeTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('ColorScheme', font_size=36),
                   Text('module: manim_extensions.machine_learning.utils.colorschemes.colorschemes', font_size=18, color=GREY),
                   Text('Color palette used by the machine learning visualizations', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        from manim_extensions.machine_learning.utils.colorschemes.colorschemes import ColorScheme

        scheme = ColorScheme()
    """

    primary_color: ManimColor
    secondary_color: ManimColor
    active_color: ManimColor
    text_color: ManimColor
    background_color: ManimColor


#: Colour scheme with light elements on a black background.
dark_mode = ColorScheme(
    primary_color=BLUE,
    secondary_color=WHITE,
    active_color=ORANGE,
    text_color=WHITE,
    background_color=BLACK,
)

#: Colour scheme with dark elements on a white background.
light_mode = ColorScheme(
    primary_color=BLUE,
    secondary_color=BLACK,
    active_color=ORANGE,
    text_color=BLACK,
    background_color=WHITE,
)
