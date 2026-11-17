# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Coverage for small, deterministic branches that need no rendering."""

import importlib

import numpy as np
import pytest
from manim import Circle, LEFT, Line, RIGHT

from manim_extensions.algorithm.array import Array
from manim_extensions.algorithm.queue import Queue
from manim_extensions.geometry import tangent_point
from manim_extensions.scenes import ConstantStrokeWidthScene
from manim_extensions.table import Cell, Table


def test_table_requires_data_or_header():
    with pytest.raises(ValueError, match="either"):
        Table()


def test_header_only_table_uses_fixed_cell_width():
    table = Table(header=["A", "B"], auto_fit=False)
    assert table.column_widths == [table.cell_width, table.cell_width]


def test_header_only_table_accessors_and_first_data_row():
    table = Table(header=["A", "B"])
    assert table.get_cell(0, 0).get_value() == "A"
    assert table.get_row(0) is table.header_row
    assert table.get_column_by_name("B") is not None
    assert table.get_header_names() == ["A", "B"]
    assert len(table) == 0
    assert table[:] == []

    row, animations = table.add_row(["X", "Y"])
    assert row[0].get_value() == "X"
    assert animations


def test_table_column_lookup_and_delete_errors():
    table = Table([["A", "B"], ["1", "2"], ["3", "4"]])
    assert table.get_cell(1, 0).get_value() == "1"
    assert table.get_row(1)[0].get_value() == "1"
    assert table.get_column(1) is not None
    assert table[1:]
    with pytest.raises(ValueError, match="not found"):
        table.get_column_by_name("C")
    with pytest.raises(IndexError, match="out of range"):
        table.delete_column(2)


def test_table_column_setters_include_header():
    table = Table([["A", "B"], ["1", "2"]])
    table.set_column_font_color(1, "red", include_header=True)
    table.set_column_background_color(1, "blue", include_header=True)


def test_cell_without_border_resize_and_styled_copy():
    cell = Cell("old", width=1.0, show_border=False)
    assert cell.border is None

    cell.set_font_color("red")
    cell.set_border_color("green")
    cell.set_background_color("blue", opacity=0.2)
    cell.set_background_color("yellow", opacity=0.4)
    cell.resize_width(2.0)

    copy = cell.get_resized_copy(3.0)
    assert copy.get_value() == "old"
    assert copy.cell_width == 3.0

    bordered = Cell("bordered")
    bordered.resize_width(2.0)
    bordered.set_border_color("green")

    header = Cell("old", is_header=True)
    assert header.set_value("new").text == "new"
    assert Cell("old").set_value("new").text == "new"

    scaled = Cell("scaled")
    scaled.scale(2.0)
    assert scaled.get_resized_copy(1.0) is not None


def test_constant_stroke_scene_constructor_keyword_and_camera_fallbacks():
    scene = ConstantStrokeWidthScene()

    fixed = Line(LEFT, RIGHT, fixed_stroke_width=True)
    assert fixed.fixed_stroke_width is True

    class NoHeightCamera:
        frame_height = None
        get_height = None

    class ZeroHeightCamera:
        frame_height = 0.0

    from types import SimpleNamespace

    no_height = SimpleNamespace(camera=NoHeightCamera())
    zero_height = SimpleNamespace(camera=ZeroHeightCamera())
    assert ConstantStrokeWidthScene._camera_stroke_scale(no_height) == 1.0
    assert ConstantStrokeWidthScene._camera_stroke_scale(zero_height) == 1.0


def test_constant_stroke_scene_update_and_add_scale_paths(monkeypatch):
    scene = ConstantStrokeWidthScene()
    circle = Circle(stroke_width=2.0)
    scene._stroke_scale = 1.0
    monkeypatch.setattr(scene, "_camera_stroke_scale", lambda: 2.0)
    scene.add(circle)
    assert circle.stroke_width == 4.0

    scene._stroke_scale = 1.0
    scene._update_stroke_scale(0.0)
    assert circle.stroke_width == 8.0
    scene._update_stroke_scale(0.0)


def test_constant_stroke_width_skips_fixed_and_in_frame_mobjects():
    class Fixed:
        is_fixed_in_frame = 0.0
        fixed_stroke_width = True
        stroke_width = 2.0

    class InFrame:
        is_fixed_in_frame = 1.0
        fixed_stroke_width = False
        stroke_width = 2.0

    class NoStroke:
        is_fixed_in_frame = 0.0
        fixed_stroke_width = False
        stroke_width = None

    ConstantStrokeWidthScene._scale_stroke_width(Fixed(), 2.0)
    ConstantStrokeWidthScene._scale_stroke_width(InFrame(), 2.0)
    ConstantStrokeWidthScene._scale_stroke_width(NoStroke(), 2.0)


def test_constant_stroke_scene_uses_camera_get_height():
    from types import SimpleNamespace

    class HeightCamera:
        frame_height = None

        @staticmethod
        def get_height():
            return 2.0

    holder = SimpleNamespace(camera=HeightCamera())
    assert ConstantStrokeWidthScene._camera_stroke_scale(holder) > 0.0


def test_require_reports_missing_extra():
    with pytest.raises(ImportError, match=r"manim_extensions\[physics\]"):
        importlib.import_module("manim_extensions.utils.deps").require(
            "physics", "_definitely_missing_manim_extensions_dependency"
        )


def test_require_returns_single_and_multiple_modules():
    import json
    import math

    deps = importlib.import_module("manim_extensions.utils.deps")
    assert deps.require("core", "json") is json
    assert deps.require("core", "json", "math") == (json, math)


def test_array_slice_returns_array():
    array = Array([1, 2, 3])
    sliced = array[1:]
    assert isinstance(sliced, Array)
    assert [node.value for node in sliced.values] == [2, 3]


def test_dequeue_on_empty_queue_is_a_noop():
    queue = Queue(capacity=3, init_data=[])
    Queue.Dequeue(queue)
    assert queue.data == []


def test_tangent_point_degenerate_line_with_unequal_distances():
    assert tangent_point([0, 0], [2, 0], [0, 2], [0, 2]) is None


def test_tangent_point_vertical_pair_uses_non_z_up_axis():
    point = tangent_point([0, 0, 0], [0, 0, 2], [1, 0, 0], [-1, 0, 0])
    assert point is None or np.asarray(point).shape == (3,)


def test_rubikscube_module_entry_point(capsys):
    from manim_extensions.rubikscube.__main__ import main

    main()
    assert "Manim Rubik's Cube" in capsys.readouterr().out


def test_nerdfont_icon_accepts_named_and_raw_values():
    from manim_extensions.nerdfont.icons import NerdFontIcon

    assert NerdFontIcon("heart").text
    assert NerdFontIcon("not-a-known-icon").text == "not-a-known-icon"
    assert NerdFontIcon(1).text


def test_qr_code_with_center_icon():
    pytest.importorskip("segno")
    from manim_extensions.qr_codes import qr_code

    result = qr_code("icon", icon="heart", icon_size=4)
    assert result is not None
