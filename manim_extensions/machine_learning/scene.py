# SPDX-FileCopyrightText: 2026 MathItYT
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Scene classes for Manim ML visualizations.

This module provides custom scene classes for machine learning visualizations.

"""

from typing import Any

from manim import ThreeDScene


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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the scene."""
        super().__init__(*args, **kwargs)

    def play(self, *args: Any, **kwargs: Any) -> None:
        """Override :meth:`~manim.scene.three_d_scene.ThreeDScene.play` for ML scenes.

        Parameters
        ----------
        args : tuple
            Positional arguments forwarded to
            :meth:`~manim.scene.three_d_scene.ThreeDScene.play`.
        **kwargs
            Forwarded to :meth:`~manim.scene.three_d_scene.ThreeDScene.play`.
        """
        pass