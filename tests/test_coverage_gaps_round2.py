# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Additional tests for reachable branches left uncovered by the main suite."""

from types import SimpleNamespace

import cairo
import numpy as np
import pytest
from manim import (
    Arc,
    DOWN,
    LEFT,
    Line,
    PI,
    RED,
    RIGHT,
    Scene,
    UP,
    VMobject,
    tempconfig,
)

from manim_extensions.automata.mobjects.manim_state import ManimState
from manim_extensions.automata.mobjects.manim_transition import ManimTransition
from manim_extensions.chemistry.threeD.threedbond import ThreeDBond
from manim_extensions.compass.animations.animation_compass import (
    PutCompassAway,
    SplitCompass,
)
from manim_extensions.compass.animations.animation_ruler import PutRulerAway
from manim_extensions.compass.compass import Compass, Ruler
from manim_extensions.compass.scene.compass_scene import CompassScene
from manim_extensions.machine_learning.neural_network.layers.parent_layers import (
    NeuralNetworkLayer,
)
from manim_extensions.machine_learning.neural_network.layers.feed_forward import (
    FeedForwardLayer,
)
from manim_extensions.meshes.exceptions import (
    InvalidMeshDimensionsException,
    InvalidMeshException,
    InvalidShapeException,
)
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.models.manim_models.basic_mesh import (
    Manim2DMesh,
    ManimMesh,
)
from manim_extensions.mindmap.algorithms.alg_time_line import TimeLineLayout
from manim_extensions.mindmap.algorithms.alg_time_line import walk
from manim_extensions.mobject_svg.svg import (
    _create_svg_from_vmobject_internal,
    _set_cairo_context_color,
    create_svg_from_vmobject,
)
from manim_extensions.physics.electromagnetism.electrostatics import (
    Charge,
    ElectricField,
)
from manim_extensions.table import Table


def test_negative_charge_without_glow_and_field_probe():
    charge = Charge(-1, LEFT, add_glow=False)
    field = ElectricField(charge)

    assert charge.magnitude == -1
    assert field.charges == (charge,)
    assert np.allclose(field._field_func(RIGHT, [LEFT], [-1]), [-0.25, 0, 0])
    assert np.allclose(field._field_func(LEFT, [LEFT], [-1]), np.zeros(3))


@pytest.fixture()
def compass_scene():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        instance = CompassScene()
        instance.setup()
        yield instance


def test_compass_scene_remaining_methods(compass_scene):
    compass_scene.compass_move_niddle_tip_to(RIGHT, run_time=0.1)
    compass_scene.rotate_compass_about_niddle_tip(0.2, added_anims=[], run_time=0.1)
    compass_scene.rotate_compass_about_niddle_tip(Arc(angle=PI / 2), run_time=0.1)
    compass_scene.compass_split_span(span=1.0, run_time=0.1)
    compass_scene.split_cmpass_span(span=0.8, run_time=0.1)
    compass_scene.flip_compass(run_time=0.1)
    compass_scene.set_ruler(LEFT, RIGHT, run_time=0.1, with_pencil=False)
    compass_scene.draw_line(LEFT, RIGHT, run_time=0.1, with_pencil=False)
    compass_scene.set_pencil(RIGHT, run_time=0.1)
    compass_scene.put_pencil_away(run_time=0.1)

    assert compass_scene.pencil is not None


def test_compass_animation_constructors():
    compass = Compass()
    ruler = Ruler()

    split = SplitCompass(compass, span=1.0)
    away = PutCompassAway(compass, 3 * RIGHT)
    ruler_away = PutRulerAway(ruler, UP, is_flat=False)

    assert split is not None and away is not None and ruler_away is not None


@pytest.fixture()
def transition_states():
    first = ManimState("q1", 0.0, 0.0, "Straight")
    second = ManimState("q2", 3.0, 0.0, "Straight")
    return first, second


def test_opposite_transition_conversion(transition_states):
    first, second = transition_states
    forward = ManimTransition(first, second, ["a"], Scene(), animation_style={})
    first.add_transition_to_state(forward)

    backward = ManimTransition(second, first, ["b"], Scene(), animation_style={})

    assert backward.arrow is not None


def test_transition_position_text_with_list_source(transition_states):
    first, _ = transition_states
    fake = SimpleNamespace(
        transition_from=[0.0, 0.0],
        transition_to=SimpleNamespace(get_x=lambda: 2.0, get_y=lambda: 2.0),
        read_symbols=[],
        calculate_direction_of_arrow_label=lambda: [0.0, 1.0, 0.0],
    )

    ManimTransition.position_text(fake, 1.0)


def test_transition_degenerate_slope():
    fake = SimpleNamespace(
        arrow=SimpleNamespace(
            get_start=lambda: np.array([0.0, 0.0, 0.0]),
            get_end=lambda: np.array([0.0, 0.0, 0.0]),
        )
    )

    assert ManimTransition.calculate_slope_of_line(fake) == 0


def test_svg_gradient_empty_and_default_path(tmp_path):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
    ctx = cairo.Context(surface)
    gradient_line = Line(LEFT, RIGHT).set_color_by_gradient(RED, RED)
    _set_cairo_context_color(ctx, gradient_line.get_stroke_rgbas(), gradient_line)

    _create_svg_from_vmobject_internal(VMobject(), ctx)
    written = create_svg_from_vmobject(Line(LEFT, RIGHT))

    assert written is not None


def test_table_extra_columns_scale_and_column_positions():
    table = Table(data=[["A", "B"], ["long", "x"], ["another", "y"]])
    table.row_values.append(["extra", "ignored", "too-many"])
    assert len(table.calculate_column_widths()) == 2
    table.row_values.pop()

    table.scale(2.0)
    _, animations = table.add_row(["A", "B"])
    assert animations

    forward = table.add_column("C", ["1", "2", "3"], index=0)
    backward = table.add_column("D", ["4", "5", "6"], index=-1)

    assert forward[0] is not None and backward[0] is not None


def test_mindmap_walk_and_area_height():
    class Node:
        def __init__(self, width=1.0, height=1.0):
            self.width = width
            self.height = height
            self.children = []

    root = Node()
    child = Node(0.5, 0.5)
    leaf = Node(0.2, 0.2)
    child.children.append(leaf)
    root.children.append(child)
    visited = []

    walk(
        root,
        None,
        lambda *args: visited.append(args[0]) or True,
        None,
        True,
        0,
        0,
    )

    layout = TimeLineLayout(root)
    assert layout._get_node_area_height(root) > 0
    assert layout._get_node_act_children_length(root) == 1


def test_parent_layer_title_debug_and_abstract_bodies():
    layer = FeedForwardLayer(3, title="Layer", debug_mode=True)
    layer.construct_layer(None, None, debug_mode=True)

    assert layer.title is not None
    assert NeuralNetworkLayer.make_forward_pass_animation(layer) is None


def test_mesh_error_branches_and_display_vertices():
    mesh = Mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])
    manim_mesh = ManimMesh(mesh, display_vertices=True)
    played = []
    manim_mesh.add_vertices(
        np.array([[1.0, 1.0, 0.0]]),
        SimpleNamespace(play=lambda *a, **k: played.append(a)),
    )

    with pytest.raises(LookupError):
        manim_mesh.stretch(2.0, dim=3)
    with pytest.raises(InvalidShapeException):
        manim_mesh.move_vertices_to(SimpleNamespace(), np.zeros((1, 3)))
    with pytest.raises(InvalidMeshDimensionsException):
        manim_mesh.move_vertex_to(SimpleNamespace(), 0, np.zeros(2))

    with pytest.raises(InvalidMeshException):
        Manim2DMesh(Mesh([[0, 0, 1], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]]))

    assert played


def test_svg_public_paths_and_gradient():
    gradient = VMobject().set_stroke(color=[RED, RED])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10)
    ctx = cairo.Context(surface)
    _set_cairo_context_color(ctx, gradient.get_stroke_rgbas(), gradient)

    from manim import VGroup

    from manim_extensions.mobject_svg.svg import create_svg_from_vgroup

    assert create_svg_from_vgroup(VGroup()) is not None


def test_molecule_wrapper_delegates():
    from manim_extensions.chemistry.molecule.molecule import Molecule

    class FakeMolecule:
        @staticmethod
        def molecule_from_file(*args, **kwargs):
            return ("file", args, kwargs)

        @staticmethod
        def multiple_molecules_from_file(*args, **kwargs):
            return ("files", args, kwargs)

        @staticmethod
        def molecule_from_string(*args, **kwargs):
            return ("string", args, kwargs)

        @staticmethod
        def multiple_molecules_from_string(*args, **kwargs):
            return ("strings", args, kwargs)

        @staticmethod
        def molecule_from_pubchem(*args, **kwargs):
            return ("pubchem", args, kwargs)

        @staticmethod
        def mc_molecule_to_atoms_and_bonds(*args, **kwargs):
            return ("atoms", args, kwargs)

    wrapper = Molecule(FakeMolecule)
    assert wrapper.molecule_from_file("a")[0] == "file"
    assert wrapper.multiple_molecules_from_file("a")[0] == "files"
    assert wrapper.molecule_from_string("a")[0] == "string"
    assert wrapper.multiple_molecules_from_string("a")[0] == "strings"
    assert wrapper.molecule_from_pubchem("a")[0] == "pubchem"
    assert wrapper.mc_molecule_to_atoms_and_bonds("a")[0] == "atoms"


def test_sequence_action_self_target_branch():
    from manim_extensions.sequence_diagram.seq_action import SeqAction
    from manim_extensions.sequence_diagram.seq_actor import SeqActor
    from manim_extensions.sequence_diagram.seq_object import SeqObject

    alice = SeqActor("Alice")
    gift = SeqObject("Gift")
    animations = list(SeqAction.subject_gives_gift_to_target(alice, gift, alice))

    assert animations


def test_rubikscube_grouped_sorting_install_and_idempotence():
    import manim_extensions.rubikscube as rubik
    from manim.camera.three_d_camera import ThreeDCamera

    original = ThreeDCamera.get_mobjects_to_display
    had_flag = getattr(ThreeDCamera, "_manim_extensions_grouped_z_key", False)
    try:
        ThreeDCamera._manim_extensions_grouped_z_key = False
        ThreeDCamera.get_mobjects_to_display = lambda self, *a, **k: []
        rubik._install_grouped_depth_sorting()
        rubik._install_grouped_depth_sorting()
        assert ThreeDCamera._manim_extensions_grouped_z_key is True
    finally:
        ThreeDCamera.get_mobjects_to_display = original
        if not had_flag:
            ThreeDCamera._manim_extensions_grouped_z_key = had_flag
