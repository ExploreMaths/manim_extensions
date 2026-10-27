# SPDX-FileCopyrightText: 2021 KingWampy
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Rubik's Cube helpers and scene objects.

The module exposes the main cube model and related animation utilities for
visualising cube states in Manim scenes.

"""

from .cube import *
from .cube_animations import *


def _install_grouped_depth_sorting() -> None:
    """Enable grouped 3D depth sorting for Manim's ``ThreeDCamera``.

    Manim sorts 3D mobjects by a single per-mobject depth key (each mobject's own
    centre), which scatters the six faces of a cubie and causes the depth-order
    flicker (the "front/back jumping") visible while a cube rotates. Installing a
    grouped z-key -- primary = the mobject's ``z_index_group`` centre, secondary =
    its own centre -- keeps a cubie's faces moving together during rotation while
    still drawing them far-to-near (correct painter's algorithm). Mobjects without
    a ``z_index_group`` are unaffected, since the secondary key then equals the
    primary and the ordering matches Manim's original behaviour.
    """
    if getattr(ThreeDCamera, "_manim_extensions_grouped_z_key", False):
        return
    _orig = ThreeDCamera.get_mobjects_to_display

    def _grouped(self, *args, **kwargs):
        mobjects = _orig(self, *args, **kwargs)
        rot_matrix = self.get_rotation_matrix()

        def z_key(mob):
            if not (hasattr(mob, "shade_in_3d") and mob.shade_in_3d):
                return (np.inf, np.inf)
            primary = float(
                np.dot(mob.get_z_index_reference_point(), rot_matrix.T)[2]
            )
            secondary = float(np.dot(mob.get_center(), rot_matrix.T)[2])
            return (primary, secondary)

        return sorted(mobjects, key=z_key)

    ThreeDCamera.get_mobjects_to_display = _grouped
    ThreeDCamera._manim_extensions_grouped_z_key = True


try:
    from manim import np
    from manim.camera.three_d_camera import ThreeDCamera

    _install_grouped_depth_sorting()
except Exception:  # pragma: no cover - manim not installed
    pass


try:
    from importlib.metadata import version as _version
except ImportError:  # pragma: no cover
    from importlib_metadata import version as _version

try:
    __version__ = _version("manim_extensions.rubikscube")
except Exception:
    try:
        __version__ = _version("manim_extensions")
    except Exception:
        __version__ = "unknown"
