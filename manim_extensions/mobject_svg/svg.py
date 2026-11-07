# SPDX-FileCopyrightText: 2023 Naveen M K
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: add the module docstring and SPDX header
# patched: document the module-level constant and the cairo context helpers
# patched: type the cairo context helpers and replace tempfile.mktemp

"""Render manim mobjects into SVG files through a Cairo surface.

Vendored from ``manim-mobject-svg`` 0.5.0. The public entry points are
:func:`~manim_extensions.mobject_svg.svg.create_svg_from_vmobject` and
:func:`~manim_extensions.mobject_svg.svg.create_svg_from_vgroup`; the
module-level helpers mirror the upstream implementation so relative
subpaths, gradients and stroke/fill ordering keep working.
"""

from __future__ import annotations

import itertools as it
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import cairo
import numpy as np
from manim import VGroup, VMobject
from manim.utils.family import extract_mobject_family_members

#: Multiplier applied to manim stroke widths when drawing into the Cairo surface.
CAIRO_LINE_WIDTH_MULTIPLE: float = 0.01

__all__ = ["create_svg_from_vmobject", "create_svg_from_vgroup"]


@contextmanager
def _get_cairo_context(
    file_name: str | Path,
    width: int | None = None,
    height: int | None = None,
) -> Iterator[cairo.Context]:
    """Yield a Cairo SVG context scaled to the current manim frame.

    Parameters
    ----------
    file_name
        Path of the SVG file that the context writes to.
    width
        Optional cropped width in manim units; falls back to the frame width.
    height
        Optional cropped height in manim units; falls back to the frame height.
    """
    from manim import config

    pw = config.pixel_width
    ph = config.pixel_height
    fw = config.frame_width
    fh = config.frame_height
    if width and height:
        pw = int(width * pw / fw)
        ph = int(height * ph / fh)
        fw = width
        fh = height

    fc = [0, 0]
    surface = cairo.SVGSurface(
        file_name,
        pw,
        ph,
    )
    ctx = cairo.Context(surface)
    ctx.scale(pw, ph)
    ctx.set_matrix(
        cairo.Matrix(
            (pw / fw),
            0,
            0,
            -(ph / fh),
            (pw / 2) - fc[0] * (pw / fw),
            (ph / 2) + fc[1] * (ph / fh),
        ),
    )
    yield ctx
    surface.finish()


def _transform_points_pre_display(points: np.ndarray) -> np.ndarray:
    """Return display-ready points, replacing non-finite values with zeros.

    Parameters
    ----------
    points
        The points to validate, as an ``(n, 3)`` array.

    Returns
    -------
        The original points, or a single zero point when any coordinate is
        NaN or infinite and therefore cannot be drawn.
    """
    if not np.all(np.isfinite(points)):
        points = np.zeros((1, 3))
    return points


def _get_stroke_rgbas(vmobject: VMobject, background: bool = False) -> np.ndarray:
    """Return the stroke rgbas used by ``vmobject``.

    Parameters
    ----------
    vmobject
        The mobject whose stroke is read.
    background
        Read the background stroke instead of the foreground stroke.

    Returns
    -------
        One rgba per stroke point, as returned by manim.
    """
    return vmobject.get_stroke_rgbas(background)


def _set_cairo_context_color(
    ctx: cairo.Context,
    rgbas: np.ndarray,
    vmobject: VMobject,
):
    """Set the cairo source to a solid colour or a stroke gradient.

    Parameters
    ----------
    ctx
        The cairo context to update.
    rgbas
        One rgba per stroke or fill point.
    vmobject
        The mobject that provides the gradient start and end points.
    """
    if len(rgbas) == 1:
        # Use reversed rgb because cairo surface is
        # encodes it in reverse order
        ctx.set_source_rgba(*rgbas[0])
    else:
        points = vmobject.get_gradient_start_and_end_points()
        points = _transform_points_pre_display(points)
        pat = cairo.LinearGradient(*it.chain(*(point[:2] for point in points)))
        step = 1.0 / (len(rgbas) - 1)
        offsets = np.arange(0, 1 + step, step)
        for rgba, offset in zip(rgbas, offsets):
            pat.add_color_stop_rgba(offset, *rgba)
        ctx.set_source(pat)


def _apply_stroke(ctx: cairo.Context, vmobject: VMobject, background: bool = False):
    """Stroke the current cairo path with the mobject's stroke colour.

    Parameters
    ----------
    ctx
        The cairo context to draw into.
    vmobject
        The mobject whose stroke width and rgbas are applied.
    background
        Stroke with the background stroke instead of the foreground one.
    """
    from manim import config

    width = vmobject.get_stroke_width(background)
    if width == 0:
        return
    _set_cairo_context_color(
        ctx,
        _get_stroke_rgbas(vmobject, background=background),
        vmobject,
    )
    ctx.set_line_width(
        width
        * CAIRO_LINE_WIDTH_MULTIPLE
        # This ensures lines have constant width as you zoom in on them.
        * (config.frame_width / config.frame_width),
    )
    # if vmobject.joint_type != LineJointType.AUTO:
    #     ctx.set_line_join(LINE_JOIN_MAP[vmobject.joint_type])
    ctx.stroke_preserve()


def _apply_fill(ctx: cairo.Context, vmobject: VMobject):
    """Fill the current cairo path with the vmobject's fill colours.

    Parameters
    ----------
    ctx
        The cairo context to draw into.
    vmobject
        The vmobject whose fill rgbas are applied.
    """
    _set_cairo_context_color(
        ctx,
        vmobject.get_fill_rgbas(),
        vmobject,
    )
    ctx.fill_preserve()


def _temporary_svg_path() -> Path:
    """Return a unique temporary path for an SVG file.

    Returns
    -------
        A path in the system temporary directory. The file already exists
        and is overwritten when the caller writes the SVG.
    """
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as handle:
        return Path(handle.name)


def _create_svg_from_vmobject_internal(
    vmobject: VMobject, ctx: cairo.Context
):
    """Draw one mobject into the current cairo context.

    Parameters
    ----------
    vmobject
        The mobject to draw.
    ctx
        The cairo context that receives the drawing.
    """
    # Drop non-finite points before building the path.
    points = vmobject.points
    points = _transform_points_pre_display(points)
    if len(points) == 0:
        return
    ctx.new_path()
    subpaths = vmobject.gen_subpaths_from_points_2d(points)
    for subpath in subpaths:
        quads = vmobject.gen_cubic_bezier_tuples_from_points(subpath)
        ctx.new_sub_path()
        start = subpath[0]
        ctx.move_to(*start[:2])
        for _p0, p1, p2, p3 in quads:
            ctx.curve_to(*p1[:2], *p2[:2], *p3[:2])
        if vmobject.consider_points_equals_2d(subpath[0], subpath[-1]):
            ctx.close_path()

    _apply_stroke(ctx, vmobject, background=True)
    _apply_fill(ctx, vmobject)
    _apply_stroke(ctx, vmobject)


def create_svg_from_vmobject(
    vmobject: VMobject,
    file_name: str | Path | None = None,
    *,
    crop: bool = True,
    padding: float = 0.05,
) -> Path:
    """Create an SVG file from a VMobject.

    Parameters
    ----------
    vmobject
        The VMobject to render.
    file_name
        Path of the SVG file; a temporary file is created when omitted.
    crop
        Whether to crop the SVG to the VMobject's size.
    padding
        Padding added around the crop, in manim units.

    Returns
    -------
        The path of the written SVG file.
    """
    if file_name is None:
        file_name = _temporary_svg_path()
    file_name = Path(file_name).absolute()
    width, height = None, None
    if crop:
        width, height = vmobject.width + padding, vmobject.height + padding
    with _get_cairo_context(file_name, width=width, height=height) as ctx:
        for _vmobject in extract_mobject_family_members([vmobject], True, True):
            _create_svg_from_vmobject_internal(_vmobject, ctx)
    return file_name


def create_svg_from_vgroup(
    vgroup: VGroup,
    file_name: str | Path | None = None,
    *,
    crop: bool = True,
    padding: float = 0.05,
) -> Path:
    """Create an SVG file from a VGroup.

    Parameters
    ----------
    vgroup
        The VGroup to render.
    file_name
        Path of the SVG file; a temporary file is created when omitted.
    crop
        Whether to crop the SVG to the VGroup's size.
    padding
        Padding added around the crop, in manim units.

    Returns
    -------
        The path of the written SVG file.
    """
    if file_name is None:
        file_name = _temporary_svg_path()
    file_name = Path(file_name).absolute()
    width, height = None, None
    if crop:
        width, height = vgroup.width + padding, vgroup.height + padding
    with _get_cairo_context(file_name, width=width, height=height) as ctx:
        # a vgroup is a list of VMobjects which may contain other VGroups
        # flatten the vgroup to get a list of VMobjects
        vgroup = extract_mobject_family_members(vgroup, True, True)
        for vmobject in vgroup:
            _create_svg_from_vmobject_internal(vmobject, ctx)
    return file_name
