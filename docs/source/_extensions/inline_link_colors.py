"""Custom Sphinx extension to color inline code cross-reference links.

Links that resolve to ``manim_extensions.*`` objects get the extension-node
colors of the inheritance graph (green), links to ``manim.*`` objects get the
Manim-node colors (blue).  This keeps every inline code link visually
consistent with the inheritance diagram: the module origin of a target is
readable at a glance from the link itself.

The palette is imported from :mod:`inheritance_colors` so the diagram nodes
and the inline links can never drift apart.
"""

import re

from docutils import nodes
from sphinx.addnodes import desc, desc_annotation, desc_content, desc_signature

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
    Type aliases (``ParsableManimColor = str | ...``) render as
    ``types.UnionType`` rather than ``type``, so collect those too.
    """
    import types

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
    manim_aliases = {
        name
        for name, obj in vars(manim).items()
        if isinstance(obj, types.UnionType)
    }
    ext_aliases = {
        name
        for name, obj in vars(manim_extensions).items()
        if isinstance(obj, types.UnionType) and name not in manim_aliases
    }
    return manim_types | manim_aliases, ext_types | ext_aliases


def _type_pattern(manim_types, ext_types):
    """Compile a pattern matching any manim / manim_extensions type name at an
    identifier boundary, longest names first (so ParsableManimColor wins over
    ManimColor)."""
    names = sorted(manim_types | ext_types, key=len, reverse=True)
    return re.compile(
        r"(?<![A-Za-z0-9_])(" + "|".join(re.escape(n) for n in names) + r")(?![A-Za-z0-9_])"
    )


def _type_origin_class(signature, pattern, manim_types, ext_types):
    """Color class for an attribute signature's type text, or None.

    The type can render either as plain text (``tex_template : TexTemplate``,
    possibly a generic like ``dict[str, ParsableManimColor]``) or, depending
    on the sphinx-autodoc-typehints version, as an intersphinx link
    (``a.reference`` to the Manim docs / internal reference).  Handle
    both forms; for plain text, any embedded type name qualifies.
    """
    for annotation in signature.findall(desc_annotation):
        for child in annotation.children:
            if isinstance(child, nodes.Text) and child.strip():
                m = pattern.search(child)
                if m:
                    return "sig-manim-attr" if m.group(1) in manim_types else "sig-ext-attr"
            elif isinstance(child, nodes.reference):
                link_class = _classify(child)
                if link_class == "ref-manim":
                    return "sig-manim-attr"
                if link_class == "ref-ext":
                    return "sig-ext-attr"
    return None


def _split_type_refs(annotation, pattern, manim_types, ext_types):
    """Color only the manim / manim_extensions names inside a plain-text type.

    A generic type renders as one text node (``dict[str,
    ParsableManimColor]``); coloring the whole node would also tint the
    builtins and brackets.  Split the text at each embedded type name and
    wrap those names in inline spans tagged sig-type-ref-manim /
    sig-type-ref-ext, which custom.css colors like inline-code links.
    Builtins (dict, str, list, ...) and syntax stay untouched.
    """
    for child in list(annotation.children):
        if not isinstance(child, nodes.Text) or not child.strip():
            continue
        parts = pattern.split(child)
        if len(parts) == 1:
            continue
        new_children = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                ref_cls = "sig-type-ref-manim" if part in manim_types else "sig-type-ref-ext"
                ref = nodes.inline(classes=[ref_cls], rawsource=part)
                ref += nodes.Text(part)
                new_children.append(ref)
            elif part:
                new_children.append(nodes.Text(part))
        idx = annotation.children.index(child)
        annotation.children[idx:idx + 1] = new_children


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
    # Cross-page internal references carry a relative refuri whose fragment
    # is the canonical dotted target, e.g. ``../mindmap/nodes.html#manim_
    # extensions.mindmap.nodes.node.Node`` — classify from the fragment.
    if "#manim_extensions." in uri:
        return "ref-ext"
    if "#manim." in uri:
        return "ref-manim"
    return None


def _drop_auto_attribute_members(doctree):
    """Remove attribute members from classes whose docstring has no
    Attributes section.

    autodoc ``members`` collects inherited public attributes (e.g.
    ``FileTree.code`` from ``Code``) even when the class docstring never
    documents them, producing a bare ``Attributes`` block out of nowhere.
    Classes that do document an Attributes section keep their members —
    numpydoc renders those entries from the docstring.
    """
    import importlib
    import inspect

    attr_section_re = re.compile(r"^\s*Attributes\s*$", re.M)
    for d in list(doctree.findall(desc)):
        if "class" not in d.get("classes", ()):
            continue
        node_id = d.get("ids") or (
            next(
                (s.get("ids") for s in d.findall(desc_signature) if s.get("ids")),
                None,
            )
        )
        if not node_id:
            continue
        dotted = node_id[0]
        if not dotted.startswith("manim_extensions"):
            continue
        try:
            modname, _, clsname = dotted.rpartition(".")
            cls = getattr(importlib.import_module(modname), clsname)
            doc = inspect.getdoc(cls) or ""
        except Exception:
            continue
        if attr_section_re.search(doc):
            continue
        content = next(
            (c for c in d.children if isinstance(c, desc_content)), None
        )
        if content is None:
            continue
        for c in list(content.children):
            if isinstance(c, desc) and "attribute" in c.get("classes", ()):
                content.remove(c)


def _process_doctree(app, doctree, docname):
    """Tag every inline code xref link with its inheritance-graph color class."""
    _drop_auto_attribute_members(doctree)
    manim_types, ext_types = _known_type_names()
    pattern = _type_pattern(manim_types, ext_types)
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
    # (the <dt>) itself only carries sig/sig-object classes.  Plain-text
    # types are then split so only the embedded type names get colored
    # (builtins such as dict/str inside generics stay uncolored).
    for sig in doctree.findall(desc_signature):
        parent_desc = sig.parent
        if not parent_desc or "attribute" not in parent_desc.get("classes", ()):
            continue
        attr_class = _type_origin_class(sig, pattern, manim_types, ext_types)
        if not attr_class:
            continue
        classes = list(sig.get("classes", ()))
        if attr_class not in classes:
            sig["classes"] = classes + [attr_class]
        for ann in sig.findall(desc_annotation):
            for child in ann.children:
                if isinstance(child, nodes.reference):
                    link_class = _classify(child)
                    if link_class:
                        classes = list(child.get("classes", ()))
                        if link_class not in classes:
                            child["classes"] = classes + [link_class]
            _split_type_refs(ann, pattern, manim_types, ext_types)

    _add_attribute_headings(doctree)


def _add_attribute_headings(doctree):
    """Insert an ``Attributes`` rubric heading before a class's attributes.

    Autodoc renders class attributes (``:members:``) as bare
    ``py.attribute`` entries with no heading, while the docstring's
    Parameters section gets a field-list heading (``Parameters:``).  Add a
    rubric in the same position so the attribute block reads
    ``Attributes:`` — styled identically by custom.css (bold, capitalize,
    trailing colon).  Classes whose docstring already carries a numpydoc
    Attributes section are skipped.
    """
    for d in list(doctree.findall(desc)):
        if "class" not in d.get("classes", ()):
            continue
        content = next(
            (c for c in d.children if isinstance(c, desc_content)), None
        )
        if content is None:
            continue
        attr_descs = [
            c for c in content.children
            if isinstance(c, desc) and "attribute" in c.get("classes", ())
        ]
        if not attr_descs:
            continue
        # A numpydoc Attributes section already supplies the heading.
        first_attr = attr_descs[0]
        preceding = content.children[:content.children.index(first_attr)]
        if any(
            isinstance(c, nodes.rubric) and c.astext().strip() == "Attributes"
            for c in preceding
        ):
            continue
        idx = content.children.index(first_attr)
        content.insert(idx, nodes.rubric("", "Attributes"))


def setup(app):
    app.connect("doctree-resolved", _process_doctree)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
    }
