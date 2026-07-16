__all__ = [
    'Layout'
]
from typing import Any

class Layout:
    """布局算法基类"""
    def layout(self) -> Any:
        """执行布局计算并返回根节点"""
        raise NotImplementedError