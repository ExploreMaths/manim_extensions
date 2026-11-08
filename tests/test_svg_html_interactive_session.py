# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for starting the interactive HTML playback session."""

import numpy as np
import pytest
from manim import Circle, Scene, ValueTracker

from manim_extensions.svg_animations.html_parsed_vmobject import HTMLParsedVMobject


@pytest.fixture()
def html_vmobject(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return HTMLParsedVMobject(Circle(), Scene())


@pytest.mark.parametrize("animate_this", [True, False])
def test_start_interactive_writes_files(html_vmobject, tmp_path, animate_this):
    tracker = ValueTracker(0.0)

    html_vmobject.start_interactive(
        [tracker], [np.linspace(0, 1, 5)], animate_this=animate_this
    )

    assert html_vmobject is not None
