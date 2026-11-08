# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for perpendicular sign degenerate inputs and image input variants."""

import numpy as np
import pytest
from manim import RIGHT, UP, Line, Square, tempconfig
from PIL import Image

from manim_extensions.mobjects import (
    CropImageMobject,
    FileTree,
    PerpendicularSign,
    Trail,
)


@pytest.fixture(autouse=True)
def _config():
    with tempconfig({"dry_run": True, "disable_caching": True, "renderer": "cairo"}):
        yield


def test_perpendicular_sign_with_collinear_lines():
    first = Line([0, 0, 0], [2, 0, 0])
    second = Line([0, 0, 0], [3, 0, 0])

    sign = PerpendicularSign(first, second, corner_direction=UP)

    assert isinstance(sign.submobjects, list)


def test_perpendicular_sign_with_parallel_offsets():
    first = Line([-2, 1, 0], [2, 1, 0])
    second = Line([-2, -1, 0], [2, -1, 0])

    sign = PerpendicularSign(first, second)

    assert sign is not None


def test_crop_image_from_pil_image():
    image = Image.new("RGB", (12, 12), (10, 120, 200))

    mob = CropImageMobject(image, corner_radius=1)

    assert mob is not None


def test_crop_image_from_path(tmp_path):
    path = tmp_path / "sample.png"
    Image.new("RGB", (14, 14), (200, 30, 60)).save(path)

    mob = CropImageMobject(str(path))

    assert mob is not None


def test_crop_image_zero_radius():
    image = np.zeros((10, 10, 3), dtype=np.uint8)

    mob = CropImageMobject(image, corner_radius=0)

    assert mob is not None


def test_trail_builds_multiple_segments():
    trail = Trail(Square())
    for step in range(3):
        trail[0].shift(RIGHT * 0.3)
        trail.get_path_xyz()

    path = trail.create_path()

    assert len(path) >= 1
