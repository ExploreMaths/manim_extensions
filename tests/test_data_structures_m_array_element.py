# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the array element mobject."""

import pytest
from manim import Scene, Square

from manim_extensions.data_structures.m_array import MArrayElement


@pytest.fixture(scope="module")
def scene():
    return Scene()


def test_defaults(scene):
    element = MArrayElement(scene)

    assert element.fetch_mob_square() is not None


def test_fetch_helpers(scene):
    element = MArrayElement(scene)

    assert isinstance(element.fetch_mob_square(), Square)
    assert element.fetch_mob_value() is not None
    assert element.fetch_mob_index() is not None


def test_fetch_mob_selector(scene):
    element = MArrayElement(scene)

    assert element.fetch_mob(None) is not None


def test_chained_elements(scene):
    first = MArrayElement(scene)
    second = MArrayElement(scene, next_to_mob=first)

    assert second.get_center() is not None
