__all__ = [
    'NodeMobject',
    'generate_tree',
    'AbstractMap'
]
from typing import Generator,List,Dict

import numpy as np
from manim.constants import *
from manim.utils.tex_templates import TexTemplateLibrary
from manim.utils.color import *
from manim.mobject.mobject import Group,Mobject
from manim.mobject.geometry.line import Line
from manim.mobject.geometry.polygram import Rectangle
from manim.mobject.types.vectorized_mobject import VMobject
from manim.mobject.text.tex_mobject import Tex

from ..nodes import Node,NodeStyle,bfs_walker,dfs_walker
from ..algorithms import Layout

class NodeMobject:
    """思维导图节点的组成部分包装类"""
    __slots__ = ['vmobject','surr_rect','connector','text']
    def __init__(
        self,
        vmobject:VMobject,
        surr_rect:Rectangle,
        connector:Line,
        text:str
    ):
        self.vmobject = vmobject
        self.surr_rect = surr_rect
        self.connector = connector
        self.text = text

def generate_tree(
    Map = None,
    node_style :NodeStyle = NodeStyle(),
    buff:float = 0.2
) -> Node:
    """
    递归的遍历Map: 生成树的根节点
    text: 为讲解文字，可用于合成语言
    """
    def _generate_tree(ID=(0,), current_map:Dict = None) -> Node:
        level = len(ID)
        mobj = _generate_node(Mobj=current_map['node'], level=level)
        current_node = Node(mobj, buff, **node_style.get_node_style(level=level))
        current_node.ID = ID
        current_node.text = current_map.get('text', None)

        if 'child' in current_map:
            for index, child_map in enumerate(current_map['child']):
                child_node = _generate_tree(ID = (*ID, index), current_map = child_map)
                current_node.add_child(child_node)
                
        return current_node

    def _generate_node(Mobj,level = 1) -> Mobject:
        """生成节点"""
        if isinstance(Mobj,str):
            Mobj = Tex(
                Mobj,
                tex_template = TexTemplateLibrary.ctex,
                **node_style.get_text_style(level = level)
            )
        return Mobj
    
    return _generate_tree(ID=(0,), current_map = Map)

class AbstractMap(Group):
    """抽象基类：思维导图、时序图等"""
    def __init__(
        self,
        layout_method:Layout = Layout()
    ):
        super().__init__()
        self.node_data_dict = {}
        self.root = layout_method.layout()
        self._set_node_position(self.root)
        self._set_connectors()
        self.add(*self.get_all_mindmap())
        self.move_to(ORIGIN)
    
    def _set_node_position(self,node:Node):
        pos = np.array([node.x, node.y, 0])
        node.vmobject.move_to(pos)
        node.surr_rect.move_to(pos)
        for child in node.children:
            self._set_node_position(child)
    
    def _set_connectors(self):
        """设置连接线"""
        raise NotImplementedError
        
    def get_node_component(self,ID) -> NodeMobject:
        """获取指定 ID 节点的完整组成对象"""
        return self.node_data_dict.get(ID,None)

    def get_node(self,ID) -> Group:
        """获取指定 ID 节点的 VMobject 和边框"""
        node = self.node_data_dict.get(ID,None)
        if node is not None:
            return Group(node.vmobject,node.surr_rect)
        return None

    def get_text(self,ID) -> str:
        """获取指定 ID 节点的讲解文本"""
        node = self.node_data_dict.get(ID,None)
        if node is not None:
            return node.text
        return None
    
    def get_connector(self,ID) -> Line:
        """获取指定 ID 节点的连接线"""
        node = self.node_data_dict.get(ID,None)
        if node is not None:
            return node.connector
        return None
    
    def get_all_mindmap(self) -> Group:
        """获取思维导图中所有节点和连线对象"""
        all_mobjects = Group()
        for node in self.node_data_dict.values():
            if node.connector is not None:
                all_mobjects.add(node.vmobject,node.surr_rect,node.connector)
            else:
                all_mobjects.add(node.vmobject,node.surr_rect)
        return all_mobjects
    
    def bfs_walker(self) -> Generator:
        """广度优先遍历"""
        for node in bfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def dfs_walker(self) -> Generator:
        """深度优先遍历"""
        for node in dfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def custom_walker(self,id_list: List[tuple]) -> Generator:
        """自定义遍历"""
        for id in id_list:
            yield self.node_data_dict.get(id,None)

    def _get_origin_node(self,ID) -> Node:
        """根据 ID 在原始树中查找节点"""
        for node in dfs_walker(self.root):
            if node.ID == ID:
                return node
        return None
    
    def _get_connector_style(self,level:int) -> dict:
        """获取指定层级的连线样式"""
        return self.node_style.get_line_style(level=level)

    def get_children(self,ID) -> Group:
        '''获取节点的子节点'''
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_children_mobjects()
    
    def get_submindmap(self,ID) -> Group:
        '''获取以节点 ID 为根的子树'''
        node = self._get_origin_node(ID)
        mondmap = Group()
        if node is None:
            return mondmap
        for node_ in dfs_walker(node):
            if node_.connector is not None and len(node_.ID) > len(ID):
                mondmap.add(node_.vmobject,node_.surr_rect,node_.connector)
            else:
                mondmap.add(node_.vmobject,node_.surr_rect)
        return mondmap

    def get_descendants(self,ID) -> Group:
        '''获取节点的后代'''
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_descendants_mobjects()