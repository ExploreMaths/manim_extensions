__all__ = [
    'Layout'
]
from typing import Any

class Layout:
    """Base class for layout algorithms."""
    def layout(self) -> Any:
        """Run the layout computation and return the root node."""
        raise NotImplementedError