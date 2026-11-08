# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the trail, file tree and cropped image mobjects."""

import numpy as np
import pytest
from manim import RIGHT, Dot, Square, tempconfig

from manim_extensions.mobjects import CropImageMobject, FileTree, LabelDot, Trail


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_label_dot_boundary_point():
    label = LabelDot("x", RIGHT * 2)

    point = label.get_boundary_point(RIGHT)

    assert point is not None


def test_file_tree_highlights_line():
    tree = FileTree({"src": {"main.py": None}})

    animation = tree.highlight(0)

    assert animation is not None


def test_file_tree_rejects_empty_tree():
    tree = FileTree({"a.py": None})
    tree.submobjects.clear()

    with pytest.raises(ValueError):
        tree.highlight(0)


def test_file_tree_rejects_out_of_range_line():
    tree = FileTree({"a.py": None})

    with pytest.raises(ValueError):
        tree.highlight(99)


def test_crop_image_accepts_numpy_array():
    image = np.zeros((16, 16, 3), dtype=np.uint8)

    mob = CropImageMobject(image, corner_radius=0.2)

    assert mob is not None


def test_trail_records_path():
    trail = Trail(Square())

    trail.get_path_xyz()
    trail[0].shift([0.5, 0, 0])
    trail.get_path_xyz()
    trail.create_path()

    assert len(trail.path_xyz) >= 1


def test_trail_trims_old_points():
    trail = Trail(Square(), nums=1)

    for step in range(4):
        trail[0].shift([0.2, 0, 0])
        trail.get_path_xyz()

    assert len(trail.path_xyz) <= 1
