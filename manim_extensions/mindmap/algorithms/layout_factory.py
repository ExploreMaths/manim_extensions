__all__ = [
    'LayoutFactory',
]
from .layout_config import LayoutType,LayoutConfig
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
        from manim_extensions.mindmap.algorithms.layout_factory import LayoutFactory

        class LayoutFactoryExample(Scene):
            def construct(self):
                label = Text("LayoutFactory creates layout algorithms", font_size=24)
                self.add(label)
"""
    @staticmethod
    def create_layout(
        layout_type: LayoutType,
        root,
        layout_config: LayoutConfig
    ):
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