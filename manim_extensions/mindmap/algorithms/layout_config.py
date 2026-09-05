# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Layout configuration for mindmap algorithms.

This module provides configuration classes for layout algorithms.

"""

from manim import *

__all__ = ["LayoutConfig", "LayoutDirection", "LayoutType"]
from enum import Enum
from typing import List, Dict
import numpy as np


class LayoutDirection(Enum):
    """Layout direction.

    Examples
    --------
    .. manim:: LayoutDirectionExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap.algorithms.layout_config import LayoutDirection

       class LayoutDirectionExample(Scene):
           def construct(self):
               directions = [
                   (RIGHT, LayoutDirection.LeftToRight),
                   (LEFT, LayoutDirection.RightToLeft),
                   (DOWN, LayoutDirection.TopToBottom),
                   (UP, LayoutDirection.BottomToTop),
               ]
               panels = VGroup()
               for vector, direction in directions:
                   arrow = Arrow(ORIGIN, 1.2 * vector, buff=0, stroke_width=4)
                   label = Text(direction.value, font_size=24)
                   label.next_to(arrow, vector, buff=0.2)
                   panels.add(VGroup(arrow, label))
               panels.arrange_in_grid(rows=2, cols=2, buff=(1.5, 1.2))
               self.add(panels)
    """

    LeftToRight = "left to right"
    RightToLeft = "right to left"
    TopToBottom = "top to bottom"
    BottomToTop = "bottom to top"


class LayoutType(Enum):
    """Layout algorithm.

    Examples
    --------
    .. manim:: LayoutTypeExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import CatalogMap, MindMap, StandardMap, TimeLine
       from manim_extensions.mindmap.algorithms.layout_config import LayoutType

       class LayoutTypeExample(Scene):
           def construct(self):
               data = {
                   "node": MathTex(r"\text{Root}", font_size=48),
                   "child": [
                       {"node": MathTex(r"A", font_size=44)},
                       {"node": MathTex(r"B", font_size=44)},
                       {"node": MathTex(r"C", font_size=44)},
                   ],
               }
               maps = Group(
                   MindMap(data),
                   TimeLine(data),
                   StandardMap(data),
                   CatalogMap(data),
               )
               for mind_map in maps:
                   mind_map.scale_to_fit_width(5.2)
               maps.arrange_in_grid(rows=2, cols=2, buff=(0.8, 0.8))
               self.add(maps)
               for mind_map, layout_type in zip(maps, LayoutType):
                   label = Text(layout_type.value, font_size=24)
                   label.next_to(mind_map, UP, buff=0.15)
                   self.add(label)
    """

    MindMap = "tidytree"
    TimeLine = "timeline"
    Standard = "standard"
    Catalog = "catalog"


class LayoutConfig:
    """Configuration options for mind-map layouts.

    Examples
    --------
    .. manim:: LayoutConfigExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import bfs_walker
       from manim_extensions.mindmap.mindmap.base import generate_tree
       from manim_extensions.mindmap.algorithms.layout_config import LayoutConfig, LayoutType
       from manim_extensions.mindmap.algorithms.layout_factory import LayoutFactory

       class LayoutConfigExample(Scene):
           def construct(self):
               config = LayoutConfig(direction=UP, node_spacing=0.8, level_spacing=1.5)
               data = {
                   "node": Tex("Root"),
                   "child": [{"node": Tex("A")}, {"node": Tex("B")}],
               }
               root = generate_tree(Map=data)
               root = LayoutFactory.create_layout(
                   LayoutType.MindMap, root, config
               ).layout()
               mobjects = Group()
               for node in bfs_walker(root):
                   node.vmobject.move_to([node.x, node.y, 0])
                   node.surr_rect.move_to([node.x, node.y, 0])
                   mobjects.add(node.vmobject, node.surr_rect)
               mobjects.scale_to_fit_height(6)
               self.add(mobjects)
    Parameters
    ----------
        direction : np.ndarray, optional
            Layout direction. Defaults to RIGHT.
        node_spacing : float, optional
            Spacing between nodes. Defaults to 0.5.
        level_spacing : float, optional
            Spacing between layers. Defaults to 0.5.
        sides : np.ndarray | List[np.ndarray], optional
            Sides used for alternating timeline layouts; a single value means single-sided. Defaults to (UP,DOWN).
    """

    def __init__(
        self,
        direction: np.ndarray = RIGHT,
        node_spacing: float = 0.5,
        level_spacing: float = 0.5,
        sides: np.ndarray | List[np.ndarray] = (UP, DOWN),
    ):
        """Initialize LayoutConfig."""
        if not any(np.array_equal(direction, d) for d in [UP, DOWN, LEFT, RIGHT]):
            raise ValueError(f"direction must be one of {LEFT,RIGHT,UP,DOWN}")
        if not isinstance(sides, (list, tuple)):
            sides = (sides,)
        for side in sides:
            if not any(np.array_equal(side, d) for d in [UP, DOWN]):
                raise ValueError(f"side must be one of {UP,DOWN}")

        self.sides = tuple(self.get_layout_direction(side) for side in sides)
        self.layout_direction = self.get_layout_direction(direction)
        self.node_spacing = node_spacing
        self.level_spacing = level_spacing
        self.direction = direction

    def get_layout_direction(self, direction: np.ndarray) -> LayoutDirection:
        """Convert a direction vector to a LayoutDirection enum.

        Parameters
        ----------
        direction : np.ndarray
        The direction of the operation.
        """
        string = None
        if np.array_equal(direction, UP):
            string = LayoutDirection.BottomToTop
        elif np.array_equal(direction, DOWN):
            string = LayoutDirection.TopToBottom
        elif np.array_equal(direction, LEFT):
            string = LayoutDirection.RightToLeft
        elif np.array_equal(direction, RIGHT):
            string = LayoutDirection.LeftToRight
        return string

    @property
    def catalog(self):
        """Return the catalog layout settings as a dictionary."""
        return {
            "node_spacing": self.node_spacing,
            "level_spacing": self.level_spacing,
        }

    @catalog.setter
    def catalog(
        self,
        catalog: Dict = {
            "node_spacing": 0.5,
            "level_spacing": 0.5,
        },
    ):
        """Update the catalog layout settings from a dictionary.

        Parameters
        ----------
        catalog : Dict
            Dictionary with ``node_spacing`` and ``level_spacing`` keys.
        """
        self.node_spacing = catalog.get("node_spacing", 0.5)
        self.level_spacing = catalog.get("level_spacing", 0.5)

    @property
    def mindmap(self):
        """Return the mind map layout settings as a dictionary."""
        return {
            "direction": self.layout_direction,
            "node_spacing": self.node_spacing,
            "level_spacing": self.level_spacing,
        }

    @mindmap.setter
    def mindmap(
        self,
        mindmap: Dict = {"direction": RIGHT, "node_spacing": 0.5, "level_spacing": 0.5},
    ):
        """Update the mind map layout settings from a dictionary.

        Parameters
        ----------
        mindmap : Dict
            Dictionary with ``direction``, ``node_spacing``, and
            ``level_spacing`` keys.
        """
        direction = mindmap.get("direction", RIGHT)
        if not any(np.array_equal(direction, d) for d in [UP, DOWN, LEFT, RIGHT]):
            raise ValueError(f"direction must be one of {LEFT,RIGHT,UP,DOWN}")
        self.direction = direction
        self.layout_direction = self.get_layout_direction(direction)
        self.node_spacing = mindmap.get("node_spacing", 0.5)
        self.level_spacing = mindmap.get("level_spacing", 0.5)

    @property
    def timeline(self):
        """Return the timeline layout settings as a dictionary."""
        return {
            "node_spacing": self.node_spacing,
            "level_spacing": self.level_spacing,
            "sides": self.sides,
        }

    @timeline.setter
    def timeline(
        self,
        timeline: Dict = {
            "node_spacing": 0.5,
            "level_spacing": 0.5,
            "sides": (UP, DOWN),
        },
    ):
        """Update the timeline layout settings from a dictionary.

        Parameters
        ----------
        timeline : Dict
            Dictionary with ``node_spacing``, ``level_spacing``, and
            ``sides`` keys.
        """
        self.node_spacing = timeline.get("node_spacing", 0.5)
        self.level_spacing = timeline.get("level_spacing", 0.5)
        sides = timeline.get("sides", (UP, DOWN))
        if not isinstance(sides, (list, tuple)):
            sides = (sides,)
        for side in sides:
            if not any(np.array_equal(side, d) for d in [UP, DOWN]):
                raise ValueError(f"side must be one of {UP,DOWN}")
        self.sides = tuple(self.get_layout_direction(side) for side in sides)