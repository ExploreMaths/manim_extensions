# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Apple Mobject for Pymunk physics simulations."""

from manim import *

class Apple(VMobject):
    """An apple-shaped Mobject built from Bezier curves.

    Parameters
    ----------
    **kwargs
        Forwarded to the parent :class:`~manim.mobject.types.vectorized_mobject.VMobject`.

    Examples
    --------
    .. manim:: AppleDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.pymunk import *

       class AppleDocExample(Scene):
           def construct(self):
               apples = VGroup(
                   Apple(color=RED, fill_color=RED, fill_opacity=0.6),
                   Apple(color=GREEN, fill_color=GREEN, fill_opacity=0.6),
                   Apple(color=YELLOW, fill_color=YELLOW, fill_opacity=0.6),
               )
               apples.arrange(RIGHT, buff=0.6).scale(0.8)
               self.add(apples)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 贝塞尔曲线点集
        points = np.array(
            [
                [0.10526316, -0.47368421, 0.0],
                [-0.94736842, -0.89473684, 0.0],
                [-0.52631579, 1.0, 0.0],
                [0.10526316, 0.47368421, 0.0],
                [0.10526316, 0.47368421, 0.0],
                [0.84210526, 1.0, 0.0],
                [0.94736842, -0.89473684, 0.0],
                [0.10526316, -0.47368421, 0.0],
                [0.10526316, -0.47368421, 0.0],
                [0.31578947, -0.78947368, 0.0],
                [0.42105263, -0.68421053, 0.0],
                [0.52631579, -0.78947368, 0.0],
                [0.52631579, -0.78947368, 0.0],
                [0.52631579, -1.0, 0.0],
                [0.10526316, -0.78947368, 0.0],
                [0.10526316, -0.47368421, 0.0],
            ]
        )
        points[:, 1] *= -1
        self.set_points(points)