# SPDX-FileCopyrightText: 2023 Naveen M K
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: add the module docstring and SPDX header
# patched: reflow the docstring and the rich-display lambdas

"""SVG export helpers for manim mobjects.

Exports :func:`~manim_extensions.mobject_svg.svg.create_svg_from_vmobject`
and :func:`~manim_extensions.mobject_svg.svg.create_svg_from_vgroup`, and
registers them on manim's classes as a ``to_svg()`` method on ``VMobject``
and ``VGroup``, so any mobject can be written to an SVG file.

The upstream package is pure Python and only depends on ``pycairo``, which
manim already requires, so it is vendored here instead of being declared as
a runtime dependency.
"""

from manim import VGroup, VMobject

from .svg import create_svg_from_vgroup, create_svg_from_vmobject

__all__ = ["create_svg_from_vgroup", "create_svg_from_vmobject"]

VMobject.to_svg = create_svg_from_vmobject  # type: ignore[attr-defined]
VGroup.to_svg = create_svg_from_vgroup  # type: ignore[attr-defined]

# Rich display for manim objects in Jupyter notebooks.
VMobject._repr_svg_ = (  # type: ignore[attr-defined]
    lambda self: create_svg_from_vmobject(self).read_text()
)
VGroup._repr_svg_ = (  # type: ignore[attr-defined]
    lambda self: create_svg_from_vgroup(self).read_text()
)
