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
from sphinx.addnodes import desc_annotation, desc_signature

from inheritance_colors import (
    _EXTENSIONS_FILL,
    _EXTENSIONS_FONT,
    _MANIM_FILL,
    _MANIM_FONT,
)

_MANIM_DOCS_HOST = "docs.manim.community"


def _known_type_names():
    """Map every importable class name to its origin color class.

    Autodoc renders class-attribute signatures with a plain text type
    (``tex_template : TexTemplate``) that never becomes a reference, so the
    reference classifier below cannot see it.  Match the type text against
    the manim / manim_extensions class names instead and tag the whole
    signature; custom.css then colors the type like an inline-code link.
    """
    import manim
    import manim_extensions

    manim_types = {
        name
        for name, obj in vars(manim).items()
        if isinstance(obj, type)
    }
    ext_types = {
        name
        for name, obj in vars(manim_extensions).items()
        if isinstance(obj, type)
        and getattr(obj, "__module__", "").startswith("manim_extensions")
    }
    return manim_types, ext_types


def _type_origin_class(signature, manim_types, ext_types):
    """Color class for an attribute signature's type text, or None.

    The type can render either as plain text (``tex_template : TexTemplate``)
    or, depending on the sphinx-autodoc-typehints version, as an intersphinx
    link (``a.reference`` to the Manim docs / internal reference).  Handle
    both forms.
    """
    for annotation in signature.findall(desc_annotation):
        for child in annotation.children:
            if isinstance(child, nodes.Text) and child.strip():
                text = child.strip()
                if text in manim_types:
                    return "sig-manim-attr"
                if text in ext_types:
                    return "sig-ext-attr"
            elif isinstance(child, nodes.reference):
                link_class = _classify(child)
                if link_class == "ref-manim":
                    return "sig-manim-attr"
                if link_class == "ref-ext":
                    return "sig-ext-attr"
    return None


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
    manim_types, ext_types = _known_type_names()
    for node in doctree.findall(nodes.reference):
        if not _has_inline_code(node):
            continue
        link_class = _classify(node)
        if not link_class:
            continue
        classes = list(node.get("classes", ()))
        if link_class not in classes:
            node["classes"] = classes + [link_class]

    # Class-attribute signatures (e.g. ``tex_template : TexTemplate``): the
    # type is plain text, not a reference, so tag the signature by the type's
    # origin and let custom.css color the type like an inline-code link.
    # Autodoc marks the *desc* (the <dl>) as an attribute; the signature
    # (the <dt>) itself only carries sig/sig-object classes.
    for sig in doctree.findall(desc_signature):
        parent_desc = sig.parent
        if not parent_desc or "attribute" not in parent_desc.get("classes", ()):
            continue
        attr_class = _type_origin_class(sig, manim_types, ext_types)
        if not attr_class:
            continue
        classes = list(sig.get("classes", ()))
        if attr_class not in classes:
            sig["classes"] = classes + [attr_class]


def setup(app):
    app.connect("doctree-resolved", _process_doctree)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
    }
