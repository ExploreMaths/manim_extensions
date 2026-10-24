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
import re

from docutils import nodes
from sphinx.addnodes import desc_signature
from sphinx.util import logging

logger = logging.getLogger(__name__)

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


def _link_for(name: str, app, docdir: str) -> tuple[str, str, str] | None:
    """Return ``(rst_path, anchor, kind)`` for a known constant name.

    ``kind`` is ``"manim"`` for manim colors/constants pages and
    ``"ext"`` for objects living in ``manim_extensions``; the HTML
    writer's palette (custom.css) uses it to color signature-default
    links the same way as inline-code cross-references.

    Resolution order:
    1. manim.utils.color.manim_colors names (auto-collected, all of them);
    2. hard-coded manim.constants category pages;
    3. any object the py domain registered this build — the default text is
       matched as a suffix of the fully-qualified object name
       (``NodeConfig.BOX_TYPE`` → ``...node.NodeConfig.BOX_TYPE``) and, when
       the match is unique, linked to its autodoc page.  This keeps every
       project constant/attribute covered without maintaining the list.
    """
    if name in _color_names():
        return "constants/colors", f"manim.utils.color.manim_colors.{name}", "manim"
    page = _CONSTANT_PAGES.get(name)
    if page is not None:
        return page, f"manim.constants.{name}", "manim"
    # Fall back to whatever the py domain registered (project objects).
    try:
        objects = app.env.domains["py"].data["objects"]
    except (KeyError, AttributeError):
        objects = {}
    matches = [
        full for full in objects
        if full == name or full.endswith("." + name)
    ]
    if len(matches) == 1:
        entry = objects[matches[0]]
        # Return the site-relative docname (no extension), exactly like the
        # constant/color branches: every caller appends ".html" itself.
        return entry.docname, entry.node_id, "ext"
    return None


# A constant-looking token inside a default expression: an ALL-CAPS name
# (``WHITE``, ``PI``) or a dotted name (``NodeConfig.BOX_TYPE``).
_TOKEN_RE = re.compile(
    r"(?:[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_.]*)"
    r"|\b[A-Z][A-Z0-9_]{1,}\b"
)
# Defaults that are composite expressions (tuple/list/dict/call): link the
# constant tokens inside instead of leaving the whole text plain.
_COMPOSITE_RE = re.compile(r"[({[\<]")


def _link_tokens(node, text: str, app, docdir: str) -> None:
    """Replace linkable constant tokens inside ``text`` with references."""
    parts = []
    pos = 0
    for m in _TOKEN_RE.finditer(text):
        if m.start() > pos:
            parts.append(nodes.Text(text[pos:m.start()]))
        name = m.group(0)
        target = _link_for(name, app, docdir)
        if target is None:
            parts.append(nodes.Text(name))
        else:
            page, anchor, kind = target
            rel = posixpath.relpath(f"{page}.html", start=docdir)
            ref = nodes.reference("", "", internal=True,
                                  refuri=f"{rel}#{anchor}")
            ref["classes"] = [f"ref-{kind}"]
            ref += nodes.Text(name)
            parts.append(ref)
        pos = m.end()
    if pos < len(text):
        parts.append(nodes.Text(text[pos:]))
    # Rebuild via append so docutils sets .parent on each child
    # (a bare ``node.children = parts`` leaves them parentless, which
    # breaks the HTML writer's reference checks).
    del node[:]
    for part in parts:
        node.append(part)


def _process_literals(app, doctree, docname) -> None:
    docdir = posixpath.dirname(docname) or "."
    for node in doctree.findall(nodes.inline):
        classes = node.get("classes", [])
        if "default_value" not in classes:
            continue
        text = node.astext().strip()
        target = _link_for(text, app, docdir)
        if target is not None:
            page, anchor, kind = target
            rel = posixpath.relpath(f"{page}.html", start=docdir)
            ref = nodes.reference("", "", internal=True,
                                  refuri=f"{rel}#{anchor}")
            ref["classes"] = [f"ref-{kind}"]
            ref += nodes.Text(text)
            node.replace_self(ref)
            continue
        # Composite default (``(UP, LEFT)``, ``[WHITE, BLUE]``, ...): link
        # the constant tokens it embeds.
        if _COMPOSITE_RE.search(text) and _TOKEN_RE.search(text):
            _link_tokens(node, text, app, docdir)


def _process_color_codes(app, doctree, docname) -> None:
    """Link manim color names inside inline code in prose.

    Docstrings often write colors as `` `WHITE` `` / `` `[BLUE, GREEN]` ``;
    without a cross-reference they render as plain text.  Replace the color
    tokens with links to ``constants/colors`` so they carry the link color,
    like the signature-default links do.  The constants category pages are
    skipped: there the names are the documented objects themselves.
    """
    if docname.startswith("constants/"):
        return
    docdir = posixpath.dirname(docname) or "."
    for node in doctree.findall(nodes.literal):
        text = node.astext().strip()
        if not _TOKEN_RE.search(text):
            continue
        if not any(name in text for name in _color_names()):
            continue
        parts = []
        linked = False
        pos = 0
        for m in _TOKEN_RE.finditer(text):
            if m.start() > pos:
                parts.append(nodes.Text(text[pos:m.start()]))
            name = m.group(0)
            if name in _color_names():
                rel = posixpath.relpath("constants/colors.html",
                                        start=docdir)
                ref = nodes.reference(
                    "", "", internal=True,
                    refuri=f"{rel}#manim.utils.color.manim_colors.{name}",
                )
                # Tag as a manim link so inline_link_colors' palette (which
                # runs earlier on doctree-resolved and cannot see these
                # nodes) still colors the text and fill of this inline code.
                ref["classes"] = ["ref-manim"]
                ref += nodes.Text(name)
                parts.append(ref)
                linked = True
            else:
                parts.append(nodes.Text(name))
            pos = m.end()
        if pos < len(text):
            parts.append(nodes.Text(text[pos:]))
        if linked:
            # The link sits *inside* the code element here (unlike
            # inline_link_colors, where the code is inside the link), so
            # custom.css fills the code via this marker class.
            classes = list(node.get("classes", ()))
            if "color-link-manim" not in classes:
                node["classes"] = classes + ["color-link-manim"]
        del node[:]
        for part in parts:
            node.append(part)


def _in_signature(node) -> bool:
    parent = node.parent
    while parent is not None:
        if isinstance(parent, desc_signature):
            return True
        parent = parent.parent
    return False


def _in_reference(node) -> bool:
    """True when the node sits inside an existing cross-reference link.

    An explicit ``:class:`...``` role renders as ``reference > literal``
    (the link wraps the code), so the literal's children are plain text and
    a child-level check alone cannot detect it — relinking would nest a
    second link inside the first.
    """
    parent = node.parent
    while parent is not None:
        if isinstance(parent, nodes.reference):
            return True
        parent = parent.parent
    return False


def _process_prose_literals(app, doctree, docname) -> None:
    """Link project class/function names written as prose inline code.

    Docstrings and changelog entries write class names as `` ``Code`` `` /
    `` ``ManimTuringMachine`` ``; without a cross-reference they render as
    plain inline code.  When the literal text exactly names one py-domain
    object this build knows (unique suffix match) and that object lives in
    ``manim_extensions``, turn it into an internal link tagged ref-ext and
    mark the code element so custom.css fills it with the extension palette,
    mirroring what _process_color_codes does for manim color names.
    Signatures, default values and already-linked literals are skipped.
    """
    try:
        objects = app.env.domains["py"].data["objects"]
    except (KeyError, AttributeError):
        objects = {}
    # Prose words that are generic numpydoc/section vocabulary: even if a
    # project object happens to share the name (e.g. Parameters), a bare
    # ``Parameters`` in prose means the section, not the class.  Never
    # auto-link these.
    GENERIC_PROSE_NAMES = {
        "Parameters", "OtherParameters", "Returns", "Yields", "Receives",
        "Raises", "Warns", "Attributes", "Methods", "Examples", "Notes",
        "References", "SeeAlso", "Condition", "Command", "Check", "Checks",
        "Warning", "Fields", "Modules", "Arguments", "Args", "KeywordArgs",
    }
    for node in list(doctree.findall(nodes.literal)):
        if any(isinstance(c, nodes.reference) for c in node.children):
            continue
        if "default_value" in node.get("classes", ()):
            continue
        if _in_signature(node) or _in_reference(node):
            continue
        text = node.astext().strip()
        if len(text) < 2 or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text):
            # Single letters (e.g. Rubik's cube turn notation U/F/B that
            # collide with chemical element symbols) are never meant as
            # object references.
            continue
        if text in GENERIC_PROSE_NAMES:
            continue
        candidates = [
            (full, entry) for full, entry in objects.items()
            if (full == text or full.endswith("." + text))
            and full.startswith("manim_extensions")
        ]
        # Methods, properties and attributes are member names, not
        # reference targets: a bare ``install`` / ``scale`` / ``text``
        # in prose is a generic word, not an attempt to link a specific
        # member.  Only top-level classes, functions and module-level
        # data participate.
        matches = [
            (full, entry) for full, entry in candidates
            if entry.objtype not in ("method", "property", "attribute")
        ]
        if len(matches) > 1:
            # An inline-code name that names several objects is a doc
            # smell: the reader cannot tell which object it points to.
            # Warn so CI (validate_refs) can fail on it; fix by narrowing
            # the reference (e.g. an explicit :class: with a full path).
            logger.warning(
                "ambiguous inline-code class name %r resolves to %s",
                text,
                ", ".join(sorted(full for full, _ in matches)),
                location=docname,
            )
            continue
        if len(matches) != 1:
            continue
        full, entry = matches[0]
        docdir = posixpath.dirname(docname) or "."
        rel = posixpath.relpath(f"{entry.docname}.html", start=docdir)
        ref = nodes.reference("", "", internal=True,
                              refuri=f"{rel}#{entry.node_id}")
        ref["classes"] = ["ref-ext"]
        ref += nodes.Text(text)
        del node[:]
        node.append(ref)
        classes = list(node.get("classes", ()))
        if "color-link-ext" not in classes:
            node["classes"] = classes + ["color-link-ext"]


def setup(app):
    app.connect("doctree-resolved", _process_literals)
    app.connect("doctree-resolved", _process_color_codes)
    app.connect("doctree-resolved", _process_prose_literals)
    return {"version": "1.1", "parallel_read_safe": True, "parallel_write_safe": True}
