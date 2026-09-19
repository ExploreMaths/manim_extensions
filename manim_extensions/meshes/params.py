# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import moderngl (meshes extra)


"""
Parameters can get out of hand for the meshes, store defaults and casting in separate functions
"""

from manim import ManimColor

# python imports
from typing import Any

# third-party imports
import manim as m

# local imports
from .exceptions import BadParameterException
from .types import DefaultParameters, Parameters

from ..utils.deps import require

# map from param name to type and default value

# basic_manim_3d_mesh_default_params
BM3DM: DefaultParameters = {
    "display_vertices": (bool, False),
    "display_edges": (bool, True),
    "display_faces": (bool, True),
    "clear_vertices": (bool, True),
    "clear_edges": (bool, True),
    "clear_faces": (bool, True),
    "edges_color": (ManimColor, ManimColor(m.BLUE)),
    "edges_width": (float, 0.1),
    "faces_color": (ManimColor, ManimColor(m.BLUE_D)),
    "faces_opacity": (float, 0.4),
    "verts_color": (ManimColor, ManimColor(m.GREEN)),
    "verts_size": (float, 0.04),
    "pre_function_handle_to_anchor_scale_factor": (float, 0.00001),
}

# basic_manim_2d_mesh_default_params
BM2DM: DefaultParameters = {
    "display_vertices": (bool, False),
    "display_edges": (bool, True),
    "display_faces": (bool, True),
    "clear_vertices": (bool, True),
    "clear_edges": (bool, True),
    "clear_faces": (bool, True),
    "edges_color": (ManimColor, ManimColor(m.LIGHT_GREY)),
    "edges_width": (float, 1.5),
    "faces_color": (ManimColor, ManimColor(m.BLUE_E)),
    "faces_opacity": (float, 1.0),
    "verts_color": (ManimColor, ManimColor(m.GREEN)),
    "verts_size": (float, 0.02),
    "pre_function_handle_to_anchor_scale_factor": (float, 0.00001),
}

# opengl_mesh_default_params
# OGLM is built lazily (see __getattr__ below): it defaults
# ``render_primitive`` to ``moderngl.TRIANGLES``, so building it at import
# time would require the optional "meshes" extra just to import this module.
def _build_oglm() -> DefaultParameters:
    moderngl = require("meshes", "moderngl")
    return {
        "color": (ManimColor, ManimColor(m.GREY)),
        "depth_test": (bool, True),
        "gloss": (float, 0.3),
        "opacity": (float, 1.0),
        "render_primitive": (int, moderngl.TRIANGLES),
        "shadow": (float, 0.4),
    }


def __getattr__(name: str) -> Any:
    # PEP 562: build OGLM on first attribute access so that importing this
    # module does not require the optional moderngl dependency.
    if name == "OGLM":
        return _build_oglm()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_param_or_default(
    value: str, params: Parameters, default: DefaultParameters
) -> Any:
    """Return the user-supplied parameter or its default value.

    If *params* contains *value*, the value is cast to the expected type
    defined in *default* (when possible).  Otherwise the default value is
    returned.

    Parameters
    ----------
    value : str
        The parameter name to look up.
    params : Parameters
        Dictionary of user-supplied parameters (may be ``None``).
    default : DefaultParameters
        Dictionary mapping parameter names to ``(type, default_value)`` tuples.

    Returns
    -------
    Any
        The resolved parameter value.

    Raises
    ------
    BadParameterException
        If *value* is not found in either *params* or *default*, or if the
        supplied value cannot be cast to the expected type.
    """
    # get value from user given parameters
    if params and value in params:
        if value in default:
            if issubclass(type(params[value]), default[value][0]) or isinstance(
                type(params[value]), default[value][0]
            ):
                return params[value]
            try:
                return default[value][0](params[value])
            except (ValueError, TypeError) as e:
                raise BadParameterException(
                    f"Value {value} does not have correct type "
                    f"{default[value][0]} and can not be cast."
                ) from e
        raise BadParameterException(f"Value {value} is not an expected default value.")
    # get value from default parameters
    if value in default:
        return default[value][1]
    # should this be raised?
    raise BadParameterException(
        f"Value {value} is not in params and not in default params."
    )