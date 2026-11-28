# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

""":class:`~manim_extensions.mindmap.algorithms.layout.Layout` factory for mindmap algorithms.

This module provides factory for creating layout algorithms.
"""

__all__ = [
    "LayoutFactory",
]
from typing import cast

from .layout import Layout
from .layout_config import LayoutType, LayoutConfig
from .alg_tidy_tree import NodeLike, TidyTreeLayout
from .alg_standard import StandardLayout, TreeNode
from .alg_time_line import TimeLineLayout, _TimelineInput
from .alg_catalog import CatalogLayout, _CatalogInput


class LayoutFactory:
    """Factory for layout algorithms.

    Examples
    --------
    .. manim:: LayoutFactoryScene
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import bfs_walker
       from manim_extensions.mindmap.mindmap.base import generate_tree
       from manim_extensions.mindmap.algorithms.layout_config import LayoutConfig, LayoutType
       from manim_extensions.mindmap.algorithms.layout_factory import LayoutFactory

       class LayoutFactoryScene(Scene):
           def construct(self):
               data = {
                   "node": Tex("Root"),
                   "child": [{"node": Tex("A")}, {"node": Tex("B")}],
               }
               panels = Group()
               for layout_type in (LayoutType.MindMap, LayoutType.Catalog):
                   root = generate_tree(Map=data)
                   config = LayoutConfig()
                   root = LayoutFactory.create_layout(layout_type, root, config).layout()
                   panel = Group()
                   for node in bfs_walker(root):
                       node.vmobject.move_to([node.x, node.y, 0])
                       node.surr_rect.move_to([node.x, node.y, 0])
                       panel.add(node.vmobject, node.surr_rect)
                   panel.scale_to_fit_height(3.5)
                   label = Text(layout_type.value, font_size=24)
                   panels.add(Group(panel, label).arrange(DOWN))
               panels.arrange(RIGHT, buff=1.2)
               self.add(panels)
    """

    @staticmethod
    def create_layout(
        layout_type: LayoutType, root: object, layout_config: LayoutConfig
    ) -> Layout:
        """Create the appropriate layout algorithm instance.

        Parameters
        ----------
        layout_type
            The desired layout type.
        root
            The root node of the tree to lay out.
        layout_config
            Configuration object providing layout-specific parameters.

        Returns
        -------
            A concrete layout algorithm instance.

        Raises
        ------
        ValueError
            If ``layout_type`` is not recognised.
        """
        match layout_type:
            case LayoutType.MindMap:
                mindmap_kwargs = layout_config.mindmap
                return TidyTreeLayout(cast(NodeLike, root), **mindmap_kwargs)
            case LayoutType.Standard:
                standard_kwargs = layout_config.mindmap
                return StandardLayout(cast(TreeNode, root), **standard_kwargs)
            case LayoutType.Catalog:
                catalog_kwargs = layout_config.catalog
                return CatalogLayout(cast(_CatalogInput, root), **catalog_kwargs)
            case LayoutType.TimeLine:
                timeline_kwargs = layout_config.timeline
                return TimeLineLayout(cast(_TimelineInput, root), **timeline_kwargs)
