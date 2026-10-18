"""Custom Sphinx extension to color inline code cross-reference links.

Links that resolve to ``manim_extensions.*`` objects get the extension-node
colors of the inheritance graph (green), links to ``manim.*`` objects get the
Manim-node colors (blue).  This keeps every inline code link visually
consistent with the inheritance diagram: the module origin of a target is
readable at a glance from the link itself.

The palette is imported from :mod:`inheritance_colors` so the diagram nodes
and the inline links can never drift apart.
"""

from docutils import nodes

from inheritance_colors import (
    _EXTENSIONS_FILL,
    _EXTENSIONS_FONT,
    _MANIM_FILL,
    _MANIM_FONT,
)

_MANIM_DOCS_HOST = "docs.manim.community"


def _has_inline_code(node):
    """True if this reference renders as an inline-code link (code.xref)."""
    return any(
        isinstance(child, nodes.Element) and "xref" in child.get("classes", ())
        for child in node.children
    )


def _classify(node):
    """Return the inheritance-graph color class for a resolved reference."""
    target = node.get("refid") or ""
    if target.startswith("manim_extensions"):
        return "ref-ext"
    if target.startswith("manim."):
        return "ref-manim"
    # Intersphinx links to the Manim docs (e.g. manim.mobject.* objects).
    uri = node.get("refuri") or ""
    if _MANIM_DOCS_HOST in uri and "/reference/manim." in uri:
        return "ref-manim"
    return None


def _process_doctree(app, doctree, docname):
    """Tag every inline code xref link with its inheritance-graph color class."""
    for node in doctree.findall(nodes.reference):
        if not _has_inline_code(node):
            continue
        link_class = _classify(node)
        if not link_class:
            continue
        classes = list(node.get("classes", ()))
        if link_class not in classes:
            node["classes"] = classes + [link_class]


def setup(app):
    app.connect("doctree-resolved", _process_doctree)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
    }
