"""Timeline 布局算法 - Python 实现"""
__all__ = [
    'TimeLineLayout',
]

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable,Tuple
from .layout import Layout
from .layout_config import LayoutDirection

@dataclass
class TimelineNode:
    """
    时间轴布局节点

    输入属性（必需）：
        width, height: 节点尺寸
        children: 子节点列表
        side_dir: 生长方向（二级节点为根的子树向上或向下）

    输出属性（算法填充）：
        x, y: 节点在画布中的左上角坐标
    """
    node: Any = None
    width: float = 0.0
    height: float = 0.0
    children: List["TimelineNode"] = field(default_factory=list)
    side_dir: LayoutDirection = None

    # 布局结果坐标
    x: float = 0.0
    y: float = 0.0

    # 内部运行时属性（无需用户设置）
    _is_root: bool = False
    _parent: Optional["TimelineNode"] = None
    _layer_index: int = 0         # 层级深度（根为0）
    _index: int = 0               # 在兄弟中的索引

    @classmethod
    def from_node(cls, node) -> 'TimelineNode':
        """从原始节点创建包装树"""
        tl = cls()
        tl.node = node
        # 复制尺寸
        tl.width = float(getattr(node, 'width', 0))
        tl.height = float(getattr(node, 'height', 0))
        # 递归创建子节点
        children = getattr(node, 'children', [])
        tl.children = [cls.from_node(child) for child in children]
        return tl

def walk(
    node: TimelineNode,
    parent: Optional[TimelineNode],
    before_callback: Optional[Callable],
    after_callback: Optional[Callable],
    is_root: bool = False,
    layer_index: int = 0,
    index: int = 0
):
    """
    树遍历工具函数

    支持先序回调（before_callback）和后序回调（after_callback）
    before_callback 返回 True 时跳过该节点的子节点遍历
    """
    # 先序回调
    if before_callback:
        result = before_callback(node, parent, is_root, layer_index, index)
        if result is True:
            return

    # 遍历子节点
    if node.children:
        for i, child in enumerate(node.children):
            walk(child, node, before_callback, after_callback,False, layer_index + 1, i)

    # 后序回调
    if after_callback:
        after_callback(node, parent, is_root, layer_index, index)

class TimeLineLayout(Layout):
    """Timeline 布局引擎"""
    def __init__(
        self,
        root: Any,
        sides: Tuple[LayoutDirection] = (
            LayoutDirection.TopToBottom,
            LayoutDirection.BottomToTop
        ),
        level_spacing: float = 0.5,
        node_spacing: float = 0.5,
    ):
        self.root = TimelineNode.from_node(root)
        self.level_spacing = level_spacing
        self.node_spacing = node_spacing
        self.sides = sides
        self.is_two_sides = (len(sides) == 2)

    # ==================== 对外接口 ====================
    def layout(self) -> Any:
        """执行三阶段布局算法"""
        self._compute_base()
        self._compute_coords()
        self._adjust()
        self._apply_coords(self.root)
        return self.root.node

    # ==================== 阶段1：基础值计算 ====================
    def _compute_base(self):
        """先序遍历：创建节点、计算根节点位置、计算二级节点的 top 值"""
        def before_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ) -> bool:
            node._parent = parent
            node._layer_index = layer_index
            node._index = index

            if is_root:
                node._is_root = True
            else:
                # 非根节点,时间轴交替显示
                if self.is_two_sides:
                    # 三级及以下节点以上级为准
                    if parent and parent.side_dir and not parent._is_root:
                        node.side_dir = parent.side_dir
                    else:
                        # 节点生长方向：二级节点交替
                        node.side_dir = self.sides[index % 2]
                else:
                    node.side_dir = self.sides[0]

                # 二级节点（根的直接子节点）与根节点垂直居中对齐
                if parent and parent._is_root:
                    node.y = parent.y + (parent.height - node.height) / 2
            return False

        walk(self.root, None, before_callback, None, True, 0)

    # ==================== 阶段2：精确坐标计算 ====================
    def _compute_coords(self):
        """先序遍历：计算节点的 left(x)、top(y)"""
        def before_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ) -> bool:
            if not node.children:
                return False

            level_spacing = self.level_spacing
            node_spacing = self.node_spacing

            if is_root:
                # 根节点的子节点是和根节点同一水平线排列
                left = node.x + node.width
                total_left = left + level_spacing
                for cur in node.children:
                    cur.x = total_left
                    total_left += cur.width + level_spacing
            else:
                total_top = node.y + node.height + node_spacing
                for cur in node.children:
                    cur.x = node.x + node.width * 0.5
                    cur.y = total_top
                    total_top += (cur.height + node_spacing)
            return False

        walk(self.root, None, before_callback, None, True, 0)

    # ==================== 阶段3：碰撞调整 ====================
    def _adjust(self):
        """先序+后序遍历：调整节点 left、top"""
        def before_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ) -> bool:
            if node._is_root:
                self._update_brothers_left(node)

            length = len(node.children)
            if parent and not parent._is_root and length > 0:
                node_spacing = self.node_spacing
                total_height = sum(item.height for item in node.children) + length * node_spacing
                self._update_brothers_top(node, total_height)
            return False

        def after_callback(
            node: TimelineNode,
            parent: Optional[TimelineNode],
            is_root: bool,
            layer_index: int,
            index: int
        ):
            # 特殊处理：向上生长的分支镜像翻转
            if (
                parent and
                parent._is_root and
                node.side_dir == LayoutDirection.BottomToTop and
                node.children
            ):
                # 遍历二级节点的子节点，整体镜像翻转到父节点上方
                for item in node.children:
                    total_height = self._get_node_area_height(item)
                    _top = item.y
                    item.y = node.y - (item.y - node.y) - total_height + node.height
                    self._update_children(item.children, "y", item.y - _top)

        walk(self.root, None, before_callback, after_callback, True, 0)

    # ==================== 碰撞调整核心算法 ====================
    def _update_brothers_left(self, node: TimelineNode):
        """
        调整兄弟节点的 left（x 坐标）

        逻辑：遍历根节点的子节点（二级节点），如果某个节点的子树
        实际占用的宽度大于节点自身宽度，则其后面的所有兄弟节点
        需要向右平移，避免重叠。
        """
        children_list = node.children
        total_add_width = 0.0

        for item in children_list:
            item.x += total_add_width
            if item.children:
                self._update_children(item.children, "x", total_add_width)

            bounds = self._get_node_boundaries(item, "h")
            area_width = bounds["right"] - bounds["left"]
            difference = area_width - item.width
            if difference > 0:
                total_add_width += difference

    def _update_brothers_top(self, node: TimelineNode, add_height: float):
        """
        调整兄弟节点的 top（y 坐标）

        逻辑：当前节点的子树很高，导致其在父节点子节点列表中后面的
        兄弟节点需要向下平移。然后递归向上传播到父链。
        """
        if node._parent and not node._parent._is_root:
            children_list = node._parent.children
            try:
                idx = children_list.index(node)
            except ValueError:
                return

            for _index, item in enumerate(children_list):
                _offset = 0.0
                # 下面的节点往下移
                if _index > idx:
                    _offset = add_height
                item.y += _offset
                # 同步更新子节点的位置
                if item.children:
                    self._update_children(item.children, "y", _offset)

            # 更新父节点的位置
            self._update_brothers_top(node._parent, add_height)

    # ==================== 辅助工具方法 ====================
    def _get_node_act_children_length(self, node: TimelineNode) -> int:
        """获取节点实际存在几个子节点"""
        return len(node.children)

    def _get_node_area_height(self, node: TimelineNode) -> float:
        """递归计算节点的区域高度"""
        total_height = 0.0

        def loop(n: TimelineNode):
            nonlocal total_height
            total_height += (n.height + self.node_spacing)
            if n.children:
                for item in n.children:
                    loop(item)

        loop(node)
        return total_height

    def _get_node_boundaries(self, node: TimelineNode, dir: str) -> Dict[str, float]:
        """获取节点的边界值"""
        def walk_tree(root: TimelineNode):
            _left = float("inf")
            _right = float("-inf")
            _top = float("inf")
            _bottom = float("-inf")

            if root.children:
                for child in root.children:
                    bounds = walk_tree(child)
                    _left = min(_left, bounds["left"])
                    _right = max(_right, bounds["right"])
                    _top = min(_top, bounds["top"])
                    _bottom = max(_bottom, bounds["bottom"])

            cur = {
                "left": root.x,
                "right": root.x + root.width,
                "top": root.y,
                "bottom": root.y + root.height
            }
            return {
                "left": min(cur["left"], _left),
                "right": max(cur["right"], _right),
                "top": min(cur["top"], _top),
                "bottom": max(cur["bottom"], _bottom)
            }

        return walk_tree(node)

    def _update_children(self, children: List[TimelineNode], prop: str, offset: float):
        """更新子节点属性"""
        for item in children:
            current = getattr(item, prop)
            setattr(item, prop, current + offset)
            if item.children:
                self._update_children(item.children, prop, offset)

    # ==================== 坐标回写 ====================
    def _apply_coords(self, node: TimelineNode):
        """将计算好的坐标应用到原始节点"""
        if node.node:
            node.node.x = node.x + node.width / 2
            node.node.y = - node.y - node.height / 2
            node.node.side = node.side_dir
            node.node.level = node._layer_index
        for child in node.children:
            self._apply_coords(child)