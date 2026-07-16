__all__ = [
    'StandardLayout',
]
from typing import List,Any
from collections import deque
from .alg_tidy_tree import TidyTreeLayout
from .layout_config import LayoutDirection
from .layout import Layout

class TreeNode:
    """StandardLayout 内部使用的树节点包装类"""
    __slots__ = ('height','width','children','parent','x','y','level','is_flip')
    def __init__(
        self,
        height:float = 0,
        width:float = 0,
    ):
        self.width = width
        self.height = height
        self.x:float = 0
        self.y:float = 0
        self.level:int = 0
        self.is_flip:bool = False
        self.children: List['TreeNode'] = []
        self.parent:'TreeNode' = None

    def add_child(self, child: 'TreeNode'):
        """添加子节点并设置父子关系"""
        self.children.append(child)
        child.parent = self

def copy_node(node:Any) -> 'TreeNode':
    if node is None:
        return None
    root = TreeNode(node.height, node.width)
    for child in node.children:
        root.add_child(copy_node(child))
    return root

def split_integer(n:int):
    if (n & 1):
        k = (n - 1) // 2
        return k + 1,k
    k = n // 2
    return k,k

def sync_copy_bfs(src: TreeNode, dst: Any):
    """
    同步递归遍历，将 src 的数据复制到 dst。
    
    Args:
        src: 源树（数据提供者）
        dst: 目标树（数据接收者）
    """
    queue = deque([(src, dst)])
    
    while queue:
        s_node, d_node = queue.popleft()
        
        if s_node is None and d_node is None:
            continue
        if s_node is None or d_node is None:
            raise ValueError("结构不一致")
        if len(s_node.children) != len(d_node.children):
            raise ValueError("子节点数量不一致")
        
        # 复制数据
        d_node.x = s_node.x
        d_node.y = s_node.y
        d_node.level = s_node.level
        d_node.is_flip = s_node.is_flip
        
        # 同步入队
        for s_child, d_child in zip(s_node.children, d_node.children):
            queue.append((s_child, d_child))

class StandardLayout(Layout):
    """两侧布局的思维导图布局算法:将子节点分成左右(或上下)两侧分别布局"""
    def __init__(
        self,
        root:Any,
        direction: LayoutDirection = LayoutDirection.LeftToRight,
        node_spacing: float = 0.5,
        level_spacing: float = 0.5
    ):
        self.root = root
        self.direction = direction
        self.flip_direction = self._flip_direction(direction)
        self.node_spacing = node_spacing
        self.level_spacing = level_spacing

    def _flip_direction(self, direction: LayoutDirection) -> LayoutDirection:
        """返回给定方向的反方向"""
        match direction:
            case LayoutDirection.LeftToRight:
                return LayoutDirection.RightToLeft
            case LayoutDirection.RightToLeft:
                return LayoutDirection.LeftToRight
            case LayoutDirection.TopToBottom:
                return LayoutDirection.BottomToTop
            case LayoutDirection.BottomToTop:
                return LayoutDirection.TopToBottom
            
    def _split(self):
        """将根节点的子节点分成左右(或上下)两部分"""
        self.left = TreeNode(self.root.height, self.root.width)
        if (number := len(self.root.children)) > 0:
            m,n = split_integer(number)
            children = [
                copy_node(child) for child in self.root.children
            ]
            for child in children[0:m]:
                self.left.add_child(child)
            self.right = None
            if n > 0:
                self.right = TreeNode(self.root.height, self.root.width)
                for child in children[m::]:
                    self.right.add_child(child)

    def layout(self):
        """执行两侧布局计算并返回原始根节点"""
        self._split()
        self.left = TidyTreeLayout(
            self.left,
            self.direction,
            self.node_spacing,
            self.level_spacing
        ).layout()
        if self.right is not None:
            self.right = TidyTreeLayout(
                self.right,
                self.flip_direction,
                self.node_spacing,
                self.level_spacing
            ).layout()
            x = self.left.x - self.right.x
            y = self.left.y - self.right.y
            self._offset(self.right, x, y)
            self._merge()
        sync_copy_bfs(self.left, self.root)
        return self.root
    
    def _offset(self,node:Any, x:float, y:float):
        """平移右侧(或下侧)子树并标记为翻转"""
        node.x += x
        node.y += y
        node.is_flip = True
        for child in node.children:
            self._offset(child,x,y)

    def _merge(self):
        """将右侧(或下侧)子树合并到左侧树中"""
        for child in self.right.children:
            self.left.add_child(child) 