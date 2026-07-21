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
    """Wrapper for the components of a mind-map node.

    .. manim:: NodeMobjectDocExample
        :save_last_frame:
        
        from manim import *
        from manim_extensions.mindmap import Node
        from manim_extensions.mindmap.mindmap.base import NodeMobject
        
        class NodeMobjectDocExample(Scene):
            def construct(self):
                node = Node(MathTex("Hello", font_size=36))
                nm = NodeMobject(node.vmobject, node.surr_rect, None, "hello")
                self.add(nm.vmobject, nm.surr_rect)
    """
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
    Recursively traverse *Map* and return the root node of the generated tree.

    ``text``: narration text that can be used for text-to-speech synthesis.
    

    .. manim:: GenerateTreeDocExample
        :save_last_frame:
        
        from manim import *
        from manim_extensions.mindmap.mindmap.base import generate_tree
        
        class GenerateTreeDocExample(Scene):
            def construct(self):
                root = generate_tree({
                    'node': MathTex("Root", font_size=36),
                    'child': [{'node': MathTex("Child", font_size=36)}]
                })
                self.add(root.vmobject, root.surr_rect)
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
        """Generate a node mobject."""
        if isinstance(Mobj,str):
            Mobj = Tex(
                Mobj,
                tex_template = TexTemplateLibrary.ctex,
                **node_style.get_text_style(level = level)
            )
        return Mobj
    
    return _generate_tree(ID=(0,), current_map = Map)

class AbstractMap(Group):
    """Abstract base class for mind maps, timelines, etc.

    .. manim:: AbstractMapDocExample
        :save_last_frame:
        
        from manim import *
        from manim_extensions.mindmap import Node
        from manim_extensions.mindmap.algorithms import Layout
        from manim_extensions.mindmap.mindmap.base import AbstractMap
        
        class AbstractMapDocExample(Scene):
            def construct(self):
                class FixedLayout(Layout):
                    def __init__(self, root):
                        self.root = root
                    def layout(self):
                        return self.root
        
                class DemoMap(AbstractMap):
                    def _set_connectors(self):
                        pass
        
                root = Node(MathTex("Root", font_size=36))
                root.add_child(Node(MathTex("A", font_size=36)))
                self.add(DemoMap(FixedLayout(root)))
    """
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
        """Set connection lines."""
        raise NotImplementedError
        
    def get_node_component(self,ID) -> NodeMobject:
        """Return the full component object of the node with the given ID."""
        return self.node_data_dict.get(ID,None)

    def get_node(self,ID) -> Group:
        """Return the VMobject and surrounding rectangle of the node with the given ID."""
        node = self.node_data_dict.get(ID,None)
        if node is not None:
            return Group(node.vmobject,node.surr_rect)
        return None

    def get_text(self,ID) -> str:
        """Return the narration text of the node with the given ID."""
        node = self.node_data_dict.get(ID,None)
        if node is not None:
            return node.text
        return None
    
    def get_connector(self,ID) -> Line:
        """Return the connector line of the node with the given ID."""
        node = self.node_data_dict.get(ID,None)
        if node is not None:
            return node.connector
        return None
    
    def get_all_mindmap(self) -> Group:
        """Return all node and connector mobjects in the mind map."""
        all_mobjects = Group()
        for node in self.node_data_dict.values():
            if node.connector is not None:
                all_mobjects.add(node.vmobject,node.surr_rect,node.connector)
            else:
                all_mobjects.add(node.vmobject,node.surr_rect)
        return all_mobjects
    
    def bfs_walker(self) -> Generator:
        """Breadth-first traversal."""
        for node in bfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def dfs_walker(self) -> Generator:
        """Depth-first traversal."""
        for node in dfs_walker(self.root):
            yield self.node_data_dict[node.ID]

    def custom_walker(self,id_list: List[tuple]) -> Generator:
        """Custom traversal."""
        for id in id_list:
            yield self.node_data_dict.get(id,None)

    def _get_origin_node(self,ID) -> Node:
        """Find the node with the given ID in the original tree."""
        for node in dfs_walker(self.root):
            if node.ID == ID:
                return node
        return None
    
    def _get_connector_style(self,level:int) -> dict:
        """Return the line style for the given level."""
        return self.node_style.get_line_style(level=level)

    def get_children(self,ID) -> Group:
        '''Return the child nodes of the node with the given ID.'''
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_children_mobjects()
    
    def get_submindmap(self,ID) -> Group:
        '''Return the subtree rooted at the node with the given ID.'''
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
        '''Return the descendants of the node with the given ID.'''
        node = self._get_origin_node(ID)
        if node is None:
            return Group()
        return node.get_descendants_mobjects()