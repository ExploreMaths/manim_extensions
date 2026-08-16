# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import Code as ManimCode

from manim_extensions.algorithm import Array, Code, Node, NodeConfig, NodeSolt, PythonCode


def test_algorithm_objects_and_helpers():
    cfg = NodeConfig()
    slot = NodeSolt()
    assert cfg.WIDTH > 0
    assert slot.LEFT_MID[0] is not None

    node = Node(value=7, width=2.0, text_scale=1.2)
    assert node.get_value() == 7
    assert node.get_box() is not None
    assert node.get_fill_color() is not None

    arr = Array([1, 2, 3], total_width=6)
    assert len(arr) == 3
    assert arr.values == [1, 2, 3]
    assert arr[1].get_value() == 2

    code = Code(code="print('hi')")
    assert isinstance(code, ManimCode)

    py = PythonCode(code="x = 1")
    assert py is not None
