# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for QR code generation, mesh templates and sequence actors."""

import pytest
from manim import Circle

from manim_extensions.meshes import templates
from manim_extensions.qr_codes.qr import qr_code
from manim_extensions.sequence_diagram.seq_actor import SeqActor


def test_qr_code_returns_a_group():
    code = qr_code("hello")

    assert len(code.submobjects) == 2


def test_cube_template_returns_a_mesh():
    cube = templates.create_cube()

    assert cube is not None


def test_pyramid_template_returns_a_mesh():
    pyramid = templates.create_pyramid()

    assert pyramid is not None


def test_create_model_requires_a_name_or_path():
    with pytest.raises(FileNotFoundError):
        templates.create_model()


def test_seq_actor_can_advance_time():
    actor = SeqActor("Alice")

    actor.time_elapse(1.0)

    assert actor is not None
