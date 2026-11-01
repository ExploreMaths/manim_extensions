"""Custom Sphinx extension: structural fixes for class documentation.

Inline-code cross-reference links no longer get custom colors — they use
Furo's native link color.  Coloring is limited to the inheritance graph
(see :mod:`inheritance_colors` + ``responsiveSvg.js``).  This extension
only keeps the two structure fixes that autodoc needs:

- :func:`_drop_auto_attribute_members` removes inherited attribute
  members unless the class redefines them (they produce a bare
  Attributes block with anchors that nothing links to);
- :func:`_prune_toc_entries` drops the corresponding "On this page"
  entries, because Sphinx's toc collector runs at ``doctree-read`` —
  before this extension's ``doctree-resolved`` pruning — so the sidebar
  would otherwise keep dangling anchors;
- :func:`_add_attribute_headings` inserts an ``Attributes`` rubric heading
  before a class's rendered attribute members and moves the block in front
  of a preceding Examples section.
"""

import re

from docutils import nodes
from sphinx.addnodes import desc, desc_content, desc_signature


def _drop_auto_attribute_members(doctree):
    """Remove inherited attribute members unless the class redefines them.

    autodoc ``members`` collects inherited public attributes (e.g.
    ``NerdFontIcon.t2c`` from ``Text``) even when the class never
    redefines them, producing bare ``Attributes`` blocks with anchors
    nothing links to.  An attribute is kept only when the class defines
    it itself — its name is in the class's own ``__dict__`` (or
    ``__slots__``).  Inherited names are dropped for every class,
    regardless of whether the docstring has an ``Attributes`` section:
    a redefined attribute is real API surface, a merely inherited one is
    not.
    """
    import importlib

    dropped: set[str] = set()
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
        except Exception:
            continue
        own = set(getattr(cls, "__dict__", {}))
        slots = getattr(cls, "__slots__", None)
        if slots:
            own.update(s for s in slots if isinstance(s, str))
        content = next(
            (c for c in d.children if isinstance(c, desc_content)), None
        )
        if content is None:
            continue
        for c in list(content.children):
            if not (isinstance(c, desc) and "attribute" in c.get("classes", ())):
                continue
            # autodoc's id for an attribute member is
            # ``<class dotted>.<name>``; if the name is not defined by the
            # class itself it comes from a base class and is dropped.
            # Guard against odd id shapes (no dot / module-level).
            attr_id = c.get("ids") or (
                next(
                    (s.get("ids") for s in c.findall(desc_signature) if s.get("ids")),
                    None,
                )
            )
            if not attr_id:
                continue
            name = attr_id[0].rpartition(".")[2]
            if name and name in own:
                continue
            content.remove(c)
            dropped.add(attr_id[0])
    return dropped


_dropped_by_doc: dict[str, set[str]] = {}


def _process_doctree(app, doctree, docname):
    dropped = _drop_auto_attribute_members(doctree)
    if dropped:
        _dropped_by_doc[docname] = dropped
    _add_attribute_headings(doctree)


def _prune_toc_entries(app, pagename, templatename, context, doctree):
    """Remove dropped attribute anchors from the rendered page toc.

    Sphinx's toc collector runs at ``doctree-read`` — before autodoc's
    members are pruned here (``doctree-resolved``) — so the "On this
    page" sidebar keeps entries for attributes whose body anchors were
    removed.  Strip those ``<li>`` entries (and any emptied parent
    ``<ul>``) from ``context['toc']`` at ``html-page-context``, just
    before the template renders the page.
    """
    dropped = _dropped_by_doc.get(pagename)
    if not dropped:
        return
    toc = context.get("toc")
    if not toc:
        return
    new_toc = toc
    for name in dropped:
        pattern = re.compile(
            r'<li><a[^>]*href="#' + re.escape(name) + r'"[^>]*>.*?</a></li>',
            re.S,
        )
        new_toc = pattern.sub("", new_toc)
    while True:
        pruned = re.sub(r"<ul>\s*</ul>", "", new_toc)
        if pruned == new_toc:
            break
        new_toc = pruned
    if new_toc != toc:
        context["toc"] = new_toc


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
    app.connect("html-page-context", _prune_toc_entries)
    return {
        "version": "2.0",
        "parallel_read_safe": True,
    }
