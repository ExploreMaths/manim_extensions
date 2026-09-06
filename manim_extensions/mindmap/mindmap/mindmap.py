# SPDX-FileCopyrightText: 2026 jj-math
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Mindmap main classes for Manim.

This module provides main mindmap classes for visualizations.

"""

__all__ = ["MindMap", "TimeLine", "StandardMap", "CatalogMap"]
from typing import Dict

from manim.constants import *
from manim.utils.color import *

from .base import NodeMobject, AbstractMap, generate_tree
from ..nodes import NodeStyle, bfs_walker
from ..algorithms import (
    TidyTreeLayout,
    TimeLineLayout,
    StandardLayout,
    CatalogLayout,
    LayoutConfig,
    LayoutType,
)


class MindMap(AbstractMap):
    r"""Mind map class: parses mind-map data in the following format and builds
    the corresponding mind-map object.

    Parameters
    ----------
        map : dict
            mind-map data
        buff : float
            padding between node content and node border
        direction
            node layout direction
        level_spacing : float
            spacing between layers
        node_spacing : float
            spacing between nodes
        node_style : :class:`~manim_extensions.mindmap.NodeStyle`
            node style

    Examples
    --------
    .. manim:: MindMapExample

       from manim import *
       from manim_extensions.mindmap import MindMap

       class MindMapExample(Scene):
           def construct(self):
               data = {
                   'node': MathTex(r"\text{Calculus}"),
                   'text': 'narration text for TTS',
                   'child': [
                       {'node': MathTex(r"\text{Limits}")},
                       {'node': MathTex(r"\text{Derivatives}")},
                       {'node': MathTex(r"\text{Integrals}"),
                        'child': [
                            {'node': MathTex(r"\int x\,dx")},
                            {'node': MathTex(r"\int x^2\,dx")},
                        ]},
                   ]
               }
               mind_map = MindMap(data)
               mind_map.scale_to_fit_width(12)
               for node in mind_map.dfs_walker():
                   if node.connector:
                       self.play(Create(node.connector), run_time=0.3)
                   self.play(Create(node.surr_rect), Write(node.vmobject),
                             run_time=0.3)
               children = mind_map.get_children((0, 2))
               self.play(*[Wiggle(child) for child in children])
               self.wait()
    """

    def __init__(
        self,
        map: Dict = {},
        buff: float = 0.2,
        direction: object = RIGHT,
        level_spacing: float = 1.0,
        node_spacing: float = 0.5,
        node_style: NodeStyle = NodeStyle(
            node_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            line_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            text_style=[
                {"color": RED, "font_size": 64},
                {"color": PURE_YELLOW, "font_size": 56},
                {"color": GREEN, "font_size": 48},
                {"color": WHITE, "font_size": 36},
            ],
        ),
    ):
        """Initialize MindMap."""
        self.node_style = node_style
        self.direction = direction
        super().__init__(
            layout_method=TidyTreeLayout(
                root=generate_tree(Map=map, node_style=node_style, buff=buff),
                **LayoutConfig(
                    direction=direction,
                    node_spacing=node_spacing,
                    level_spacing=level_spacing,
                ).mindmap,
            )
        )

    def _set_connectors(self) -> None:
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = (
                node.get_connector(
                    LayoutType.MindMap,
                    direction=self.direction,
                    **self._get_connector_style(level=len(node.ID)),
                )
                if node.parent is not None
                else None
            )

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject=node.vmobject,
                surr_rect=node.surr_rect,
                connector=node.connector,
                text=node.text,
            )


class TimeLine(AbstractMap):
    r"""
    Timeline: data format is the same as :class:`~manim_extensions.mindmap.mindmap.mindmap.MindMap`.

    Parameters
    ----------
    map : dict
        timeline data
    buff : float
        padding between node content and node border
    sides
        node layout direction; growth direction of subtrees rooted at
        second-level nodes
    level_spacing : float
        spacing between layers
    node_spacing : float
        spacing between nodes
    node_style : :class:`~manim_extensions.mindmap.NodeStyle`
        node style


    .. manim:: TimeLineDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import TimeLine

       class TimeLineDocExample(Scene):
           def construct(self):
               data = {
                   'node': MathTex(r"\text{History}"),
                   'child': [
                       {'node': MathTex(r"2022")},
                       {'node': MathTex(r"2023")},
                       {'node': MathTex(r"2024")},
                   ]
               }
               timeline = TimeLine(data)
               timeline.scale_to_fit_width(12)
               self.add(timeline)
               timeline.get_node((0, 1)).set_color(YELLOW)
    """

    def __init__(
        self,
        map: Dict = {},
        buff: float = 0.2,
        sides: tuple[object, object] = (UP, DOWN),
        level_spacing: float = 1.0,
        node_spacing: float = 0.5,
        node_style: NodeStyle = NodeStyle(
            node_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            line_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            text_style=[
                {"color": RED, "font_size": 64},
                {"color": PURE_YELLOW, "font_size": 56},
                {"color": GREEN, "font_size": 48},
                {"color": WHITE, "font_size": 36},
            ],
        ),
    ):
        """Initialize the TimeLine instance."""
        self.node_style = node_style
        super().__init__(
            layout_method=TimeLineLayout(
                root=generate_tree(Map=map, node_style=node_style, buff=buff),
                **LayoutConfig(
                    node_spacing=node_spacing, level_spacing=level_spacing, sides=sides
                ).timeline,
            )
        )

    def _set_connectors(self) -> None:
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = (
                node.get_connector(
                    LayoutType.TimeLine,
                    direction=RIGHT,
                    **self._get_connector_style(level=len(node.ID)),
                )
                if node.parent is not None
                else None
            )

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject=node.vmobject,
                surr_rect=node.surr_rect,
                connector=node.connector,
                text=node.text,
            )


class StandardMap(AbstractMap):
    r"""
    Two-sided mind map: data format is the same as :class:`~manim_extensions.mindmap.mindmap.mindmap.MindMap`.

    Parameters
    ----------
    map : dict
        mind-map data
    buff : float
        padding between node content and node border
    direction
        layout direction
    level_spacing : float
        spacing between layers
    node_spacing : float
        spacing between nodes
    node_style : :class:`~manim_extensions.mindmap.NodeStyle`
        node style


    .. manim:: StandardMapDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import StandardMap

       class StandardMapDocExample(Scene):
           def construct(self):
               data = {
                   'node': MathTex(r"\text{Root}"),
                   'child': [
                       {'node': MathTex(r"\text{Left}"),
                        'child': [
                            {'node': MathTex(r"\text{L1}")},
                            {'node': MathTex(r"\text{L2}")},
                        ]},
                       {'node': MathTex(r"\text{Right}")},
                   ]
               }
               mind_map = StandardMap(data)
               mind_map.scale_to_fit_width(12)
               self.add(mind_map)
               mind_map.get_children((0, 0)).set_color(YELLOW)
    """

    def __init__(
        self,
        map: Dict = {},
        buff: float = 0.2,
        direction: object = RIGHT,
        level_spacing: float = 1.0,
        node_spacing: float = 0.5,
        node_style: NodeStyle = NodeStyle(
            node_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            line_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            text_style=[
                {"color": RED, "font_size": 64},
                {"color": PURE_YELLOW, "font_size": 56},
                {"color": GREEN, "font_size": 48},
                {"color": WHITE, "font_size": 36},
            ],
        ),
    ):
        """Initialize the StandardMap instance."""
        self.node_style = node_style
        super().__init__(
            layout_method=StandardLayout(
                root=generate_tree(Map=map, node_style=node_style, buff=buff),
                **LayoutConfig(
                    direction=direction,
                    node_spacing=node_spacing,
                    level_spacing=level_spacing,
                ).mindmap,
            )
        )

    def _set_connectors(self) -> None:
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = (
                node.get_connector(
                    LayoutType.Standard,
                    direction=RIGHT,
                    **self._get_connector_style(level=len(node.ID)),
                )
                if node.parent is not None
                else None
            )

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject=node.vmobject,
                surr_rect=node.surr_rect,
                connector=node.connector,
                text=node.text,
            )


class CatalogMap(AbstractMap):
    r"""
    Catalog / organisation-chart: data format is the same as :class:`~manim_extensions.mindmap.mindmap.mindmap.MindMap`,
    layout direction is downwards.

    Parameters
    ----------
    map : dict
        catalog data
    buff : float
        padding between node content and node border
    level_spacing : float
        spacing between layers
    node_spacing : float
        spacing between nodes
    node_style : :class:`~manim_extensions.mindmap.NodeStyle`
        node style


    .. manim:: CatalogMapDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions.mindmap import CatalogMap

       class CatalogMapDocExample(Scene):
           def construct(self):
               data = {
                   'node': MathTex(r"\text{Company}"),
                   'child': [
                       {'node': MathTex(r"\text{Engineering}"),
                        'child': [
                            {'node': MathTex(r"\text{Dev}")},
                            {'node': MathTex(r"\text{QA}")},
                        ]},
                       {'node': MathTex(r"\text{Sales}")},
                   ]
               }
               catalog = CatalogMap(data)
               catalog.scale_to_fit_width(12)
               self.add(catalog)
               catalog.get_descendants((0, 0)).set_color(YELLOW)
    """

    def __init__(
        self,
        map: Dict = {},
        buff: float = 0.2,
        level_spacing: float = 1.0,
        node_spacing: float = 0.5,
        node_style: NodeStyle = NodeStyle(
            node_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            line_style=[
                {"color": WHITE, "stroke_width": 8},
                {"color": WHITE, "stroke_width": 6},
                {"color": WHITE, "stroke_width": 4},
            ],
            text_style=[
                {"color": RED, "font_size": 64},
                {"color": PURE_YELLOW, "font_size": 56},
                {"color": GREEN, "font_size": 48},
                {"color": WHITE, "font_size": 36},
            ],
        ),
    ):
        """Initialize the CatalogMap instance."""
        self.node_style = node_style
        super().__init__(
            layout_method=CatalogLayout(
                root=generate_tree(Map=map, node_style=node_style, buff=buff),
                **LayoutConfig(
                    node_spacing=node_spacing,
                    level_spacing=level_spacing,
                ).catalog,
            )
        )

    def _set_connectors(self) -> None:
        """Set connection lines."""
        for node in bfs_walker(self.root):
            node.connector = (
                node.get_connector(
                    LayoutType.Catalog,
                    direction=RIGHT,
                    **self._get_connector_style(level=len(node.ID)),
                )
                if node.parent is not None
                else None
            )

            self.node_data_dict[node.ID] = NodeMobject(
                vmobject=node.vmobject,
                surr_rect=node.surr_rect,
                connector=node.connector,
                text=node.text,
            )