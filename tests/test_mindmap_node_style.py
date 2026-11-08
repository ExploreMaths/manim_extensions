# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for node style fallbacks."""

import pytest

from manim_extensions.mindmap.nodes.node import NodeStyle


def test_empty_style_lists_fall_back_to_defaults():
    style = NodeStyle(node_style=[], line_style=[], text_style=[])

    assert style.node_num == 1
    assert style.line_num == 1
    assert style.text_num == 1


def test_explicit_style_lists_are_kept():
    style = NodeStyle(
        node_style=[{"color": "red"}],
        line_style=[{"color": "blue"}],
        text_style=[{"font_size": 20}],
    )

    assert style.node_num == 1
    assert style.node_style[0]["color"] == "red"
    assert style.line_style[0]["color"] == "blue"
    assert style.text_style[0]["font_size"] == 20


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 7])
def test_get_node_style_wraps_by_level(level):
    style = NodeStyle(node_style=[{"color": "red"}, {"color": "blue"}])

    assert len(style.get_node_style(level)) >= 1
