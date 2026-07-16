__all__ = [
    'LayoutAnimation',
    'RemoveNode',
    'InsertNode',
    'ScaleNode',
    'AlterNode',
]
from typing import List,Dict

from manim.scene.scene import Scene
from manim.mobject.types.image_mobject import ImageMobject
from manim.mobject.mobject import Group
from manim.mobject.types.vectorized_mobject import VMobject
from manim.mobject.text.tex_mobject import Tex,MathTex
from manim.mobject.geometry.polygram import Rectangle
from manim.animation.creation import Animation,Create,Write
from manim.animation.composition import AnimationGroup
from manim.animation.fading import FadeIn,FadeOut
from manim.utils.color import *
from manim.constants import *
import numpy as np

from ..algorithms import LayoutFactory,LayoutType,LayoutConfig
from ..nodes import Node,bfs_walker,NodeSate,NodeStyle

def fadeout_of_subtrees(nodes: List[Node] = None) -> FadeOut:
    '''FadeOut指定节点及其子树'''
    mobjs = []
    for node in nodes:
        for node_ in bfs_walker(node):
            node_.x = node_.y = node_.level = 0
            mobjs.extend([*node_.get_node_and_line_without_updater()])
            
            if node_.node_state == NodeSate.REMOVE:
                node_.parent = None
            node_.node_state = NodeSate.INSERT
    return FadeOut(*mobjs)

def animate_of_create(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles:Dict,
    node_styles:Dict,
    layout_type:LayoutType
) -> List[Animation]:
    '''创建节点动画'''
    anims = []
    node.set_connector(layout_type,direction,**line_styles)
    if isinstance(node.vmobject,ImageMobject):
        AnimateClass = FadeIn
    elif isinstance(node.vmobject,(Tex,MathTex)):
        AnimateClass = Write
    else:
        AnimateClass = Create
    anims.extend(
        [
            AnimateClass(node.vmobject.move_to(pos)),
            Create(
                node.surr_rect.become(
                    Rectangle(
                        height = node.height,
                        width = node.width,
                        **node_styles
                    ).move_to(pos)
                )
            )
        ]
    )
    if hasattr(node,'connector'):
        anims.append(Create(node.connector))
    node.node_state = NodeSate.DISPLAY
    return anims

def animate_of_display(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles:Dict,
    node_styles:Dict,
    layout_type:LayoutType,
    change_dir:bool,
    change_layout:bool
) -> List[Animation]:
    '''已经显示在scene中的节点,更新位置和样式的动画'''
    anims =[
        node.vmobject.animate.move_to(pos),
        node.surr_rect.animate.become(
            Rectangle(
                height = node.height,
                width = node.width,
                **node_styles
            ).move_to(pos)
        )
    ]
    node.change_connector(change_dir,change_layout,layout_type,direction,**line_styles)
    return anims

def animate_of_scale(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles:Dict,
    node_styles:Dict,
    layout_type:LayoutType,
    change_dir:bool,
    change_layout:bool
) -> List[Animation]:
    '''已经显示在scene中的节点,放大或缩小的动画'''
    anims = [
        node.vmobject.animate.scale(node.scale_factor).move_to(pos),
        node.surr_rect.animate.become(
            Rectangle(
                height = node.height,
                width = node.width,
                **node_styles
            ).move_to(pos)
        )
    ]
    node.change_connector(change_dir,change_layout,layout_type,direction,**line_styles)
    node.node_state = NodeSate.DISPLAY
    return anims

def animate_of_alter(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles:Dict,
    node_styles:Dict,
    layout_type:LayoutType,
    change_dir:bool,
    change_layout:bool
) -> List[Animation]:
    '''已经显示在scene中的节点,更换 vmobject 的动画'''
    anims = [
        node.vmobject.animate.become(
            node.alter_vmobject.move_to(pos)
        ),
        node.surr_rect.animate.become(
            Rectangle(
                height = node.height,
                width = node.width,
                **node_styles
            ).move_to(pos)
        )
    ]
    node.node_state = NodeSate.DISPLAY
    node.change_connector(change_dir,change_layout,layout_type,direction,**line_styles)
    return anims

def animate_of_node(
    node: Node,
    pos: np.ndarray,
    direction: np.ndarray,
    line_styles:Dict,
    node_styles:Dict,
    layout_type:LayoutType,
    change_dir:bool,
    change_layout:bool
) -> List[Animation]:
    '''获取 node 的动画'''
    args = (node,pos,direction,line_styles,node_styles,layout_type)
    match node.node_state:
        case NodeSate.INSERT:
            anims = animate_of_create(*args)
        case NodeSate.DISPLAY:
            anims = animate_of_display(*args,change_dir,change_layout)
        case NodeSate.SCALE:
            anims = animate_of_scale(*args,change_dir,change_layout)
        case NodeSate.ALTER:
            anims = animate_of_alter(*args,change_dir,change_layout)
    return anims

def is_layout_change(root: Node, layout_type: LayoutType) -> bool:
    '''
    判断是否替换了布局算法
    
    Args:
        root (Node): 根节点(初次布局,或已经应用过布局)
        layout_type (LayoutType): 将要采用的布局方法
    Returns (bool):是否更换布局算法
    '''
    origin_layout = getattr(root,'layout_type',None)
    if origin_layout is not None:
        return origin_layout != layout_type
    return False

def is_direction_change(root: Node, direction = RIGHT) -> bool:
    '''
    判断是否更换了布局方向

    Args:
        root (Node): 根节点(初次布局,或已经应用过布局)
        direction: 将要采用的布局方向
    Returns (bool):是否更换布局方向
    '''
    origin_dir = getattr(root,'direction',None)
    if origin_dir is not None:
        return not np.array_equal(origin_dir,direction)
    return False

def animate_of_layout(
    root: Node,
    remove_nodes: List[Node] = None,
    layout_type: LayoutType = LayoutType.MindMap,
    layout_config: LayoutConfig = LayoutConfig(),
    node_style: NodeStyle = NodeStyle(),
) -> List[Animation]:
    """动画的核心方法: 完整的 Layout 布局算法并生成动画"""
    direction = layout_config.direction
    change_dir = is_direction_change(root,direction)
    change_layout = is_layout_change(root,layout_type)
    current_x,current_y,_ = root.vmobject.get_center()
    layout = LayoutFactory.create_layout(layout_type,root,layout_config)
    root = layout.layout()
    setattr(root,'layout_type',layout_type)
    setattr(root,'direction',direction)
    x_offset = current_x - root.x
    y_offset = current_y - root.y
    anims = [fadeout_of_subtrees(remove_nodes)] if remove_nodes else []
        
    for node in bfs_walker(root):
        node.x += x_offset
        node.y += y_offset
        node_styles = node_style.get_node_style(node.level)
        line_styles = node_style.get_line_style(node.level)
        pos = np.array([node.x, node.y, 0])
        anims.extend(
            animate_of_node(
                node,
                pos,
                direction,
                line_styles,
                node_styles,
                layout_type,
                change_dir,
                change_layout
            )
        )
        node.x = node.y = 0
    return anims
    
class AbstractLayoutAnimation(AnimationGroup):
    """布局动画的抽象基类: 收集节点状态并生成完整布局动画"""
    def __init__(
        self,
        scene:Scene,
        root:Node,
        layout_type:LayoutType = LayoutType.MindMap,
        layout_config:LayoutConfig = LayoutConfig(),
        node_style:NodeStyle = NodeStyle(),
        **kwargs
    ):
        '''
        对树的节点执行操作后,再执行完整的 Layout 布局算法并生成动画
        
        Args:
            scene (Scene): 当前场景
            root (Node): 根节点
            layout_type (LayoutType, optional): 布局类型. Defaults to LayoutType.MindMap.
            layout_config (LayoutConfig, optional): 布局参数. Defaults to LayoutConfig().
            node_style (NodeStyle, optional): 布局和节点样式. Defaults to NodeStyle().
        '''
        self.scene = scene  
        self.root = root
        self.layout_type = layout_type
        self.layout_config = layout_config
        self.node_style = node_style
        anims = self.collect_animations()
        super().__init__(*anims,**kwargs)

    def _check_node_state(self) -> List[Node]:
        '''检查各个节点的状态,并返回需要移除的节点'''
        remove_nodes = []
        for node in bfs_walker(self.root):
            if node.vmobject not in self.scene.get_mobject_family_members():
                match node.node_state:
                    case NodeSate.INSERT:
                        pass
                    case NodeSate.DISPLAY:
                        node.node_state = NodeSate.INSERT
                    case NodeSate.REMOVE:
                        raise Exception(f'{node.vmobject} is not on current scene,the animation of remove node is not supported')
                    case NodeSate.SCALE:
                        raise Exception(f'{node.vmobject} is not on current scene,the animation of scale node is not supported')
                    case _:
                        raise Exception(f'{node.vmobject} is not on current scene,the animation of alter node is not supported')
            else:
                match node.node_state:
                    case NodeSate.INSERT:
                        node.node_state = NodeSate.DISPLAY
                    case NodeSate.REMOVE:
                        parent = node.parent
                        if parent is None:
                            remove_nodes.append(node)
                            continue
                        try:
                            idx = parent.children.index(node) # TODO: 优化，匹配到第一个为止,修改 __eq__?
                            if (child_num := len(parent.children)) > 1:
                                if idx == 0:
                                    parent.children[1].neighbor = None
                                elif idx < child_num - 1:
                                    parent.children[idx+1].neighbor = parent.children[idx-1]
                            parent.children.remove(node)
                            node.neighbor = None
                            remove_nodes.append(node)
                        except ValueError:
                            raise ValueError(f"Node {node} is not a child of {parent}")
                    case NodeSate.SCALE | NodeSate.DISPLAY | NodeSate.ALTER:
                        pass
        return remove_nodes

    def collect_animations(self) -> List[Animation]:
        '''收集动画: 子类必须实现'''
        raise NotImplementedError
    
    def get_common_root(self, nodes: List[Node]) -> Node:
        '''获取 nodes 的公共根节点'''
        root = nodes[0].get_root()
        if len(nodes) == 1:
            return root
        if not all(node.get_root() is root for node in nodes[1::]):
            return None
        return root
    
class LayoutAnimation(AbstractLayoutAnimation):
    """通用布局动画: 对整棵树应用布局并播放所有变化动画"""
    def __init__(
        self,
        scene:Scene,
        root:Node,
        layout_type:LayoutType = LayoutType.MindMap,
        layout_config:LayoutConfig = LayoutConfig(),
        node_style:NodeStyle = NodeStyle(),
        **kwargs
    ):
        super().__init__(
            scene,
            root,
            layout_type = layout_type,
            layout_config = layout_config,
            node_style = node_style,
            **kwargs
        )
    
    def collect_animations(self):
        remove_nodes = self._check_node_state()
        return animate_of_layout(
            self.root,
            remove_nodes,
            self.layout_type,
            self.layout_config,
            self.node_style
        )
    
class RemoveNode(LayoutAnimation):
    '''移除以 nodes 为根的树或子树, nodes 可以是一个节点,也可以是一个节点列表'''
    def __init__(
        self,
        scene:Scene,
        nodes:Node | List[Node],
        layout_type:LayoutType = LayoutType.MindMap,
        layout_config:LayoutConfig = LayoutConfig(),
        node_style:NodeStyle = NodeStyle(),
        **kwargs
    ):
        self.is_whole_tree = False
        if isinstance(nodes,Node):
            nodes = (nodes,)
        root = self.get_common_root(nodes)
        if root is None:
            raise Exception('nodes must be in the same tree')
        for node in nodes:
            if (parent:= node.parent) is None:
                self.is_whole_tree = True
                break
            else:
                parent.remove_child(node)
        super().__init__(
            scene,
            root,
            layout_type = layout_type,
            layout_config = layout_config,
            node_style = node_style,
            **kwargs
        )

    def collect_animations(self):
        if self.is_whole_tree:
            tree = self._get_whole_tree()
            if len(tree) == 0:
                raise Exception(f'the root {self.root} is not on current scene')
            return (FadeOut(*tree),)
        else:
            return super().collect_animations()

    def _get_whole_tree(self) -> Group:
        group = Group()
        for node in bfs_walker(self.root):
            if node.vmobject not in self.scene.get_mobject_family_members():
                continue
            node.node_state = NodeSate.INSERT
            group.add(*node.get_node_and_line_without_updater())
        return group

class InsertNode(LayoutAnimation):
    """向思维导图中插入一个或多个子节点"""
    def __init__(
        self,
        scene:Scene,
        father_children:Dict[Node,List[Node]] = None,
        layout_type:LayoutType = LayoutType.MindMap,
        layout_config:LayoutConfig = LayoutConfig(),
        node_style:NodeStyle = NodeStyle(),
        **kwargs
    ):
        '''
        插入子节点(列表)插入到指定父节点下

        参数:
            father_children: 字典,键是父节点,值是子节点列表
        '''
        root = None
        self.father_children = father_children
        super().__init__(
            scene,
            root,
            layout_type = layout_type,
            layout_config = layout_config,
            node_style = node_style,
            **kwargs
        )

    def get_root(self,nodes:List[Node]):
        if len(nodes) == 0:
            raise Exception('father_children is empty')
        root = self.get_common_root(nodes)
        if root is None:
            raise Exception('all fathers must be in the same tree')
        return root

    def collect_animations(self) -> List[Animation]:
        for father,children in self.father_children.items():
            if children:
                for child in children:
                    father.add_child(child)
        self.root = self.get_root(list(self.father_children.keys()))
        return super().collect_animations()
    
class ScaleNode(LayoutAnimation):
    """放缩思维导图中一个或多个节点"""
    def __init__(
        self,
        scene:Scene,
        node_scale:Dict[Node,float] = None,
        layout_type:LayoutType = LayoutType.MindMap,
        layout_config:LayoutConfig = LayoutConfig(),
        node_style:NodeStyle = NodeStyle(),
        **kwargs
    ):
        """
        放大或缩小节点

        参数:
            node_scale: 字典,键是 Node 节点,值是缩放比例值(float)
        """
        for node, scale in node_scale.items():
            node.scale(scale)
        root = self.get_common_root(list(node_scale.keys()))
        super().__init__(
            scene,
            root,
            layout_type = layout_type,
            layout_config = layout_config,
            node_style = node_style,
            **kwargs
        )

class AlterNode(LayoutAnimation):
    """替换思维导图中节点内容"""
    def __init__(
        self,
        scene:Scene,
        node_vmobject:Dict[Node,VMobject] = None,
        layout_type:LayoutType = LayoutType.MindMap,
        layout_config:LayoutConfig = LayoutConfig(),
        node_style:NodeStyle = NodeStyle(),
        **kwargs
    ):
        """
        更换节点的vmobject

        参数:
            node_vmobject: 字典,键是 Node 节点,值是待更换的 VMobject
        """
        for node, scale in node_vmobject.items():
            node.alter_content(scale)
        root = self.get_common_root(list(node_vmobject.keys()))
        super().__init__(
            scene,
            root,
            layout_type = layout_type,
            layout_config = layout_config,
            node_style = node_style,
            **kwargs
        )