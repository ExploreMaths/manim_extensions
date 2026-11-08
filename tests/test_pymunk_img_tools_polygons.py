# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for collision polygon extraction from pixel arrays."""

import numpy as np

from manim_extensions.pymunk.utils.img_tools import (
    get_normalized_convex_polygons,
    map_polygons_to_manim,
)


def _opaque_square(size=64, start=16, stop=48):
    image = np.zeros((size, size, 3), dtype=np.uint8)
    image[start:stop, start:stop] = 255
    return image


def test_solid_image_yields_convex_polygons():
    polygons = get_normalized_convex_polygons(_opaque_square())

    assert len(polygons) >= 1
    assert all(len(polygon) >= 3 for polygon in polygons)


def test_transparent_image_yields_convex_polygons():
    rgba = np.zeros((64, 64, 4), dtype=np.uint8)
    rgba[20:44, 20:44] = (255, 0, 0, 255)

    polygons = get_normalized_convex_polygons(rgba)

    assert len(polygons) >= 1


def test_empty_image_yields_no_polygons():
    assert get_normalized_convex_polygons(np.zeros((32, 32, 3), dtype=np.uint8)) == []


def test_polygons_are_mapped_into_manim_coordinates():
    polygons = [[[[10.0, 10.0], [30.0, 10.0], [30.0, 30.0]]]]

    mapped = map_polygons_to_manim(polygons[0], 64, 64, 8.0, 8.0)

    assert len(mapped) == 1
    assert len(mapped[0]) == 3
    assert mapped[0][0][0] < mapped[0][1][0]
