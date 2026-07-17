__all__ = [
    'MindMap',
    'TimeLine',
    'StandardMap',
    'CatalogMap'
]
from typing import Dict

from manim.constants import *
from manim.utils.color import *

from .base import NodeMobject,AbstractMap,generate_tree
from ..nodes import Node,NodeStyle,bfs_walker
from ..algorithms import (
    TidyTreeLayout,
    TimeLineLayout,
    StandardLayout,
    CatalogLayout,
    LayoutConfig,
    LayoutType,
)
    
class MindMap(AbstractMap):
    """
    Mind map class: parses mind-map data in the following format and builds
    the corresponding mind-map object.

    Example::

        mindmap = {
            'node': r'Sphere volume',
            'text': 'Text used for TTS narration',
            'child': [
                {
                    'node': r'3rd century BC',  # or a VMobject / Mobject
                    'child': [
                        {'node': r'Archimedes: method of exhaustion'}
                    ]
                },
                {
                    'node': r'3rd century AD',
                    'child': [
                        {'node': r'Nine Chapters on the Mathematical Art'},
                        {
                            'node': r'Liu Hui: Mouhefanggai',
                            'child': [
                                {'node': r'Sphere and Mouhefanggai'},
                                {'node': r'Volume of Mouhefanggai?'}
                            ]
                        }
                    ]
                },
                {
                    'node': r'5th century AD',
                    'child': [
                        {'node': r'Zu Geng: Cavalieri principle'}
                    ]
                },
                {
                    'node': r'17th century AD',
                    'child': [
                        {'node': r'Kepler'},
                        {'node': r'Cavalieri principle'}
                    ]
                },
                {
                    'node': r'18th century AD',
                    'child': [
                        {'node': r'Matsunaga Yoshisuke'}
                    ]
                }
            ]
        }

        mind = MindMap(mindmap)
        mind.scale_to_fit_width(12)
        self.play(FadeIn(mind))
    """
    def __init__(
        self,
        map:Dict = {},
        buff:float = 0.2,
        direction = RIGHT,
        level_spacing = 1.0,
        node_spacing = 0.5,
        node_style :NodeStyle = NodeStyle(
            node_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            line_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            text_style = [
                {'color':RED,'font_size':64},
                {'color':YELLOW,'font_size':56},
                {'color':GREEN,'font_size':48},
                {'color':WHITE,'font_size':36}
            ]
        )
    ):
        '''Constructor for the mind-map class.

        Parameters:
            map: mind-map data
            buff: padding between node content and node border
            direction: node layout direction
            level_spacing: spacing between layers
            node_spacing: spacing between nodes
            node_style: node style
        '''
        self.node_style = node_style
        self.direction = direction
        super().__init__(
            layout_method = TidyTreeLayout(
                root = generate_tree(
                    Map = map,
                    node_style = node_style,
                    buff = buff
                ),
                **LayoutConfig(
                    direction = direction,
                    node_spacing = node_spacing,
                    level_spacing = level_spacing
                ).mindmap
            )
        )
    
    def _set_connectors(self):
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = node.get_connector(
                LayoutType.MindMap,
                direction = self.direction,
                **self._get_connector_style(level = len(node.ID))
            ) if node.parent is not None else None

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject = node.vmobject,
                surr_rect = node.surr_rect,
                connector = node.connector,
                text = node.text
            )

class TimeLine(AbstractMap):
    """
    Timeline: data format is the same as :class:`MindMap`.

    Parameters:
        map: timeline data
        buff: padding between node content and node border
        sides: node layout direction; growth direction of subtrees rooted at
            second-level nodes
        level_spacing: spacing between layers
        node_spacing: spacing between nodes
        node_style: node style
    """
    def __init__(
        self,
        map:Dict = {},
        buff:float = 0.2,
        sides = (UP,DOWN),
        level_spacing = 1.0,
        node_spacing = 0.5,
        node_style :NodeStyle = NodeStyle(
            node_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            line_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            text_style = [
                {'color':RED,'font_size':64},
                {'color':YELLOW,'font_size':56},
                {'color':GREEN,'font_size':48},
                {'color':WHITE,'font_size':36}
            ]
        )
    ):
        self.node_style = node_style
        super().__init__(
            layout_method = TimeLineLayout(
                root = generate_tree(
                    Map = map,
                    node_style = node_style,
                    buff = buff
                ),
                **LayoutConfig(
                    node_spacing = node_spacing,
                    level_spacing = level_spacing,
                    sides = sides
                ).timeline
            )
        )

    def _set_connectors(self):
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = node.get_connector(
                LayoutType.TimeLine,
                direction = RIGHT,
                **self._get_connector_style(level = len(node.ID))
            ) if node.parent is not None else None

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject = node.vmobject,
                surr_rect = node.surr_rect,
                connector = node.connector,
                text = node.text
            )

class StandardMap(AbstractMap):
    """
    Two-sided mind map: data format is the same as :class:`MindMap`.

    Parameters:
        map: mind-map data
        buff: padding between node content and node border
        direction: layout direction
        level_spacing: spacing between layers
        node_spacing: spacing between nodes
        node_style: node style
    """
    def __init__(
        self,
        map:Dict = {},
        buff:float = 0.2,
        direction = RIGHT,
        level_spacing = 1.0,
        node_spacing = 0.5,
        node_style :NodeStyle = NodeStyle(
            node_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            line_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            text_style = [
                {'color':RED,'font_size':64},
                {'color':YELLOW,'font_size':56},
                {'color':GREEN,'font_size':48},
                {'color':WHITE,'font_size':36}
            ]
        )
    ):
        self.node_style = node_style
        super().__init__(
            layout_method = StandardLayout(
                root = generate_tree(
                    Map = map,
                    node_style = node_style,
                    buff = buff
                ),
                **LayoutConfig(
                    direction = direction,
                    node_spacing = node_spacing,
                    level_spacing = level_spacing,
                ).mindmap
            )
        )

    def _set_connectors(self):
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = node.get_connector(
                LayoutType.Standard,
                direction = RIGHT,
                **self._get_connector_style(level = len(node.ID))
            ) if node.parent is not None else None

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject = node.vmobject,
                surr_rect = node.surr_rect,
                connector = node.connector,
                text = node.text
            )

class CatalogMap(AbstractMap):
    """
    Catalog / organisation-chart: data format is the same as :class:`MindMap`,
    layout direction is downwards.

    Parameters:
        map: catalog data
        buff: padding between node content and node border
        level_spacing: spacing between layers
        node_spacing: spacing between nodes
        node_style: node style
    """
    def __init__(
        self,
        map:Dict = {},
        buff:float = 0.2,
        level_spacing = 1.0,
        node_spacing = 0.5,
        node_style :NodeStyle = NodeStyle(
            node_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            line_style = [
                {'color':WHITE,'stroke_width':8},
                {'color':WHITE,'stroke_width':6},
                {'color':WHITE,'stroke_width':4}
            ],
            text_style = [
                {'color':RED,'font_size':64},
                {'color':YELLOW,'font_size':56},
                {'color':GREEN,'font_size':48},
                {'color':WHITE,'font_size':36}
            ]
        )
    ):
        self.node_style = node_style
        super().__init__(
            layout_method = CatalogLayout(
                root = generate_tree(
                    Map = map,
                    node_style = node_style,
                    buff = buff
                ),
                **LayoutConfig(
                    node_spacing = node_spacing,
                    level_spacing = level_spacing,
                ).catalog
            )
        )

    def _set_connectors(self):
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = node.get_connector(
                LayoutType.Catalog,
                direction = RIGHT,
                **self._get_connector_style(level = len(node.ID))
            ) if node.parent is not None else None

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject = node.vmobject,
                surr_rect = node.surr_rect,
                connector = node.connector,
                text = node.text
            )
