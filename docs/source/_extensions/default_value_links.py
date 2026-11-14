# SPDX-FileCopyrightText: 2026 ExploreMaths
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
from sphinx.addnodes import desc, desc_annotation, desc_signature
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
    ``"ext"`` for objects living in ``manim_extensions``.

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
    matches = [full for full in objects if full == name or full.endswith("." + name)]
    if len(matches) == 1:
        entry = objects[matches[0]]
        # Return the site-relative docname (no extension), exactly like the
        # constant/color branches: every caller appends ".html" itself.
        return entry.docname, entry.node_id, "ext"
    return None


_INTERSPHINX_TYPES = ("py:class", "py:data", "py:function", "py:module", "py:type")


def _external_link_for(name: str, app) -> str | None:
    """Return the intersphinx URL for a class/type outside this project."""
    inventory = getattr(app.env, "intersphinx_inventory", {})
    for objtype in _INTERSPHINX_TYPES:
        entry = inventory.get(objtype, {}).get(name)
        if entry is not None:
            return getattr(entry, "uri", None)
    return None


# A constant-looking token inside a default expression: an ALL-CAPS name
# (``WHITE``, ``PI``) or a dotted name (``NodeConfig.BOX_TYPE``).
_TOKEN_RE = re.compile(
    r"(?:[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_.]*)" r"|\b[A-Z][A-Z0-9_]{1,}\b"
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
            parts.append(nodes.Text(text[pos : m.start()]))
        name = m.group(0)
        target = _link_for(name, app, docdir)
        if target is None:
            parts.append(nodes.Text(name))
        else:
            page, anchor, kind = target
            rel = posixpath.relpath(f"{page}.html", start=docdir)
            ref = nodes.reference("", "", internal=True, refuri=f"{rel}#{anchor}")
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
            ref = nodes.reference("", "", internal=True, refuri=f"{rel}#{anchor}")
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
    tokens with links to ``constants/colors``.  The constants category pages
    are skipped: there the names are the documented objects themselves.
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
                parts.append(nodes.Text(text[pos : m.start()]))
            name = m.group(0)
            if name in _color_names():
                rel = posixpath.relpath("constants/colors.html", start=docdir)
                ref = nodes.reference(
                    "",
                    "",
                    internal=True,
                    refuri=f"{rel}#manim.utils.color.manim_colors.{name}",
                )
                ref += nodes.Text(name)
                parts.append(ref)
                linked = True
            else:
                parts.append(nodes.Text(name))
            pos = m.end()
        if pos < len(text):
            parts.append(nodes.Text(text[pos:]))
        if linked:
            pass
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
    ``manim_extensions``, turn it into an internal link.  Signatures,
    default values and already-linked literals are skipped.
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
        "Parameters",
        "OtherParameters",
        "Returns",
        "Yields",
        "Receives",
        "Raises",
        "Warns",
        "Attributes",
        "Methods",
        "Examples",
        "Notes",
        "References",
        "SeeAlso",
        "Condition",
        "Command",
        "Check",
        "Checks",
        "Warning",
        "Fields",
        "Modules",
        "Arguments",
        "Args",
        "KeywordArgs",
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
            (full, entry)
            for full, entry in objects.items()
            if (full == text or full.endswith("." + text))
            and full.startswith("manim_extensions")
        ]
        # Methods, properties and attributes are member names, not
        # reference targets: a bare ``install`` / ``scale`` / ``text``
        # in prose is a generic word, not an attempt to link a specific
        # member.  Only top-level classes, functions and module-level
        # data participate.
        matches = [
            (full, entry)
            for full, entry in candidates
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
        ref = nodes.reference("", "", internal=True, refuri=f"{rel}#{entry.node_id}")
        ref += nodes.Text(text)
        del node[:]
        node.append(ref)


# Keep in sync with ``autodoc_all._VALUE_LINK_RE``: ``<class '...'>``,
# ``type[...]``, dotted paths and ``ClassName(`` are the spellings used by
# ``repr`` output.
_VALUE_REF_RE = re.compile(
    r"(?P<classrepr><class '(?P<classpath>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)'>)"
    r"|(?P<typeexpr>type\[(?P<typepath>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)\])"
    r"|(?P<dotted>[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+)"
    r"|(?P<call>[A-Z][A-Za-z0-9_]*(?=\())"
)


def _process_constant_signature_values(app, doctree, docname) -> None:
    """Link class/type tokens in ordinary ``autodata`` constant values.

    Constants below the folding threshold are rendered by autodoc as plain
    text inside the ``desc_annotation`` of their data signature.  They never
    reach the payload HTML, so apply the same dotted/class-name resolution
    here.  Tokens that do not resolve stay verbatim.
    """
    docdir = posixpath.dirname(docname) or "."
    for sig in doctree.findall(desc_signature):
        parent = sig.parent
        if not isinstance(parent, desc) or parent.get("objtype") != "data":
            continue
        # A data signature can carry more than one annotation: type aliases
        # first get ``: TypeAlias`` and then a separate annotation with the
        # value, so inspect every annotation instead of only the first.
        annotations = [
            child for child in sig.children if isinstance(child, desc_annotation)
        ]
        for annotation in annotations:
            for text_node in list(annotation.findall(nodes.Text)):
                text = text_node.astext()
                if not _VALUE_REF_RE.search(text):
                    continue
                parts = []
                pos = 0
                for match in _VALUE_REF_RE.finditer(text):
                    if match.start() > pos:
                        parts.append(nodes.Text(text[pos : match.start()]))
                    token = match.group(0)
                    target = (
                        match.group("classpath") or match.group("typepath") or token
                    )
                    short = target.rsplit(".", 1)[-1]
                    if match.group("classrepr"):
                        shown = short
                        prefix = suffix = ""
                    elif match.group("typeexpr"):
                        shown = short
                        prefix, suffix = "type[", "]"
                    else:
                        shown = token
                        prefix = suffix = ""
                    resolved = _link_for(target, app, docdir)
                    if resolved is not None:
                        page, anchor, _kind = resolved
                        rel = posixpath.relpath(f"{page}.html", start=docdir)
                        ref = nodes.reference(
                            "", "", internal=True, refuri=f"{rel}#{anchor}"
                        )
                        ref += nodes.Text(shown)
                        if prefix:
                            parts.append(nodes.Text(prefix))
                        parts.append(ref)
                        if suffix:
                            parts.append(nodes.Text(suffix))
                    elif (external := _external_link_for(target, app)) is not None:
                        ref = nodes.reference("", "", internal=False, refuri=external)
                        ref += nodes.Text(shown)
                        if prefix:
                            parts.append(nodes.Text(prefix))
                        parts.append(ref)
                        if suffix:
                            parts.append(nodes.Text(suffix))
                    else:
                        parts.append(nodes.Text(token))
                    pos = match.end()
                if pos < len(text):
                    parts.append(nodes.Text(text[pos:]))
                text_node.parent.replace(text_node, parts)


_PAYLOAD_REF_RE = re.compile(
    r'<span class="constant-value-ref" data-target="([^"]+)" '
    r'data-fallback="([^"]*)">(.*?)</span>'
)


def _process_constant_value_payloads(app, doctree, docname) -> None:
    """Resolve class/type markers inside expanded constant values.

    Large constants are stored as raw HTML alongside their summary.  Their
    full value keeps the same class/type tokens as the source spelling; this
    pass turns those tokens into the same internal references used by
    signature defaults.  Tokens that do not resolve are restored verbatim,
    so the rendered value stays exact.
    """
    docdir = posixpath.dirname(docname) or "."
    for node in doctree.findall(nodes.raw):
        text = node.astext()
        if "constant-value-ref" not in text:
            continue

        def replace(match: re.Match) -> str:
            target, fallback, shown = match.group(1), match.group(2), match.group(3)
            resolved = _link_for(target, app, docdir)
            if resolved is not None:
                page, anchor, _kind = resolved
                rel = posixpath.relpath(f"{page}.html", start=docdir)
                href = f"{rel}#{anchor}"
                css_class = "reference internal"
            else:
                href = _external_link_for(target, app)
                css_class = "reference external"
            if href is None:
                return fallback
            if shown.startswith("type[") and shown.endswith("]"):
                inner = shown[5:-1]
                return f'type[<a class="{css_class}" href="{href}">{inner}</a>]'
            return f'<a class="{css_class}" href="{href}">{shown}</a>'

        new_text = _PAYLOAD_REF_RE.sub(replace, text)
        if new_text != text:
            del node[:]
            node.append(nodes.Text(new_text))


def setup(app):
    app.connect("doctree-resolved", _process_literals)
    app.connect("doctree-resolved", _process_color_codes)
    app.connect("doctree-resolved", _process_prose_literals)
    app.connect("doctree-resolved", _process_constant_signature_values)
    app.connect("doctree-resolved", _process_constant_value_payloads)
    return {"version": "1.1", "parallel_read_safe": True, "parallel_write_safe": True}
