# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

import pytest
from manim import ImageMobject, MathTex, RIGHT, Text

from manim_extensions.mindmap import Node
from manim_extensions.mindmap.algorithms import LayoutType
from manim_extensions.mindmap.animations.animations import (
    AbstractLayoutAnimation,
    InsertNode,
    animate_of_create,
)


def test_animate_of_create_for_math_text_image_and_plain():
    root = Node(Text("Root"))
    plain = Node(Text("Child"))
    math = Node(MathTex("x"))
    image = Node(ImageMobject([[0.0]]))
    root.add_child(plain)

    assert animate_of_create(plain, RIGHT * 2, RIGHT, {}, {}, LayoutType.MindMap)
    assert animate_of_create(math, RIGHT * 2, RIGHT, {}, {}, LayoutType.MindMap)
    assert animate_of_create(image, RIGHT * 2, RIGHT, {}, {}, LayoutType.MindMap)


def test_get_common_root_returns_none_for_different_trees():
    animation = InsertNode.__new__(InsertNode)
    first = Node(Text("A"))
    second = Node(Text("B"))

    assert animation.get_common_root([first, second]) is None


def test_get_root_rejects_empty_and_different_trees():
    animation = InsertNode.__new__(InsertNode)
    first = Node(Text("A"))
    second = Node(Text("B"))

    try:
        animation.get_root([])
    except Exception:
        pass
    else:
        raise AssertionError("empty list should raise")

    try:
        animation.get_root([first, second])
    except Exception:
        pass
    else:
        raise AssertionError("different trees should raise")


def test_abstract_collect_animations_not_implemented():
    animation = AbstractLayoutAnimation.__new__(AbstractLayoutAnimation)
    try:
        animation.collect_animations()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("abstract method should raise")


def test_layout_animation_alter_node_off_scene():
    from manim import Scene

    from manim_extensions.mindmap.algorithms.layout_config import LayoutConfig
    from manim_extensions.mindmap.animations.animations import LayoutAnimation
    from manim_extensions.mindmap.nodes.node import NodeState

    scene = Scene()
    root = Node(Text("root"))
    root.node_state = NodeState.ALTER
    with pytest.raises(Exception, match="alter node"):
        LayoutAnimation(scene, root, layout_config=LayoutConfig())


def test_remove_node_with_parentless_root_and_empty_tree():
    from manim import Scene

    from manim_extensions.mindmap.animations.animations import RemoveNode
    from manim_extensions.mindmap.nodes.node import NodeState

    scene = Scene()
    root = Node(Text("root"))
    root.node_state = NodeState.REMOVE
    with pytest.raises(Exception, match="not on current scene"):
        RemoveNode(scene, root)


def test_remove_child_not_in_parent_children():
    from manim import Scene

    from manim_extensions.mindmap.animations.animations import LayoutAnimation
    from manim_extensions.mindmap.nodes.node import NodeState

    scene = Scene()
    root = Node(Text("root"))
    child = Node(Text("child"))
    root.add_child(child)
    root.children.remove(child)
    child.node_state = NodeState.REMOVE
    scene.add(child.vmobject)
    import importlib

    module = importlib.import_module("manim_extensions.mindmap.animations.animations")

    original_walker = module.bfs_walker
    module.bfs_walker = lambda root: iter((root, child))
    animation = LayoutAnimation.__new__(LayoutAnimation)
    animation.root = root
    animation.scene = scene

    try:
        with pytest.raises(ValueError):
            animation._check_node_state()
    finally:
        module.bfs_walker = original_walker


def test_remove_node_duplicate_root_trees_raises():
    from manim import Scene

    from manim_extensions.mindmap.animations.animations import RemoveNode

    first = Node(Text("A"))
    second = Node(Text("B"))
    with pytest.raises(Exception, match="same tree"):
        RemoveNode(Scene(), [first, second])


def test_parentless_remove_node_on_scene_is_collected():
    from manim import Scene

    from manim_extensions.mindmap.animations.animations import LayoutAnimation
    from manim_extensions.mindmap.nodes.node import NodeState

    scene = Scene()
    root = Node(Text("root"))
    scene.add(root.vmobject)
    root.node_state = NodeState.REMOVE
    animation = LayoutAnimation.__new__(LayoutAnimation)
    animation.root = root
    animation.scene = scene

    assert animation._check_node_state() == [root]
