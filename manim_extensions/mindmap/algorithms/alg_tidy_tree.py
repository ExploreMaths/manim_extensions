"""
Non-layered Tidy Tree Layout Algorithm (Python Implementation)
用于计算树形结构的节点位置布局

算法参考来源《Improving Walker's Algorithm to Run in Linear Time》
"""
__all__ = [
    'TidyTreeLayout'
]
from dataclasses import dataclass, field
from typing import List, Optional, Any
from .layout_config import LayoutDirection
from .layout import Layout

@dataclass
class WrappedTree:
    """包装树节点，用于布局计算"""
    # 原始节点引用
    node: Any = None
    # 基本属性
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
    level: int = 0 # 节点层级
    # 子节点
    children: List['WrappedTree'] = field(default_factory=list)
    child_number: int = 0

    # === 核心布局属性 ===
    prelim: float = 0.0  # 节点相对于父节点的初步位置，不考虑任何重叠修正
    mod: float = 0.0     # 以当前节点为根的整棵子树需要额外平移的量
    shift: float = 0.0   # 记录需要均匀分摊到后续兄弟子树的间距份额
    change: float = 0.0  # 在分摊链的末端节点做一次性修正，消除累积误差

    # === 子树轮廓线追踪,用于不重叠检测 ===
    extreme_left: Optional['WrappedTree'] = None  # 最左端点节点
    extreme_right: Optional['WrappedTree'] = None  # 最右端点节点
    mod_sum_extreme_left: float = 0.0   # 从最左端点到根路径上所有 mod 的累加和
    mod_sum_extreme_right: float = 0.0  # 从最右端点到根路径上所有 mod 的累加和

    # 线程,用于轮廓遍历: 两个子树的高度不同时,矮树耗尽时,链接到临近子树的轮廓
    thread_left: Optional['WrappedTree'] = None
    thread_right: Optional['WrappedTree'] = None

    @classmethod
    def from_node(cls, node, is_horizontal: bool,level:int = 0) -> 'WrappedTree':
        """从原始节点创建包装树"""
        wt = cls()
        wt.node = node
        wt.level = level
        level += 1
        # 复制尺寸
        if is_horizontal:
            wt.width = getattr(node, 'height', 0)
            wt.height = getattr(node, 'width', 0)
            wt.x = getattr(node, 'x', 0)
        else:
            wt.width = getattr(node, 'width', 0)
            wt.height = getattr(node, 'height', 0)
            wt.y = getattr(node, 'y', 0)

        # 递归创建子节点
        children = getattr(node, 'children', [])
        wt.children = [cls.from_node(child, is_horizontal, level) for child in children]
        wt.child_number = len(wt.children)
        return wt

@dataclass
class IYLNode:
    """
    separate 函数中的最低轮廓线: 
    为避免第 i 个子树与前面 i-1 个子树的逐一比较,通过链表单调裁剪,提升效率!
    被 IYLNode 淘汰的子树，已被更高且更靠右的中间子树完全遮挡，当前子树永远不可能先撞到它们
    """
    low: float                       # 子树最右轮廓低端节点,在正交方向上的高度
    index: int                       # 子树在兄弟节点中的索引
    nxt: Optional['IYLNode'] = None  # 指向链表中下一个 IYL 节点（该节点的 low 值严格更高）

def move_right(node, move: float, is_horizontal: bool):
    """向右（或向下）移动节点及其所有子节点"""
    if is_horizontal:
        node.y += move
    else:
        node.x += move
    for child in node.children:
        move_right(child, move, is_horizontal)

def get_min(node, is_horizontal: bool) -> float:
    """获取节点树中最小坐标值"""
    res = node.y if is_horizontal else node.x
    for child in node.children:
        res = min(get_min(child, is_horizontal), res)
    return res

def normalize(node, is_horizontal: bool):
    """归一化坐标: 将最小坐标对齐到0,确保布局从原点开始"""
    min_val = get_min(node, is_horizontal)
    move_right(node, -min_val, is_horizontal)

def convert_back(converted: WrappedTree, root, is_horizontal: bool):
    """将计算结果转换回原始节点：将 WrappedTree.x 写回原始节点的 x 或 y(根据方向)"""
    if is_horizontal:
        root.y = converted.x
    else:
        root.x = converted.x

    for i, child in enumerate(converted.children):
        if i < len(root.children):
            convert_back(child, root.children[i], is_horizontal)

def layer(node, direction,level_spacing):
    """设置层级（深度）坐标"""
    if (parent := node.parent) is not None:
        node.level = parent.level + 1
        if direction == LayoutDirection.LeftToRight:
            node.x = parent.x + (parent.width + node.width) / 2 + level_spacing
        elif direction == LayoutDirection.RightToLeft:
            node.x = parent.x - (parent.width + node.width) / 2 - level_spacing
        elif direction == LayoutDirection.BottomToTop:
            node.y = parent.y + (parent.height + node.height) / 2 + level_spacing
        else:
            node.y = parent.y - (parent.height + node.height) / 2 - level_spacing

    for child in node.children:
        layer(child, direction,level_spacing)

class TidyTreeLayout(Layout):
    """非分层整洁树布局算法"""
    def __init__(
        self,
        root,
        direction: LayoutDirection = LayoutDirection.LeftToRight,
        node_spacing: float = 0.5,
        level_spacing: float = 0.5
    ):
        self.root = root
        self.direction = direction
        self.is_horizontal = self._is_horizontal(direction)
        self.node_spacing = node_spacing
        self.level_spacing = level_spacing
        self.wt = None

    def _is_horizontal(self,direction):
        return direction in (LayoutDirection.LeftToRight, LayoutDirection.RightToLeft)

    def layout(self):
        """执行布局计算"""
        layer(self.root, self.direction,self.level_spacing)
        self.wt = WrappedTree.from_node(self.root, self.is_horizontal)
        self.first_walk(self.wt)
        self.second_walk(self.wt, 0)
        convert_back(self.wt, self.root, self.is_horizontal)
        normalize(self.root, self.is_horizontal)
        # self.compute_connectors()
        return self.root

    def first_walk(self, t: WrappedTree):
        """
        第一次遍历：
        计算每个节点的 prelim(初步相对位置)和 mod(修饰偏移),检测并消除子树间的重叠
        """
        if t.child_number == 0:
            self.set_extremes(t)
            return

        # 处理第一个子节点
        self.first_walk(t.children[0])
        ih = self.update_iyl(self.bottom(t.children[0].extreme_right), 0, None)

        # 处理其余子节点
        for i in range(1, t.child_number):
            self.first_walk(t.children[i])
            min_val = self.bottom(t.children[i].extreme_right)
            self.separate(t, i, ih)
            ih = self.update_iyl(min_val, i, ih)

        self.position_root(t)
        self.set_extremes(t)

    def set_extremes(self, t: WrappedTree):
        """设置极值节点"""
        if t.child_number == 0:
            t.extreme_left = t
            t.extreme_right = t
            t.mod_sum_extreme_left = 0
            t.mod_sum_extreme_right = 0
        else:
            t.extreme_left = t.children[0].extreme_left
            t.mod_sum_extreme_left = t.children[0].mod_sum_extreme_left
            t.extreme_right = t.children[-1].extreme_right
            t.mod_sum_extreme_right = t.children[-1].mod_sum_extreme_right

    def update_iyl(self, low: float, index: int, ih: Optional[IYLNode]) -> IYLNode:
        """
        更新 IYLNode 链表: 淘汰掉 ih.low 值小于等于 low 的节点
        返回: 新的节点成为表头,并指向剩余链表
        """
        while ih is not None and low >= ih.low:
            ih = ih.nxt
        return IYLNode(low, index, ih)

    def separate(self, t: WrappedTree, i: int, ih: Optional[IYLNode]):
        """
        算法核心: 分离第i个子树与前面子树,确保不重叠

        参数:
            t (WrappedTree): 父节点
            i (int): 当前子树索引
            ih (Optional[IYLNode]): 那些"右轮廓还暴露在外、可能先与第 i 个子树发生碰撞"的前序子树
        """
        sr = t.children[i - 1]   # 当前右轮廓节点，初始为紧邻的左兄弟
        mssr = sr.mod            # 从 t.children[i-1] 到 sr 路径上的 mod 累加和
        cl = t.children[i]       # 当前左轮廓节点，初始为当前子树根节点
        mscl = cl.mod            # 从 t.children[i] 到 cl 路径上的 mod 累加和

        while sr is not None and cl is not None:
            # 跳过已被完全遮挡的前序子树
            if ih is not None and self.bottom(sr) > ih.low:
                # 当前 sr 高度已经超过了该前序子树的轮廓范围，在这个高度上,ih 不可能与当前子树碰撞
                # 跳过该前序子树，继续与下一个更高的前序子树比较
                ih = ih.nxt

            dist = mssr + sr.prelim + self.node_spacing + (sr.width + cl.width)/2 - (mscl + cl.prelim)
            if dist > 0:
                mscl += dist
                si = ih.index if ih is not None else i - 1
                self.move_subtree(t, i, si, dist)

            sy = self.bottom(sr)
            cy = self.bottom(cl)

            if sy <= cy:
                sr = self.next_right_contour(sr)
                if sr is not None:
                    mssr += sr.mod

            if sy >= cy:
                cl = self.next_left_contour(cl)
                if cl is not None:
                    mscl += cl.mod

        if sr is None and cl is not None:
            self.set_left_thread(t, i, cl, mscl)
        elif sr is not None and cl is None:
            self.set_right_thread(t, i, sr, mssr)

    def move_subtree(self, t: WrappedTree, i: int, si: int, dist: float):
        """移动子树"""
        t.children[i].mod += dist
        t.children[i].mod_sum_extreme_left += dist
        t.children[i].mod_sum_extreme_right += dist
        self.distribute_extra(t, i, si, dist)

    def distribute_extra(self, t: WrappedTree, i: int, si: int, dist: float):
        """分配额外间距"""
        if si != i - 1:
            nr = i - si
            t.children[si + 1].shift += dist / nr
            t.children[i].shift -= dist / nr
            t.children[i].change -= dist - dist / nr

    def next_left_contour(self, t: WrappedTree) -> Optional[WrappedTree]:
        """获取下一个左轮廓节点"""
        return t.thread_left if t.child_number == 0 else t.children[0]

    def next_right_contour(self, t: WrappedTree) -> Optional[WrappedTree]:
        """获取下一个右轮廓节点"""
        return t.thread_right if t.child_number == 0 else t.children[-1]

    def bottom(self, t: WrappedTree) -> float:
        """返回节点在正交方向上的高度"""
        if self.is_horizontal:
            return t.height/2 + abs(t.x)
        return abs(t.y) + t.height/2

    def set_left_thread(self, t: WrappedTree, i: int, cl: WrappedTree, modsumcl: float):
        """设置左线程"""
        li = t.children[0].extreme_left
        li.thread_left = cl
        diff = (modsumcl - cl.mod) - t.children[0].mod_sum_extreme_left
        li.mod += diff
        li.prelim -= diff
        t.children[0].extreme_left = t.children[i].extreme_left
        t.children[0].mod_sum_extreme_left = t.children[i].mod_sum_extreme_left

    def set_right_thread(self, t: WrappedTree, i: int, sr: WrappedTree, modsumsr: float):
        """设置右线程"""
        ri = t.children[i].extreme_right
        ri.thread_right = sr
        diff = (modsumsr - sr.mod) - t.children[i].mod_sum_extreme_right
        ri.mod += diff
        ri.prelim -= diff
        t.children[i].extreme_right = t.children[i - 1].extreme_right
        t.children[i].mod_sum_extreme_right = t.children[i - 1].mod_sum_extreme_right

    def position_root(self, t: WrappedTree):
        """放置子树 t 根节点: 将其放置在子节点的正中间"""
        t.prelim = (
            t.children[0].prelim + t.children[0].mod + t.children[-1].mod + t.children[-1].prelim 
        ) / 2

    def second_walk(self, t: WrappedTree, modsum: float):
        """
        第二次遍历：
        将 prelim 和 mod 累加到最终绝对非层级的坐标 x 或 y 上

        参数:
            modsum: 从根到当前路径上所有祖先 mod 值的总和
        """
        modsum += t.mod
        if self.is_horizontal:
            t.x = -t.prelim - modsum
        else:
            t.x = t.prelim + modsum
        self.add_child_spacing(t)

        for child in t.children:
            self.second_walk(child, modsum)

    def add_child_spacing(self, t: WrappedTree):
        """添加子节点间距"""
        d = 0
        modsumdelta = 0
        for child in t.children:
            d += child.shift
            modsumdelta += d + child.change
            child.mod += modsumdelta

    def compute_connectors(self):
        """计算连接器"""
        def compute_node(node:Any):
            parent = node.parent
            match self.direction:
                case LayoutDirection.TopToBottom:
                    xs,ys = parent.x, parent.y - parent.height/2
                    xe,ye = node.x, node.y + node.height/2
                    points = ((xs, ys),(xs, (ys + ye) / 2),(xe, (ys + ye) / 2),(xe, ye))
                case LayoutDirection.BottomToTop:
                    xs,ys = parent.x, parent.y + parent.height/2
                    xe,ye = node.x, node.y - node.height/2
                    points = ((xs, ys),(xs, (ys + ye) / 2),(xe, (ys + ye) / 2),(xe, ye))
                case LayoutDirection.LeftToRight:
                    xs,ys = parent.x + parent.width/2, parent.y
                    xe,ye = node.x - node.width/2, node.y
                    points = ((xs, ys),((xs + xe) / 2, ys),((xs + xe) / 2, ye),(xe, ye))
                case LayoutDirection.RightToLeft:
                    xs,ys = parent.x - parent.width/2, parent.y
                    xe,ye = node.x + node.width/2, node.y
                    points = ((xs, ys),((xs + xe) / 2, ys),((xs + xe) / 2, ye),(xe, ye))
            node.connector_points = points

            for child in node.children:
                compute_node(child)

        for child in self.root.children:
            compute_node(child)