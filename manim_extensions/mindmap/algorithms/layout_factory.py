# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Layout factory for mindmap algorithms.

This module provides factory for creating layout algorithms.

"""

__all__ = [
    "LayoutFactory",
]
from .layout_config import LayoutType, LayoutConfig
from .alg_tidy_tree import TidyTreeLayout
from .alg_standard import StandardLayout
from .alg_time_line import TimeLineLayout
from .alg_catalog import CatalogLayout


class LayoutFactory:
    """Factory for layout algorithms.

    Examples
    --------
    .. manim:: LayoutFactoryExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import bfs_walker
       from manim_extensions.mindmap.mindmap.base import generate_tree
       from manim_extensions.mindmap.algorithms.layout_config import LayoutConfig, LayoutType
       from manim_extensions.mindmap.algorithms.layout_factory import LayoutFactory

       class LayoutFactoryExample(Scene):
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
    def create_layout(layout_type: LayoutType, root, layout_config: LayoutConfig):
        """Create the appropriate layout algorithm instance.

        Parameters
        ----------
        layout_type : LayoutType
            The desired layout type.
        root
            The root node of the tree to lay out.
        layout_config : LayoutConfig
            Configuration object providing layout-specific parameters.

        Returns
        -------
        Layout
            A concrete layout algorithm instance.

        Raises
        ------
        ValueError
            If *layout_type* is not recognised.
        """
        match layout_type:
            case LayoutType.MindMap:
                kwargs = layout_config.mindmap
                return TidyTreeLayout(root, **kwargs)
            case LayoutType.Standard:
                kwargs = layout_config.mindmap
                return StandardLayout(root, **kwargs)
            case LayoutType.Catalog:
                kwargs = layout_config.catalog
                return CatalogLayout(root, **kwargs)
            case LayoutType.TimeLine:
                kwargs = layout_config.timeline
                return TimeLineLayout(root, **kwargs)