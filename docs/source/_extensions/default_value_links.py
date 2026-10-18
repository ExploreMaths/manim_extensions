# SPDX-FileCopyrightText: 2026 ExploreMaths
#
# SPDX-License-Identifier: MIT

"""Link manim constant names in signature default values.

With ``autodoc_preserve_defaults`` enabled, autodoc renders defaults with
their source spelling (``color=WHITE`` instead of
``color=ManimColor('#FFFFFF')``) inside ``literal`` nodes carrying the
``default_value`` class.  Those names are plain text, so this extension
replaces the literal with a real reference to this project's Constants
pages (``constants/colors.html`` etc.), which carry the object anchors
collected by autodoc.
"""

from __future__ import annotations

import posixpath

from docutils import nodes
from sphinx.util.docutils import SphinxTranslator  # noqa: F401  (kept for parity)

_CONSTANT_PAGES: dict[str, str] = {
    # manim.constants names -> category page under docs/source/constants/
    "ORIGIN": "directions",
    "UP": "directions",
    "DOWN": "directions",
    "LEFT": "directions",
    "RIGHT": "directions",
    "IN": "directions",
    "OUT": "directions",
    "UL": "directions",
    "UR": "directions",
    "DL": "directions",
    "DR": "directions",
    "BOLD": "fonts",
    "BOOK": "fonts",
    "HEAVY": "fonts",
    "ITALIC": "fonts",
    "LIGHT": "fonts",
    "MEDIUM": "fonts",
    "NORMAL": "fonts",
    "OBLIQUE": "fonts",
    "SEMIBOLD": "fonts",
    "SEMILIGHT": "fonts",
    "THIN": "fonts",
    "ULTRABOLD": "fonts",
    "ULTRAHEAVY": "fonts",
    "ULTRALIGHT": "fonts",
    "DEFAULT_ARROW_TIP_LENGTH": "defaults",
    "DEFAULT_DASH_LENGTH": "defaults",
    "DEFAULT_DOT_RADIUS": "defaults",
    "DEFAULT_FONT_SIZE": "defaults",
    "DEFAULT_MOBJECT_TO_EDGE_BUFFER": "defaults",
    "DEFAULT_MOBJECT_TO_MOBJECT_BUFFER": "defaults",
    "DEFAULT_POINTWISE_FUNCTION_RUN_TIME": "defaults",
    "DEFAULT_POINT_DENSITY_1D": "defaults",
    "DEFAULT_POINT_DENSITY_2D": "defaults",
    "DEFAULT_QUALITY": "defaults",
    "DEFAULT_SMALL_DOT_RADIUS": "defaults",
    "DEFAULT_STROKE_WIDTH": "defaults",
    "DEFAULT_WAIT_TIME": "defaults",
    "SMALL_BUFF": "buffers",
    "MED_SMALL_BUFF": "buffers",
    "MED_LARGE_BUFF": "buffers",
    "LARGE_BUFF": "buffers",
    "X_AXIS": "axes",
    "Y_AXIS": "axes",
    "Z_AXIS": "axes",
    "START_X": "axes",
    "START_Y": "axes",
    "DEGREES": "numeric",
    "PI": "numeric",
    "TAU": "numeric",
    "SCALE_FACTOR_PER_FONT_POINT": "numeric",
    "CHOOSE_NUMBER_MESSAGE": "messages",
    "CONTEXT_SETTINGS": "messages",
    "CTRL_VALUE": "messages",
    "EPILOG": "messages",
    "INVALID_NUMBER_MESSAGE": "messages",
    "NO_SCENE_MESSAGE": "messages",
    "QUALITIES": "messages",
    "RESAMPLING_ALGORITHMS": "messages",
    "SCENE_NOT_FOUND_MESSAGE": "messages",
    "SHIFT_VALUE": "messages",
}

# manim.utils.color.manim_colors names (all of them).
_COLOR_NAMES: frozenset[str] | None = None


def _color_names() -> frozenset[str]:
    global _COLOR_NAMES
    if _COLOR_NAMES is None:
        try:
            import manim.utils.color.manim_colors as _mc

            _COLOR_NAMES = frozenset(
                n for n in dir(_mc) if n.isupper() and not n.startswith("_")
            )
        except Exception:
            _COLOR_NAMES = frozenset()
    return _COLOR_NAMES


def _link_for(name: str) -> tuple[str, str] | None:
    """Return ``(page, anchor)`` for a manim constant name, else None."""
    page = _CONSTANT_PAGES.get(name)
    if page is not None:
        return page, f"manim.constants.{name}"
    if name in _color_names():
        return "colors", f"manim.utils.color.manim_colors.{name}"
    return None


def _process_literals(app, doctree, docname) -> None:
    docdir = posixpath.dirname(docname) or "."
    for node in doctree.findall(nodes.inline):
        classes = node.get("classes", [])
        if "default_value" not in classes:
            continue
        text = node.astext().strip()
        target = _link_for(text)
        if target is None:
            continue
        page, anchor = target
        rel = posixpath.relpath(f"constants/{page}.html", start=docdir)
        ref = nodes.reference("", "", internal=True, refuri=f"{rel}#{anchor}")
        ref += nodes.literal(text, text, classes=["pre"])
        node.replace_self(ref)


def setup(app):
    app.connect("doctree-resolved", _process_literals)
    return {"version": "1.0", "parallel_read_safe": True, "parallel_write_safe": True}
