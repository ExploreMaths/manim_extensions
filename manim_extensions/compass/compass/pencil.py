# from manim import *
__all__ = [
    'Pencil',
]
from pathlib import Path

from manim.mobject.svg.svg_mobject import SVGMobject
from manim.mobject.geometry.line import Line
from manim.constants import PI,ORIGIN

class Pencil(SVGMobject):
    '''Pencil mobject.

    .. manim:: PencilDocExample
        :save_last_frame:

        from manim import *
        from manim_extensions.compass import Pencil

        class PencilDocExample(Scene):
            def construct(self):
                pencil = Pencil().to_edge(LEFT)
                self.add(pencil)
    '''
    def __init__(self, height = 2,angle = PI/4):
        super().__init__(
            file_name = Path(__file__).resolve().parent / "assets/pencil.svg",
            height = height
        )
        self.rotate(angle = -angle)
        self._nib = self.submobjects[3]

    def get_nib(self):
        '''Return the position of the nib.

        .. manim:: GetNibDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Pencil

            class GetNibDocExample(Scene):
                def construct(self):
                    pencil = Pencil().to_edge(LEFT)
                    dot = Dot(pencil.get_nib())
                    self.add(pencil, dot)
        '''
        return self._nib.get_all_points()[7]
    
    def get_nid_vector(self):
        '''Return the direction of the pencil body.

        .. manim:: GetNidVectorDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Pencil

            class GetNidVectorDocExample(Scene):
                def construct(self):
                    pencil = Pencil().to_edge(LEFT)
                    v = pencil.get_nid_vector()
                    arrow = Arrow(pencil.get_nib(), pencil.get_nib() + v)
                    self.add(pencil, arrow)
        '''
        return Line(
            self.get_nib(),
            self.submobjects[1].get_center()
        ).get_unit_vector()
    
    def move_nid_to(self,point = ORIGIN):
        '''Translate the pencil so that the nib moves to point.

        .. manim:: MoveNidToDocExample
            :save_last_frame:

            from manim import *
            from manim_extensions.compass import Pencil

            class MoveNidToDocExample(Scene):
                def construct(self):
                    pencil = Pencil().move_nid_to(ORIGIN)
                    self.add(pencil)
        '''
        self.shift(
            point - self.get_nib()
        )
        return self