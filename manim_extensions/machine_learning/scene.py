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

    Parameters
    ----------
    args : tuple
        Positional arguments forwarded to
        :class:`~manim.scene.three_d_scene.ThreeDScene`.
    **kwargs
        Forwarded to :class:`~manim.scene.three_d_scene.ThreeDScene`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def play(self):
        """ """
        pass