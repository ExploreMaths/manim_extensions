# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for mesh validation, decorators and parameter fallbacks."""

import numpy as np
import pytest

from manim_extensions.meshes.decorators import (
    dangling_face_decorator,
    dangling_vert_decorator,
)
from manim_extensions.meshes.exceptions import (
    BadParameterException,
    InvalidShapeException,
    MeshIndexException,
)
from manim_extensions.meshes.models.data_models.mesh import Mesh
from manim_extensions.meshes.params import get_param_or_default


class _Sequence:
    """A nested sequence that is not a list, tuple or ndarray."""

    def __init__(self, values):
        self.values = values

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        return self.values[index]

    def __iter__(self):
        return iter(self.values)


def build_mesh():
    return Mesh(
        [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]],
        [[0, 1, 2], [1, 3, 2]],
        [[0, 1]],
    )


def test_add_parts_accepts_tuple():
    mesh = build_mesh()
    mesh.add_parts((np.array([0, 1]),))

    assert len(mesh.parts) == 2


def test_concatenate_rejects_out_of_bounds_face_and_part():
    first = build_mesh()
    second = build_mesh()
    second._faces = [np.array([99, 0, 1])]
    with pytest.raises(MeshIndexException, match="face index is out of bounds"):
        first.add_to_mesh(second)

    third = build_mesh()
    third._parts = [np.array([99])]
    with pytest.raises(MeshIndexException, match="part index is out of bounds"):
        build_mesh().add_to_mesh(third)


def test_decorators_warn_on_dangling_geometry():
    class FakeMesh:
        test_for_dangling = True

        def dangling_vert_check(self):
            return True

        def dangling_face_check(self):
            return True

    @dangling_vert_decorator()
    def mutate(mesh):
        return 1

    @dangling_face_decorator()
    def mutate_face(mesh):
        return 2

    with pytest.warns(UserWarning, match="Dangling vertices"):
        assert mutate(FakeMesh()) == 1
    with pytest.warns(UserWarning, match="Dangling faces"):
        assert mutate_face(FakeMesh()) == 2


def test_bad_parameter_messages():
    with pytest.raises(BadParameterException, match="does not have correct type"):
        get_param_or_default("width", {"width": "bad"}, {"width": (float, 1.0)})
    with pytest.raises(BadParameterException, match="not an expected default value"):
        get_param_or_default("height", {"height": 1}, {"width": (int, 1)})
    with pytest.raises(BadParameterException, match="not in params and not in default"):
        get_param_or_default("missing", {}, {})


def test_get_param_or_default_casts_and_falls_back():
    assert get_param_or_default("width", {"width": "2"}, {"width": (float, 1.0)}) == 2.0
    assert get_param_or_default("width", {}, {"width": (float, 1.0)}) == 1.0


def test_shape_exception_message():
    error = InvalidShapeException("vertices", 2, 3)

    assert str(error) == "Size of vertices is expected to be 3 but was 2."
