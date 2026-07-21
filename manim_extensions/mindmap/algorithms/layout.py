__all__ = [
    'Layout'
]
from typing import Any

class Layout:
    """Base class for layout algorithms.

    .. manim:: LayoutDocExample
        :save_last_frame:
        
        from manim import *
        from manim_extensions.mindmap.algorithms.layout import Layout
        
        class LayoutDocExample(Scene):
            def construct(self):
                class FixedLayout(Layout):
                    def layout(self):
                        return None
        
                self.add(Text(f"FixedLayout().layout() = {FixedLayout().layout()}", font_size=36))
    """
    def layout(self) -> Any:
        """Run the layout computation and return the root node."""
        raise NotImplementedError