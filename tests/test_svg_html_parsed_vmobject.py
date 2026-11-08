# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for exporting an animating vmobject to HTML/JS."""

import os

import pytest
from manim import Circle, Scene

from manim_extensions.svg_animations.html_parsed_vmobject import HTMLParsedVMobject


@pytest.fixture()
def exporter(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    scene = Scene()
    circle = Circle()
    scene.add(circle)
    return HTMLParsedVMobject(circle, scene)


def test_exporter_initialises(exporter):
    assert exporter.filename_base == "Scene"
    assert exporter.html_filename == "Scene.html"


def test_updater_and_update_html(exporter):
    exporter.updater(0.1)
    exporter.update_html()

    assert exporter.js_updates != ""


def test_finish_writes_output_files(exporter, tmp_path):
    exporter.finish()

    assert len(list(tmp_path.iterdir())) >= 1
