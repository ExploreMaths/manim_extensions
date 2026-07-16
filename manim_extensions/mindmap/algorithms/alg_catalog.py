"""
组织目录布局算法 - Python 实现

布局特点：
- 根节点居中
- 二级节点水平排列在根节点下方
- 三级及以下节点垂直排列在父节点下方（纵向树）
- 自动调整兄弟节点偏移，避免重叠
"""
__all__ = [
    'CatalogLayout'
]
from dataclasses import dataclass, field
from typing import List, Optional, Any, Callable, Tuple
from .layout_config import LayoutDirection
from .layout import Layout

@dataclass
class CatalogNode:
    """
    目录组织图节点

    输入属性：
        width, height: 节点尺寸
        children: 子节点列表

    输出属性（算法填充）：
        left, top: 节点在画布中的左上角坐标
        layer_index: 层级（根为0）
        parent: 父节点引用
        children_area_width: 根节点子节点总宽度（用于水平排列）
    """
    data: Any = None
    width: float = 0.0
    height: float = 0.0
    children: List["CatalogNode"] = field(default_factory=list)

    # 布局结果
    left: float = 0.0
    top: float = 0.0
    layer_index: int = 0
    parent: Optional["CatalogNode"] = None
    children_area_width: float = 0.0

    @classmethod
    def from_data(cls, node: Any) -> "CatalogNode":
        """从原始数据递归创建节点树"""
        org_node = cls()
        org_node.node = node
        org_node.width = getattr(node, 'width', 0)
        org_node.height = getattr(node, 'height', 0)

        children = getattr(node, 'children', [])
        org_node.children = [cls.from_data(child) for child in children]
        return org_node

class CatalogLayout(Layout):
    """目录组织图布局算法"""
    def __init__(
        self,
        root: Any,
        node_spacing: float = 0.5,
        level_spacing: float = 0.5
    ):
        """
        Args:
            root: 根节点
            node_spacing: 根节点到二级节点的垂直距离，同时也是二级节点之间的水平间距
            level_spacing: 三级及以下节点之间的垂直间距
        """
        self.root = CatalogNode.from_data(root)
        self.margin_root_child = node_spacing
        self.margin_vertical = level_spacing

    def _get_margin_x(self, layer_index: int) -> float:
        """水平间距：
            + 根节点的子节点使用 margin_root_child
            + 其他层级使用 margin_vertical
            + 实际只有二级节点用到水平间距
        """
        return self.margin_root_child if layer_index == 1 else self.margin_vertical

    def _get_margin_y(self, layer_index: int) -> float:
        """垂直间距：根节点的子节点使用 margin_root_child（垂直方向），其他层级使用 margin_vertical"""
        return self.margin_root_child if layer_index == 1 else self.margin_vertical

    def _update_children(self, nodes: List[CatalogNode], prop: str, offset: float):
        """递归更新子节点属性（left 或 top）"""
        for node in nodes:
            setattr(node, prop, getattr(node, prop) + offset)
            if node.children:
                self._update_children(node.children, prop, offset)

    def _update_children_pro(self, nodes: List[CatalogNode], props: dict):
        """递归更新子节点多个属性"""
        for node in nodes:
            for k, v in props.items():
                setattr(node, k, getattr(node, k) + v)
            if node.children:
                self._update_children_pro(node.children, props)

    def _walk(
        self,
        node: CatalogNode,
        pre_cb: Optional[Callable] = None,
        post_cb: Optional[Callable] = None,
        layer: int = 0,
        index: int = 0
    ):
        """遍历树，执行前序和后序回调"""
        if pre_cb:
            pre_cb(node, layer, index)
        for i, child in enumerate(node.children):
            child.layer_index = layer + 1
            child.parent = node
            self._walk(child, pre_cb, post_cb, layer + 1, i)
        if post_cb:
            post_cb(node, layer, index)

    def _get_node_boundaries_horizontal(self, node: CatalogNode) -> Tuple[float, float]:
        """获取节点及其所有后代节点的水平边界（min_left, max_right）"""
        left = node.left
        right = node.left + node.width
        for child in node.children:
            cl, cr = self._get_node_boundaries_horizontal(child)
            left = min(left, cl)
            right = max(right, cr)
        return left, right

    def _get_node_area_width(self, node: CatalogNode) -> float:
        """
        递归计算子树的最大宽度（根节点到最右侧叶子的水平跨度）通过递归计算所有路径的总宽度，取最大值。
        注意：这个宽度用于调整兄弟节点的水平偏移。
        """
        min_l, max_r = self._get_node_boundaries_horizontal(node)
        return max_r - min_l

    def _get_node_area_height(self, node: CatalogNode) -> float:
        """递归计算节点子树的总高度（用于垂直调整）"""
        total = node.height
        if node.children:
            margin_y = self._get_margin_y(node.layer_index + 1)
            for i, child in enumerate(node.children):
                total += margin_y
                total += self._get_node_area_height(child)
        return total

    def _update_brothers_left(self, node: CatalogNode, add_width: float):
        """调整兄弟节点的 left 偏移（向右偏移）"""
        if node.parent is None:
            return
        siblings = node.parent.children
        idx = siblings.index(node)
        for i, sibling in enumerate(siblings):
            if i > idx:
                sibling.left += add_width
                if sibling.children:
                    self._update_children(sibling.children, "left", add_width)
        # 递归向上调整
        self._update_brothers_left(node.parent, add_width)

    def _update_brothers_top(self, node: CatalogNode, add_height: float):
        """调整兄弟节点的 top 偏移（向下偏移）"""
        if node.parent and not node.parent.layer_index == 0:  # 父节点不是根节点
            siblings = node.parent.children
            idx = siblings.index(node)
            for i, sibling in enumerate(siblings):
                if i > idx:
                    sibling.top += add_height
                    if sibling.children:
                        self._update_children(sibling.children, "top", add_height)
            self._update_brothers_top(node.parent, add_height)

    # ------------------------------------------------------------------
    # 核心布局步骤
    # ------------------------------------------------------------------
    def _compute_base_value(self):
        """
        第一步：创建节点，设置根节点位置，设置二级节点的初始 top
        """
        def pre_cb(node: CatalogNode, layer: int, _idx: int):
            if layer:
                # 非根节点：二级节点（父为根）定位到根节点下方
                if node.parent and node.parent.layer_index == 0:
                    margin_y = self._get_margin_y(layer)
                    node.top = node.parent.top + node.parent.height + margin_y

        # 后序遍历：计算根节点的 children_area_width（子节点总宽度）
        def post_cb(node: CatalogNode, layer: int, _idx: int):
            if layer == 0:
                child_count = len(node.children)
                if child_count == 0:
                    node.children_area_width = 0
                else:
                    children_width = sum(child.width for child in node.children)
                    margin_x = self._get_margin_x(layer + 1)
                    node.children_area_width = children_width + (child_count + 1) * margin_x

        self._walk(self.root, pre_cb=pre_cb, post_cb=post_cb)

    def _compute_left_top_value(self):
        """
        第二步：计算子节点的 left 和 top
        - 根节点的子节点水平排列
        - 非根节点的子节点垂直排列
        """
        def pre_cb(node: CatalogNode, layer: int, _idx: int):
            margin_x = self._get_margin_x(layer + 1)
            margin_y = self._get_margin_y(layer + 1)

            if layer == 0:  # 根节点
                # 水平居中排列子节点
                start_left = node.left + node.width / 2 - node.children_area_width / 2
                current_left = start_left + margin_x
                for child in node.children:
                    child.left = current_left
                    current_left += child.width + margin_x
            else:
                # 非根节点：子节点垂直排列
                start_top = node.top + node.height + margin_y
                current_top = start_top
                for child in node.children:
                    child.left = node.left + node.width * 0.5  # 水平居中于父节点
                    child.top = current_top
                    current_top += child.height + margin_y

        self._walk(self.root, pre_cb=pre_cb)

    def _adjust_left_top_value(self):
        """
        第三步：调整位置（处理子树宽度/高度偏移）
        - 前序：对于二级节点，若其子树宽度大于自身宽度，则调整后续兄弟节点
        - 前序：对于非根节点且有子节点，调整垂直偏移
        - 后序：对于根节点，调整所有子节点水平偏移，使整体居中
        """
        # 前序回调
        def pre_cb(node: CatalogNode, layer: int, _idx: int):
            # 调整水平偏移（二级节点及其后代）
            if node.parent and node.parent.layer_index == 0:
                area_width = self._get_node_area_width(node)
                diff = area_width - node.width
                if diff > 0:
                    self._update_brothers_left(node, diff)
            # 调整垂直偏移（非根节点且有子节点）
            if node.parent and node.parent.layer_index != 0 and node.children:
                margin_y = self._get_margin_y(layer + 1)
                total_height = sum(
                    child.height + margin_y
                    for child in node.children
                )
                self._update_brothers_top(node, total_height)

        # 后序回调：根节点整体居中调整
        def post_cb(node: CatalogNode, layer: int, _idx: int):
            if layer == 0:
                left_bound, right_bound = self._get_node_boundaries_horizontal(node)
                children_width = right_bound - left_bound
                # 计算偏移量，使得整个子树在根节点水平方向上居中
                target_center = node.left + node.width / 2
                current_center = left_bound + children_width / 2
                offset = target_center - current_center
                if abs(offset) > 1e-6:
                    self._update_children(node.children, "left", offset)

        self._walk(self.root, pre_cb=pre_cb, post_cb=post_cb)

    def _applay_coords(self):
        """应用计算结果到节点"""
        def _applay_coords_for_node(node: CatalogNode):
            node.node.x = node.left + node.width / 2
            node.node.y = -node.top - node.height / 2
            node.node.level = node.layer_index
            for child in node.children:
                _applay_coords_for_node(child)

        _applay_coords_for_node(self.root)

    def layout(self) -> Any:
        """执行完整布局，返回根节点（坐标已填充）"""
        self._compute_base_value()
        self._compute_left_top_value()
        self._adjust_left_top_value()
        self._applay_coords()
        return self.root.node