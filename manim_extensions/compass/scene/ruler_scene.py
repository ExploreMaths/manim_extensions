# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Scene that draws lines with a ruler and a pencil.

:class:`SingleRulerScene` extends :class:`~manim.scene.moving_camera_scene.MovingCameraScene`
with helper methods to lay down a ruler, draw a line with the pencil, and
return the ruler to its resting position.
"""

__all__ = ["SingleRulerScene"]

from manim.animation.composition import AnimationGroup
from manim.animation.transform import Restore
from manim.constants import DOWN, RIGHT
from manim.mobject.geometry.line import Line
from manim.scene.moving_camera_scene import MovingCameraScene
from manim.utils.color import WHITE

from ..animations import DrawPath
from ..compass import Pencil, Ruler


class SingleRulerScene(MovingCameraScene):
    """A scene that provides a ruler and a pencil for drawing lines.

    Examples
    --------

    .. manim:: SingleRulerSceneExample
       :save_last_frame:

       from manim_extensions.compass import SingleRulerScene

       class SingleRulerSceneExample(SingleRulerScene):
           def construct(self):
               self.draw_line_with_pencil(LEFT, 3 * UR)
               self.put_ruler_back()
    """

    def setup(self) -> None:
        """Place the ruler at the bottom edge and the pencil at the right edge."""
        self.ruler = Ruler(width=0.4, length=8).to_edge(DOWN)
        self.pencil = Pencil(height=1).to_edge(RIGHT)
        self.pen_pos = self.pencil.get_center()
        self.ruler.save_state()

    def draw_line_with_pencil(
        self, start, end, added_anims=None, **kwargs
    ):
        """Draw a :class:`~manim.mobject.geometry.line.Line` from ``start`` to ``end``.

        Parameters
        ----------
        start
            The start point of the line.
        end
            The end point of the line.
        added_anims
            Extra animations to play alongside the drawing, if any.
        run_time
            Total run time for the two plays.
        color
            The stroke color of the line.
        stroke_width
            The stroke width of the line.

        Returns
        -------
        Line
            The line that was drawn.
        """
        run_time = kwargs.pop("run_time", 1.0)
        color = kwargs.pop("color", WHITE)
        stroke_width = kwargs.pop("stroke_width", 4)
        line = Line(start, end, color=color, stroke_width=stroke_width)
        self.play(
            AnimationGroup(
                self.ruler.animate.set_ruler(start, end),
                self.pencil.animate.move_nid_to(start),
                lag_ratio=1.0,
            ),
            run_time=0.5 * run_time,
        )
        anims = [DrawPath(self.pencil, line)]
        if added_anims is not None:
            anims.extend(added_anims)
        self.play(*anims, run_time=0.5 * run_time, **kwargs)
        return line

    def put_ruler_back(self, added_anims=None, run_time=0.5, **kwargs):
        """Restore the ruler to its saved state and move the pencil back."""
        anims = [
            Restore(self.ruler),
            self.pencil.animate.move_to(self.pen_pos),
        ]
        if added_anims is not None:
            anims.extend(added_anims)
        self.play(*anims, run_time=run_time, **kwargs)
