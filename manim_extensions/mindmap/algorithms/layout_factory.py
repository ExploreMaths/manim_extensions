__all__ = [
    'LayoutFactory',
]
from .layout_config import LayoutType,LayoutConfig
from .alg_tidy_tree import TidyTreeLayout
from .alg_standard import StandardLayout
from .alg_time_line import TimeLineLayout
from .alg_catalog import CatalogLayout

class LayoutFactory:
    '''布局算法工厂'''
    @staticmethod
    def create_layout(
        layout_type: LayoutType,
        root,
        layout_config:LayoutConfig
    ):
        """根据布局类型创建对应的布局算法实例"""
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