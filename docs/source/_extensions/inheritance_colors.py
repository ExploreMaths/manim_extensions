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

Large diagrams are also rewritten into a bidirectional layout: each parent
keeps some children on its right and moves the rest to its left, with the
arrow still pointing at the child.  Disconnected components are packed into
columns so a handful of standalone classes no longer form one tall strip.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from functools import lru_cache

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


def _connected_components(children: dict[str, list[str]]) -> int:
    """Count undirected components in the generated inheritance graph."""
    neighbours: dict[str, set[str]] = defaultdict(set)
    for parent, child_list in children.items():
        for child in child_list:
            neighbours[parent].add(child)
            neighbours[child].add(parent)

    seen: set[str] = set()
    count = 0
    for start in neighbours:
        if start in seen:
            continue
        count += 1
        stack = [start]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            stack.extend(neighbours[node])
    return count


def _make_bidirectional(dot: str) -> str:
    """Split children around each parent and pack disconnected components."""
    lines = dot.split("\n")
    children: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        match = _EDGE_RE.match(line)
        if match:
            children[match.group(1)].append(match.group(2))

    if not children:
        return dot

    @lru_cache(maxsize=None)
    def descendant_count(node: str) -> int:
        seen: set[str] = set()
        stack = list(children[node])
        while stack:
            item = stack.pop()
            if item in seen:
                continue
            seen.add(item)
            stack.extend(children[item])
        return len(seen)

    # Assign a stable side to each node.  A child shared by several parents
    # keeps whichever side it got first; the remaining edges simply follow it.
    side: dict[str, str] = {}
    for parent in sorted(children, key=lambda item: -len(children[item])):
        ordered = sorted(
            children[parent], key=lambda child: (-descendant_count(child), child)
        )
        left_weight = right_weight = 0
        for child in ordered:
            weight = descendant_count(child) + 1
            current = side.get(child)
            if current is None:
                current = "left" if left_weight <= right_weight else "right"
                side[child] = current
            if current == "left":
                left_weight += weight
            else:
                right_weight += weight

    result: list[str] = []
    for line in lines:
        match = _EDGE_RE.match(line)
        if not match:
            result.append(line)
            continue
        parent, child, attrs = match.groups()
        if side.get(child) == "left":
            attrs = f"{attrs}, dir=back" if attrs else "dir=back"
            result.append(f'  "{child}" -> "{parent}" [{attrs}];')
        else:
            result.append(line)

    components = _connected_components(children)
    if components > 1:
        # More components than this turns labels into unreadable noise; three
        # columns keep standalone classes close to their current visual size.
        columns = min(3, max(2, math.ceil(math.sqrt(components))))
        for index, line in enumerate(result):
            if line.startswith("digraph "):
                result[index + 1 : index + 1] = [
                    "  pack=true;",
                    f'  packmode="array_c{columns}";',
                ]
                break

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
