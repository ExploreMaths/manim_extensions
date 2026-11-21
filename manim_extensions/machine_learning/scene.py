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
    .. code-block:: python

        from manim_extensions.machine_learning.scene import ManimML3DScene

        class MyScene(ManimML3DScene):
            def construct(self):
                self.wait()
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
