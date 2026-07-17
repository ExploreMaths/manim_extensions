__all__ = [
    'Ruler',
]
# from manim import *
from manim.mobject.geometry.polygram import Rectangle
from manim.mobject.geometry.line import Line
from manim.mobject.types.vectorized_mobject import VGroup
from manim.utils.color import *
from manim.constants import *
import numpy as np

from ..utils.geometry_method import get_vecs_angle

class Ruler(VGroup):
    '''Ruler mobject.'''
    def __init__(
        self,
        length = 12,
        width = 0.8,
        ruler_color = WHITE,
        stroke_width = 2,
        fill_opacity = 0.4,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.ruler_length = length
        self.ruler_width = width
        self.ruler_color = ruler_color
        self.ruler = Rectangle(
            height = self.ruler_width,
            width = self.ruler_length,
            color = self.ruler_color,
            stroke_width = stroke_width,
            fill_opacity = fill_opacity,
        )
        self.add(self.ruler)

    def get_vecs_of_ruler(self):
        '''Return the extension and width directions of the ruler.'''
        A,B,C,_ = self.ruler.get_vertices()
        return Line(B,A).get_unit_vector(),Line(B,C).get_unit_vector()
    
    def get_direction_vector_of_ruler(self):
        '''Return the extension direction of the ruler.'''
        s,e,*_ = self.ruler.get_vertices()
        return Line(e,s).get_unit_vector()
    
    def get_width_vector_of_ruler(self):
        '''Return the width direction of the ruler.'''
        _,s,e,_ = self.ruler.get_vertices()
        return Line(e,s).get_unit_vector()
        
    def get_start_and_end(self):
        '''Return the start and end points of the ruler.'''
        E,S,*_ = self.ruler.get_vertices()
        return S,E
    
    def get_middle_point(self):
        '''Return the midpoint of the ruler.'''
        S,E = self.get_start_and_end()
        return (S+E)/2
    
    def get_length_of_ruler(self):
        '''Return the length of the ruler.'''
        S,E = self.get_start_and_end()
        return np.linalg.norm(E-S)

    def set_ruler(self,start = LEFT,end = RIGHT):
        '''
        Place the ruler so that one of its edges aligns with start and end.

        args
            start: start point of the ruler placement
            end: end point of the ruler placement
        '''
        direction = end - start
        current_pos = self.get_middle_point()
        target_pos = (start + end)/2

        self.rotate(
            angle = get_vecs_angle(
                self.get_direction_vector_of_ruler(),
                direction
            ),
            about_point = current_pos
        ).shift(target_pos - current_pos)
        return self
    
    def put_ruler_flat(self):
        '''Lay the ruler flat.'''
        self.rotate(
            angle = get_vecs_angle(
                self.get_direction_vector_of_ruler(),
                RIGHT
            )
        )
        return self