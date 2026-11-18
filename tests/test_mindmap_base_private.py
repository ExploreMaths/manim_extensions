from manim import Group, Text

from manim_extensions.mindmap.mindmap.base import AbstractMap
from manim_extensions.mindmap.nodes import Node


def _empty_map():
    result = AbstractMap.__new__(AbstractMap)
    result.node_data_dict = {}
    result.root = Node(Text("root"))
    result.root.ID = ()
    return result


def test_abstract_map_unknown_lookups():
    mindmap = _empty_map()

    assert mindmap.get_node_component("missing") is None
    assert mindmap.get_node("missing") is None
    assert mindmap.get_text("missing") is None
    assert mindmap.get_connector("missing") is None
    assert len(mindmap.get_children("missing")) == 0
    assert len(mindmap.get_submindmap("missing")) == 0
    assert len(mindmap.get_descendants("missing")) == 0


def test_abstract_map_component_generator_handles_unknown_ids():
    mindmap = _empty_map()
    assert list(mindmap.custom_walker(["missing"])) == [None]


def test_abstract_map_set_connectors_is_abstract():
    mindmap = _empty_map()
    try:
        mindmap._set_connectors()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("abstract hook should raise")


def test_get_submindmap_includes_connectors():
    from manim import RIGHT

    from manim_extensions.mindmap.algorithms import LayoutType

    root = Node(Text("root"))
    root.ID = ""
    root.connector = None
    child = Node(Text("child"))
    child.ID = "0"
    root.add_child(child)
    child.set_connector(LayoutType.MindMap, RIGHT)
    mindmap = AbstractMap.__new__(AbstractMap)
    mindmap.node_data_dict = {}
    mindmap.root = root

    group = mindmap.get_submindmap("")

    assert len(group) == 5
