# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Scene classes for Manim ML visualizations.

This module provides custom scene classes for machine learning visualizations.

"""

from manim import *


class ManimML3DScene(ThreeDScene):
    """
    This is a wrapper class for the Manim ThreeDScene

    Note: the primary purpose of this is to make it so
    that everything inside of a layer
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def play(self):
        """ """
        pass