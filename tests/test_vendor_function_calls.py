# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Module level helpers called with their simplest literal argument."""

import importlib

import numpy as np
import pytest
from manim import Circle, Line

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

CASES = [
    ("manim_extensions.animations:easeInBounce", (1,)),
    ("manim_extensions.animations:easeInOutBounce", (1,)),
    ("manim_extensions.animations:easeOutBounce", (1,)),
    ("manim_extensions.animations:easeOutElastic", (1,)),
    (
        "manim_extensions.chemistry.future_classes.future_classes:add_over_rectangular_surface",
        (),
    ),
    ("manim_extensions.chemistry.future_classes.future_classes:inverse_linear", (1,)),
    ("manim_extensions.chemistry.future_classes.future_classes:inverse_smooth", (1,)),
    ("manim_extensions.chemistry.future_classes.future_classes:zero", (1,)),
    ("manim_extensions.fontawesome.manim_fontawesome:list_icons", ()),
    (
        "manim_extensions.machine_learning.diffusion.mcmc:gaussian_proposal",
        (np.array([0.0, 0.0, 0.0]),),
    ),
    (
        "manim_extensions.machine_learning.diffusion.mcmc:metropolis_hastings_sampler",
        (),
    ),
    ("manim_extensions.meshes.decorators:dangling_face_decorator", ()),
    ("manim_extensions.meshes.decorators:dangling_vert_decorator", ()),
    ("manim_extensions.meshes.helpers:is_twice_nested_iterable", (1,)),
    ("manim_extensions.meshes.templates:create_coplanar_points", ()),
    ("manim_extensions.meshes.templates:create_coplanar_triangles", ()),
    ("manim_extensions.meshes.templates:create_cube", ()),
    ("manim_extensions.meshes.templates:create_pyramid", ()),
    ("manim_extensions.meshes.templates:create_triangle", ()),
    ("manim_extensions.mindmap.algorithms.alg_standard:split_integer", (1,)),
    ("manim_extensions.mindmap.animations.animations:is_direction_change", (1,)),
    ("manim_extensions.mindmap.nodes.node:bfs_walker", (1,)),
    ("manim_extensions.mindmap.nodes.node:dfs_walker", (1,)),
    ("manim_extensions.physics.rigid_mechanics.rigid_mechanics:get_angle", (1,)),
    ("manim_extensions.qr_codes.qr:qr_code", (1,)),
    ("manim_extensions.rubikscube.cube_utils:get_axis_from_face", (1,)),
    ("manim_extensions.rubikscube.cube_utils:get_direction_from_face", (1,)),
    ("manim_extensions.utils.deprecation:deprecated", ("text",)),
    ("manim_extensions.utils.deps:require", (1,)),
]


@pytest.mark.parametrize("target,args", CASES, ids=[case[0] for case in CASES])
def test_module_function(target, args):
    module_name, _, func_name = target.rpartition(":")
    module = importlib.import_module(module_name)

    module.__dict__[func_name](*args)
