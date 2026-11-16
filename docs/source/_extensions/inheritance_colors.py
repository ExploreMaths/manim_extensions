# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Custom Sphinx extension to color inheritance diagram nodes by module origin.

Manim Extensions classes get a distinct fill color from base Manim classes
so users can tell them apart at a glance.  The two colours are Furo's own
admonition colours: manim uses --color-admonition-title--seealso (#448AFF,
tint #DAE8FF = rgba(68,138,255,.2) over white) and manim_extensions
--color-admonition-title--important (#00BFA5, tint #CCF2ED).  Furo keeps
these variables theme-independent, so light and dark share the same
values; the dark canvas look comes from responsiveSvg.js re-applying the
rgba tints over the dark SVG background.

Large diagrams are also rewritten into a bidirectional layout: some
disconnected components grow left-to-right, others grow right-to-left, while
the arrow still points at the child.  A parent never emits children on both
sides.  The whole graph therefore reads as one continuous layout instead of
separate packed blocks; classes with no inheritance edge are omitted because
they carry no relationship to draw.
"""

from __future__ import annotations

import re
from collections import defaultdict

from sphinx.ext.inheritance_diagram import InheritanceGraph

_EXTENSIONS_FILL = "#CCF2ED"
_EXTENSIONS_FONT = "#00BFA5"
_MANIM_FILL = "#DAE8FF"
_MANIM_FONT = "#448AFF"

# Only the Reference Manual's full-library graph is large enough for this
# treatment.  Every other inheritance diagram keeps the usual left-to-right
# layout.  The full graph currently has ~215 nodes; the next largest diagram
# is well below this cutoff.
_REFERENCE_MANUAL_GRAPH_THRESHOLD = 100

_EDGE_RE = re.compile(r'^\s*"([^"]+)" -> "([^"]+)" \[(.*)\];\s*$')


def _component_groups(children: dict[str, list[str]]) -> list[set[str]]:
    """Return undirected components of the generated inheritance graph."""
    neighbours: dict[str, set[str]] = defaultdict(set)
    for parent, child_list in children.items():
        for child in child_list:
            neighbours[parent].add(child)
            neighbours[child].add(parent)

    seen: set[str] = set()
    groups: list[set[str]] = []
    for start in neighbours:
        if start in seen:
            continue
        group: set[str] = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            group.add(node)
            stack.extend(neighbours[node])
        groups.append(group)
    return groups


def _make_bidirectional(dot: str) -> str:
    """Orient whole components left-to-right or right-to-left in one layout."""
    lines = dot.split("\n")
    children: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        match = _EDGE_RE.match(line)
        if match:
            children[match.group(1)].append(match.group(2))

    if not children:
        return dot

    node_re = re.compile(r'^\s*"([^"]+)" \[')
    lines = [line for line in lines if not line.strip().startswith("pack")]
    linked = set(children)
    for child_list in children.values():
        linked.update(child_list)

    # A class with no inheritance edge cannot be part of an inheritance graph.
    # Leaving those nodes in produces the tall strip of unrelated classes; drop
    # them so the remaining components can share one continuous layout.
    lines = [
        line
        for line in lines
        if not (node_re.match(line) and node_re.match(line).group(1) not in linked)
    ]

    groups = _component_groups(children)
    groups.sort(key=lambda group: (-len(group), min(group)))

    # Alternate the growth direction between components.  Every edge inside a
    # component follows that component's direction, so a parent still has all
    # of its children on one side instead of radiating in both directions.
    reversed_nodes: set[str] = set()
    for index, group in enumerate(groups):
        if index % 2:
            reversed_nodes.update(group)

    result: list[str] = []
    for line in lines:
        match = _EDGE_RE.match(line)
        if not match:
            result.append(line)
            continue
        parent, child, attrs = match.groups()
        if parent in reversed_nodes:
            attrs = f"{attrs}, dir=back" if attrs else "dir=back"
            result.append(f'  "{child}" -> "{parent}" [{attrs}];')
        else:
            result.append(line)

    return "\n".join(result)


def _generate_dot_with_colors(self, *args, **kwargs):
    color_map = {}
    for cls_name, fullname, bases, tooltip in self.class_info:
        module = fullname.rsplit(".", 1)[0] if "." in fullname else fullname
        if module.startswith("manim_extensions"):
            color_map[cls_name] = (_EXTENSIONS_FILL, _EXTENSIONS_FONT)
        elif module.startswith("manim"):
            color_map[cls_name] = (_MANIM_FILL, _MANIM_FONT)

    dot = self._original_generate_dot(*args, **kwargs)

    if not color_map:
        return dot

    lines = dot.split("\n")
    result = []
    for line in lines:
        if "[" in line and "->" not in line:
            try:
                node_id = line.strip().split('"')[1]
            except IndexError:
                result.append(line)
                continue
            if node_id in color_map:
                fill, font = color_map[node_id]
                line = line.replace("fillcolor=white", f'fillcolor="{fill}"', 1)
                line = line.replace("fontsize=", f'fontcolor="{font}"fontsize=', 1)
        result.append(line)

    dot = "\n".join(result)
    if len(self.class_info) >= _REFERENCE_MANUAL_GRAPH_THRESHOLD:
        dot = _make_bidirectional(dot)
    return dot


def setup(app):
    InheritanceGraph._original_generate_dot = InheritanceGraph._generate_dot
    InheritanceGraph._generate_dot = _generate_dot_with_colors
    InheritanceGraph._original_generate_dot_public = InheritanceGraph.generate_dot
    InheritanceGraph.generate_dot = _generate_dot_with_colors
    return {"version": "1.0", "parallel_read_safe": True}
