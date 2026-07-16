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
    思维导图类: 解析如下格式的思维导图数据,并生成对应的思维导图对象

    mindmap = {
        'node':r'球体积',
        'text':'用于TTS讲解的文本',
        'child':[
            {
                'node':r'公元前3世纪',#或者为VMobject、Mobject对象
                'child':[
                    {
                        'node':r'阿基米德平衡法',
                    }
                ]
            },
            {
                'node':r'公元3世纪',
                'child':[
                    {
                        'node':r'《九章算术》',
                    },
                    {
                        'node':r'刘徽：牟合方盖',
                        'child':[
                            {
                                'node':r'球与牟合方盖的关系',
                            },
                            {
                                'node':r'牟合方盖体积？',
                            }
                        ]
                    }
                ]
            },
            {
                'node':r'公元5世纪',
                'child':[
                    {
                        'node':r'祖暅：开立圆术',
                    }
                ]
            },
            {
                'node':r'公元17世纪',
                'child':[
                    {
                        'node':r'开普勒',
                    },
                    {
                        'node':r'卡瓦列里原理',
                    }
                ]
            },
            {
                'node':r'公元18世纪',
                'child':[
                    {
                        'node':r'松永良弼：会玉术',
                    }
                ]
            }
        ]
    }

    mind = MindMap(mindmap)
    mind.scale_to_fit_width(12)
    self.play(
        FadeIn(mind)
    )
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
        '''
        思维导图类构造函数
        
        参数说明:
            map: 思维导图数据
            buff: 节点内容和节点边框间距
            direction: 节点布局方向
            level_spacing: 层间距
            node_spacing: 节点间距
            node_style: 节点样式
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
        """设置连接线"""
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
    时序图:数据格式与 MindMap 相同
    
    参数说明:
        map: 时序图数据
        buff: 节点内容和节点边框间距
        sides: 节点布局方向,以二级节点为根的子树发延伸方向
        level_spacing: 层间距
        node_spacing: 节点间距
        node_style: 节点样式
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
        """设置连接线"""
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
    两侧布局的思维导图:数据格式与 MindMap 相同
    
    参数说明:
        map: 导图数据
        buff: 节点内容和节点边框间距
        direction: 布局方向
        level_spacing: 层间距
        node_spacing: 节点间距
        node_style: 节点样式
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
        """设置连接线"""
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
    目录组织结构图:数据格式与 MindMap 相同,布局方向向下
    
    参数说明:
        map: 目录数据
        buff: 节点内容和节点边框间距
        level_spacing: 层间距
        node_spacing: 节点间距
        node_style: 节点样式
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
        """设置连接线"""
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