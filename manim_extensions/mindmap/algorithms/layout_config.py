__all__ = [
    'LayoutConfig',
    'LayoutDirection',
    'LayoutType'
]
from enum import Enum
from typing import List,Dict
import numpy as np
from manim.constants import LEFT, RIGHT, UP, DOWN,PI

class LayoutDirection(Enum):
    '''Layout direction.

    '''
    LeftToRight = 'left to right'
    RightToLeft = 'right to left'
    TopToBottom = 'top to bottom'
    BottomToTop = 'bottom to top'

class LayoutType(Enum):
    '''Layout algorithm.

    '''
    MindMap = 'tidytree'
    TimeLine = 'timeline'
    Standard = 'standard'
    Catalog = 'catalog'

class LayoutConfig:
    """
    """

    def __init__(
        self,
        direction:np.ndarray = RIGHT,
        node_spacing:float = 0.5,
        level_spacing:float = 0.5,
        sides:np.ndarray | List[np.ndarray] = (UP,DOWN)
    ):
        '''Layout parameters
        
        Parameters
        ----------
        direction : np.ndarray, optional
            Layout direction. Defaults to RIGHT.
        node_spacing : float, optional
            Spacing between nodes. Defaults to 0.5.
        level_spacing : float, optional
            Spacing between layers. Defaults to 0.5.
        sides : np.ndarray | List[np.ndarray], optional
            Sides used for alternating timeline layouts; a single value means single-sided. Defaults to (UP,DOWN).
        '''
        if not any(np.array_equal(direction, d) for d in [UP, DOWN, LEFT, RIGHT]):
            raise ValueError(f'direction must be one of {LEFT,RIGHT,UP,DOWN}')
        if not isinstance(sides, (list,tuple)):
            sides = (sides,)
        for side in sides:
            if not any(np.array_equal(side, d) for d in [UP, DOWN]):
                raise ValueError(f'side must be one of {UP,DOWN}')
        
        self.sides = tuple(self.get_layout_direction(side) for side in sides)
        self.layout_direction = self.get_layout_direction(direction)
        self.node_spacing = node_spacing
        self.level_spacing = level_spacing
        self.direction = direction

    def get_layout_direction(self,direction:np.ndarray) -> LayoutDirection:
        """Convert a direction vector to a LayoutDirection enum."""
        string = None
        if np.array_equal(direction,UP):
            string = LayoutDirection.BottomToTop
        elif np.array_equal(direction,DOWN):
            string = LayoutDirection.TopToBottom
        elif np.array_equal(direction,LEFT):
            string = LayoutDirection.RightToLeft
        elif np.array_equal(direction,RIGHT):
            string = LayoutDirection.LeftToRight
        return string
    
    @property
    def catalog(self):
        return {
            'node_spacing':self.node_spacing,
            'level_spacing':self.level_spacing,
        }
    
    @catalog.setter
    def catalog(
        self,
        catalog:Dict = {
            'node_spacing':0.5,
            'level_spacing':0.5,
        }
    ):
        self.node_spacing = catalog.get('node_spacing',0.5)
        self.level_spacing = catalog.get('level_spacing',0.5)
    
    @property
    def mindmap(self):
        return {
            'direction':self.layout_direction,
            'node_spacing':self.node_spacing,
            'level_spacing':self.level_spacing,
        }
    
    @mindmap.setter
    def mindmap(
        self,
        mindmap:Dict = {
            'direction':RIGHT,
            'node_spacing':0.5,
            'level_spacing':0.5
        }
    ):
        direction = mindmap.get('direction',RIGHT)
        if not any(np.array_equal(direction, d) for d in [UP, DOWN, LEFT, RIGHT]):
            raise ValueError(f'direction must be one of {LEFT,RIGHT,UP,DOWN}')
        self.direction = direction
        self.layout_direction = self.get_layout_direction(direction)
        self.node_spacing = mindmap.get('node_spacing',0.5)
        self.level_spacing = mindmap.get('level_spacing',0.5)

    @property
    def timeline(self):
        return {
            'node_spacing':self.node_spacing,
            'level_spacing':self.level_spacing,
            'sides':self.sides,
        }
    
    @timeline.setter
    def timeline(
        self,
        timeline:Dict = {
            'node_spacing':0.5,
            'level_spacing':0.5,
            'sides':(UP,DOWN)
        }
    ):
        self.node_spacing = timeline.get('node_spacing',0.5)
        self.level_spacing = timeline.get('level_spacing',0.5)
        sides = timeline.get('sides',(UP,DOWN))
        if not isinstance(sides, (list,tuple)):
            sides = (sides,)
        for side in sides:
            if not any(np.array_equal(side, d) for d in [UP, DOWN]):
                raise ValueError(f'side must be one of {UP,DOWN}')
        self.sides = tuple(self.get_layout_direction(side) for side in sides)