# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Color schemes for neural network visualization."""

from manim import *
from dataclasses import dataclass

@dataclass
class ColorScheme:
    primary_color: str
    secondary_color: str
    active_color: str
    text_color: str
    background_color: str

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