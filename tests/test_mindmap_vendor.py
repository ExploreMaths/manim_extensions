# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *
import numpy as np

from manim_extensions.mindmap import (
    CatalogMap,
    MindMap,
    Node,
    NodeStyle,
    StandardMap,
    TimeLine,
)


def test_node_style_fields():
    style = NodeStyle()

    assert style.node_num == 4
    assert style.line_num == 4
    assert style.text_num == 4
    assert style.get_node_style(0)["color"] is not None
    assert style.get_line_style(0)["color"] is not None
    assert style.get_text_style(0)["color"] is not None


def test_node_constructor_and_attributes():
    text = MathTex(r"\text{Root}")
    node = Node(text)

    assert node.vmobject is text
    assert node.surr_rect is not None
    assert node.children == []
    assert node.parent is None
    assert node.node_state.name == "INSERT"
    assert node.buff == 0.2
    assert node.width > 0
    assert node.height > 0


def test_mindmap_variants():
    data = {
        "node": MathTex(r"\text{Root}"),
        "child": [{"node": MathTex(r"\text{Left}")}, {"node": MathTex(r"\text{Right}")}],
    }

    mind_map = MindMap(data, direction=RIGHT)
    timeline = TimeLine(data)
    standard = StandardMap(data, direction=RIGHT)
    catalog = CatalogMap(data)

    for obj in (mind_map, timeline, standard, catalog):
        assert obj.root is not None
        assert obj.node_style is not None
        assert hasattr(obj, "node_data_dict")

    assert np.allclose(mind_map.direction, RIGHT)
    assert timeline is not None
    assert standard is not None
    assert catalog is not None
