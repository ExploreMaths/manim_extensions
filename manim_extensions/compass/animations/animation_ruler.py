__all__ = [
    'PutRuler',
    'PutRulerAway'
]
# from manim import *
from manim.mobject.types.point_cloud_mobject import Point
from manim.animation.transform import ApplyMethod
from manim.constants import RIGHT, LEFT, UP, DOWN

from ..compass.ruler import Ruler

class PutRuler(ApplyMethod):
    """Compass-and-straightedge animation: rotate the ruler so that one of its edges aligns with start-end.

    .. manim:: PutRulerDocExample

       from manim import *
       from manim_extensions.compass import Ruler, PutRuler

       class PutRulerDocExample(Scene):
           def construct(self):
               ruler = Ruler().to_edge(LEFT)
               self.play(PutRuler(ruler, LEFT, RIGHT))
               self.wait()

    Parameters
    ----------
        ruler : Ruler
            The ruler.
        start : Point
            The start point.
        end : Point
            The end point."""
    def __init__(
        self,
        ruler:Ruler,
        start:Point = None,
        end:Point = None,
        **kwargs
    ):
        """Initialize PutRuler."""
        super().__init__(
            ruler.set_ruler,
            start,
            end,
            **kwargs
        )

class PutRulerAway(PutRuler):
    """Put the ruler away: move the ruler to point.

    .. manim:: PutRulerAwayDocExample

       from manim import *
       from manim_extensions.compass import Ruler, PutRulerAway

       class PutRulerAwayDocExample(Scene):
           def construct(self):
               ruler = Ruler().to_edge(LEFT)
               self.play(PutRulerAway(ruler, 2 * DOWN))
               self.wait()

    Parameters
    ----------
        ruler : Ruler
            The ruler.
        point : Point
            The placement position.
        is_flat : bool
            Whether to place it horizontally (or vertically)."""
    def __init__(
        self,
        ruler:Ruler,
        point:Point = None,
        is_flat:bool = True,
        **kwargs
    ):
        """Initialize PutRulerAway."""
        if is_flat:
            start = point + LEFT
            end = point + RIGHT
        else:
            start = point + UP
            end = point + DOWN
        super().__init__(
            ruler,
            start,
            end,
            **kwargs
        )