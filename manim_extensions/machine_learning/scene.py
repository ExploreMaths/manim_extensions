# SPDX-FileCopyrightText: 2026 MathItYT
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: forward play to ThreeDScene instead of silently doing nothing

"""Scene classes for Manim ML visualizations.

This module provides custom scene classes for machine learning visualizations.

"""

from typing import Any

from manim import ThreeDScene


class ManimML3DScene(ThreeDScene):
    """
    This is a wrapper class for the Manim ThreeDScene.

    .. note::

       the primary purpose of this is to make it so
       that everything inside of a layer


    Parameters
    ----------
    args
        Positional arguments forwarded to
        :class:`~manim.scene.three_d_scene.ThreeDScene`.
    **kwargs
        Forwarded to :class:`~manim.scene.three_d_scene.ThreeDScene`.

    Examples
    --------
    .. manim:: ManimML3DPreview
       :save_last_frame:

       from manim import *
       from manim_extensions.machine_learning.neural_network.architectures.feed_forward import FeedForwardNeuralNetwork
       from manim_extensions.machine_learning.scene import ManimML3DScene

       class ManimML3DPreview(ManimML3DScene):
           def construct(self):
               network = FeedForwardNeuralNetwork([3, 4, 2])
               network.scale_to_fit_height(5.0)
               self.add(network)
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[no-untyped-call]

    def play(self, *args: Any, **kwargs: Any) -> Any:
        """Override :meth:`~manim.scene.scene.Scene.play` for ML scenes.

        Parameters
        ----------
        args
            Positional arguments forwarded to
            :meth:`~manim.scene.scene.Scene.play`.
        **kwargs
            Forwarded to :meth:`~manim.scene.scene.Scene.play`.


            Returns
            -------
                The resulting value.
        """
        super().play(*args, **kwargs)
