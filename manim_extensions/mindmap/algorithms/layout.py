__all__ = [
    'Layout'
]
from typing import Any

class Layout:
    """Base class for layout algorithms.

    Examples
    --------

    .. manim:: LayoutExample
      :save_last_frame:

        from manim import *
        from manim_extensions.mindmap.algorithms.layout import Layout

        class LayoutExample(Scene):
            def construct(self):
                layout = Layout()
                label = Text("Layout base class", font_size=24)
                self.add(label)
"""
    def layout(self) -> Any:
        """Run the layout computation and return the root node."""
        raise NotImplementedError