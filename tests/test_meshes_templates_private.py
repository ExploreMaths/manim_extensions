# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

import pytest

from manim_extensions.meshes.exceptions import InvalidRequestException
from manim_extensions.meshes.templates import (
    create_cube,
    create_grid,
    create_model,
    create_pyramid,
)


def test_pyramid_with_quad_base():
    mesh = create_pyramid(triangles_only=False)
    assert mesh.faces is not None


def test_cube_with_quad_faces():
    mesh = create_cube(triangles_only=False)
    assert mesh.faces is not None


def test_grid_rejects_dimensions_above_four():
    with pytest.raises(InvalidRequestException):
        create_grid([(0.0, 1.0, 2)] * 5)


def test_create_model_requires_name_or_path():
    with pytest.raises(FileNotFoundError):
        create_model()


def test_create_model_rejects_unknown_name(monkeypatch):
    import manim_extensions.meshes.templates as module

    monkeypatch.setattr(module, "require", lambda group, name: object())
    with pytest.raises(FileNotFoundError, match="not a valid"):
        create_model(name="missing-model")
