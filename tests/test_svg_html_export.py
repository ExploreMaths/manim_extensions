# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the HTML overlay exporter."""

import pytest
from manim import Scene, Square

from manim_extensions.svg_animations.html_parsed_vmobject import HTMLParsedVMobject


@pytest.fixture()
def scene():
    return Scene()


@pytest.fixture()
def exporter(scene, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return HTMLParsedVMobject(Square(), scene, basic_html=True)


def test_html_file_name_is_derived_from_scene(exporter):
    assert exporter.html_filename.endswith(".html")
    assert exporter.js_filename.endswith(".js")


def test_update_html_tracks_frame(exporter):
    exporter.update_html()

    assert exporter.continue_updating is True


def test_updater_advances_frame_index(exporter):
    exporter.updater(1.0)

    assert exporter.current_index >= 1


def test_finish_runs_without_error(exporter):
    exporter.finish()

    assert exporter.html_filename
