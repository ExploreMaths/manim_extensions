# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Color schemes for neural network visualization."""

from manim import BLACK, BLUE, ORANGE, WHITE, ManimColor
from dataclasses import dataclass

@dataclass
class ColorScheme:
    """TODO: add docstring for ColorScheme."""
    primary_color: ManimColor
    secondary_color: ManimColor
    active_color: ManimColor
    text_color: ManimColor
    background_color: ManimColor

dark_mode = ColorScheme(
    primary_color=BLUE,
    secondary_color=WHITE,
    active_color=ORANGE,
    text_color=WHITE,
    background_color=BLACK
)

light_mode = ColorScheme(
    primary_color=BLUE,
    secondary_color=BLACK,
    active_color=ORANGE,
    text_color=BLACK,
    background_color=WHITE
)