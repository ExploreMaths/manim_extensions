# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for economic diagram branches and compass geometry helpers."""

import numpy as np
import pytest
from manim import ORIGIN, RIGHT, PI, Arc

from manim_extensions.compass import Compass, PutCompass
from manim_extensions.compass.animations.animation_compass import MoveNiddleTipTo
from manim_extensions.compass.utils.geometry_method import ArcFromCenter
from manim_extensions.economics.linked import LinkedISLMADAS
from manim_extensions.economics.solow import SolowDiagram


def test_ArcFromCenter_matches_endpoints():
    arc = ArcFromCenter(ORIGIN, 2 * RIGHT, PI / 2)

    assert isinstance(arc, Arc)
    assert np.isclose(arc.radius, 2.0)


def test_put_compass_and_move_niddle_tip():
    compass = Compass()
    PutCompass(compass, ORIGIN, 2 * RIGHT)
    MoveNiddleTipTo(compass, 2 * RIGHT)


def test_put_compass_rejects_span_beyond_legs():
    compass = Compass()

    with pytest.raises(ValueError, match="span exceeds"):
        PutCompass(compass, ORIGIN, 10 * RIGHT)


def test_linked_diagrams_accept_forwarded_kwargs():
    linked = LinkedISLMADAS(
        is_lm_kwargs={"x_length": 5.0, "numbered_eq": True},
        ad_as_kwargs={"y_length": 2.5},
        spacing=2.0,
    )

    assert linked.is_lm is not None
    assert linked.ad_as is not None


def test_solow_show_shares_returns_none_without_steady_state(monkeypatch):
    diagram = SolowDiagram()
    monkeypatch.setattr(diagram, "_steady_state_k", lambda: None)

    assert diagram.show_shares() is None


def test_solow_show_shares_replaces_existing_group():
    diagram = SolowDiagram()
    diagram.show_shares(1.0)
    animation = diagram.show_shares(2.0)

    assert animation is not None
    assert animation.mobject is not None


def test_solow_share_updater_rebuilds_group():
    diagram = SolowDiagram()
    animation = diagram.animate_shares_along(0.2, 2.0)
    animation.interpolate(0.5)

    assert diagram._shares_group is not None
