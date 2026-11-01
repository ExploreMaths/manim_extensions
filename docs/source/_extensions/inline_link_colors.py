"""Custom Sphinx extension: structural fixes for class documentation.

Inline-code cross-reference links no longer get custom colors — they use
Furo's native link color.  Coloring is limited to the inheritance graph
(see :mod:`inheritance_colors` + ``responsiveSvg.js``).  This extension
only keeps the two structure fixes that autodoc needs:

- :func:`_drop_auto_attribute_members` removes inherited attribute members
  from classes whose docstring has no ``Attributes`` section (they produce
  a bare Attributes block with anchors that nothing links to);
- :func:`_add_attribute_headings` inserts an ``Attributes`` rubric heading
  before a class's rendered attribute members and moves the block in front
  of a preceding Examples section.
"""

import re

from docutils import nodes
from sphinx.addnodes import desc, desc_content, desc_signature


def _drop_auto_attribute_members(doctree):
    """Remove inherited attribute members from classes whose docstring has
    no Attributes section.

    autodoc ``members`` collects inherited public attributes (e.g.
    ``FileTree.code`` from ``Code``) even when the class docstring never
    documents them, producing a bare ``Attributes`` block out of nowhere.
    Attributes the class defines itself (e.g. ``NodeConfig.BOX_TYPE``) are
    kept — they are real API surface the sidebar links to, and removing
    them leaves dangling anchors.  Classes that do document an Attributes
    section keep all their members — numpydoc renders those entries from
    the docstring.
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
            if not (isinstance(c, desc) and "attribute" in c.get("classes", ())):
                continue
            # Only inherited members are dropped: autodoc's id for an
            # attribute member is ``<class dotted>.<name>``; if the name is
            # not in the class's own ``__dict__`` it comes from a base
            # class.  Guard against odd id shapes (no dot / module-level).
            attr_id = c.get("ids") or (
                next(
                    (s.get("ids") for s in c.findall(desc_signature) if s.get("ids")),
                    None,
                )
            )
            if not attr_id:
                continue
            name = attr_id[0].rpartition(".")[2]
            if name and name in getattr(cls, "__dict__", {}):
                continue
            content.remove(c)


def _process_doctree(app, doctree, docname):
    _drop_auto_attribute_members(doctree)
    _add_attribute_headings(doctree)


def _find_examples_start(content, first_attr):
    """Return the node that opens the docstring's Examples block, if any.

    Autodoc renders an ``.. admonition:: Example`` (or numpydoc-style
    example section) as a ``rubric`` titled "Examples" followed by raw
    HTML/imagery/literal blocks.  Only blocks that sit *before* the first
    attribute member count — an Examples section after the members keeps
    its natural place.
    """
    for c in content.children:
        if c is first_attr:
            break
        if isinstance(c, nodes.rubric) and c.astext().strip().lower() == "examples":
            return c
        if isinstance(c, nodes.raw):
            body = c.astext().lower()
            if "admonition" in body and "example" in body:
                return c
    return None


def _add_attribute_headings(doctree):
    """Insert an ``Attributes`` rubric heading before a class's attributes.

    Autodoc renders class attributes (``:members:``) as bare
    ``py.attribute`` entries with no heading, while the docstring's
    Parameters section gets a field-list heading (``Parameters:``).  Add a
    rubric in the same position so the attribute block reads
    ``Attributes:`` — styled identically by custom.css (bold, capitalize,
    trailing colon).  Classes whose docstring already carries a numpydoc
    Attributes section are skipped.

    The whole attribute block is also moved before the docstring's
    Examples section (when one precedes it), so the members read in the
    order ``description → Attributes → Examples`` instead of trailing the
    example imagery.
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
        ex_start = _find_examples_start(content, first_attr)
        rubric = nodes.rubric("", "Attributes")
        if ex_start is None:
            idx = content.children.index(first_attr)
            content.insert(idx, rubric)
            continue
        # Move rubric + attribute members in front of the Examples block.
        # ``index`` nodes sit between members and must travel with them.
        idx_attr = content.children.index(first_attr)
        block = []
        for c in content.children[idx_attr:]:
            if c in attr_descs or (
                getattr(c, "tagname", None) == "index" and block
            ):
                block.append(c)
            elif getattr(c, "tagname", None) == "index":
                continue
            else:
                break
        idx_ex = content.children.index(ex_start)
        head = content.children[:idx_ex]
        tail = [c for c in content.children[idx_ex:] if c not in block]
        content.children[:] = head + [rubric] + block + tail


def setup(app):
    app.connect("doctree-resolved", _process_doctree)
    return {
        "version": "2.0",
        "parallel_read_safe": True,
    }
