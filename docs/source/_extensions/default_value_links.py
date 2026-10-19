# SPDX-FileCopyrightText: 2026 ExploreMaths
#
# SPDX-License-Identifier: MIT

"""Link manim / manim_extensions constant names in signature defaults.

With ``autodoc_preserve_defaults`` enabled, autodoc renders defaults with
their source spelling (``color=WHITE`` instead of
``color=ManimColor('#FFFFFF')``) inside ``inline`` nodes carrying the
``default_value`` class.  Those names are plain text, so this extension
replaces the inline node with a real reference to the page that documents
the constant (``constants/colors.html``, ``reference/basic/mobjects.html``
for project constants, ...), which carries the object anchors collected
by autodoc.  The link is plain text (no ``code`` wrapper) so it does not
pick up the inline-code background/border.
"""

from __future__ import annotations

import posixpath

from docutils import nodes

_CONSTANT_PAGES: dict[str, str] = {
    # manim.constants names -> rst path of the category page (no extension)
    "ORIGIN": "constants/directions",
    "UP": "constants/directions",
    "DOWN": "constants/directions",
    "LEFT": "constants/directions",
    "RIGHT": "constants/directions",
    "IN": "constants/directions",
    "OUT": "constants/directions",
    "UL": "constants/directions",
    "UR": "constants/directions",
    "DL": "constants/directions",
    "DR": "constants/directions",
    "BOLD": "constants/fonts",
    "BOOK": "constants/fonts",
    "HEAVY": "constants/fonts",
    "ITALIC": "constants/fonts",
    "LIGHT": "constants/fonts",
    "MEDIUM": "constants/fonts",
    "NORMAL": "constants/fonts",
    "OBLIQUE": "constants/fonts",
    "SEMIBOLD": "constants/fonts",
    "SEMILIGHT": "constants/fonts",
    "THIN": "constants/fonts",
    "ULTRABOLD": "constants/fonts",
    "ULTRAHEAVY": "constants/fonts",
    "ULTRALIGHT": "constants/fonts",
    "DEFAULT_ARROW_TIP_LENGTH": "constants/defaults",
    "DEFAULT_DASH_LENGTH": "constants/defaults",
    "DEFAULT_DOT_RADIUS": "constants/defaults",
    "DEFAULT_FONT_SIZE": "constants/defaults",
    "DEFAULT_MOBJECT_TO_EDGE_BUFFER": "constants/defaults",
    "DEFAULT_MOBJECT_TO_MOBJECT_BUFFER": "constants/defaults",
    "DEFAULT_POINTWISE_FUNCTION_RUN_TIME": "constants/defaults",
    "DEFAULT_POINT_DENSITY_1D": "constants/defaults",
    "DEFAULT_POINT_DENSITY_2D": "constants/defaults",
    "DEFAULT_QUALITY": "constants/defaults",
    "DEFAULT_SMALL_DOT_RADIUS": "constants/defaults",
    "DEFAULT_STROKE_WIDTH": "constants/defaults",
    "DEFAULT_WAIT_TIME": "constants/defaults",
    "SMALL_BUFF": "constants/buffers",
    "MED_SMALL_BUFF": "constants/buffers",
    "MED_LARGE_BUFF": "constants/buffers",
    "LARGE_BUFF": "constants/buffers",
    "X_AXIS": "constants/axes",
    "Y_AXIS": "constants/axes",
    "Z_AXIS": "constants/axes",
    "START_X": "constants/axes",
    "START_Y": "constants/axes",
    "DEGREES": "constants/numeric",
    "PI": "constants/numeric",
    "TAU": "constants/numeric",
    "SCALE_FACTOR_PER_FONT_POINT": "constants/numeric",
    "CHOOSE_NUMBER_MESSAGE": "constants/messages",
    "CONTEXT_SETTINGS": "constants/messages",
    "CTRL_VALUE": "constants/messages",
    "EPILOG": "constants/messages",
    "INVALID_NUMBER_MESSAGE": "constants/messages",
    "NO_SCENE_MESSAGE": "constants/messages",
    "QUALITIES": "constants/messages",
    "RESAMPLING_ALGORITHMS": "constants/messages",
    "SCENE_NOT_FOUND_MESSAGE": "constants/messages",
    "SHIFT_VALUE": "constants/messages",
}

# manim_extensions constants used as signature defaults -> (rst path, anchor).
_PROJECT_CONSTANTS: dict[str, tuple[str, str]] = {
    "DEFAULT_CJK_FONT": (
        "reference/basic/mobjects",
        "manim_extensions.mobjects.DEFAULT_CJK_FONT",
    ),
    "NodeConfig.BOX_TYPE": (
        "reference/algorithm/classes",
        "manim_extensions.algorithm.node.NodeConfig.BOX_TYPE",
    ),
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
    """Return ``(rst_path, anchor)`` for a known constant name, else None."""
    proj = _PROJECT_CONSTANTS.get(name)
    if proj is not None:
        return proj
    page = _CONSTANT_PAGES.get(name)
    if page is not None:
        return page, f"manim.constants.{name}"
    if name in _color_names():
        return "constants/colors", f"manim.utils.color.manim_colors.{name}"
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
        rel = posixpath.relpath(f"{page}.html", start=docdir)
        ref = nodes.reference("", "", internal=True, refuri=f"{rel}#{anchor}")
        ref += nodes.Text(text)
        node.replace_self(ref)


def setup(app):
    app.connect("doctree-resolved", _process_literals)
    return {"version": "1.1", "parallel_read_safe": True, "parallel_write_safe": True}
