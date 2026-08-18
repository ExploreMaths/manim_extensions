"""Custom Sphinx extension to color inheritance diagram nodes by module origin.

Manim Extensions classes get a distinct fill color from base Manim classes
so users can tell them apart at a glance.
"""

from sphinx.ext.inheritance_diagram import InheritanceGraph

_EXTENSIONS_FILL = "#D5F5E3"
_EXTENSIONS_FONT = "#1E8449"
_MANIM_FILL = "#EBF5FB"
_MANIM_FONT = "#1A5276"


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

    return "\n".join(result)


def setup(app):
    InheritanceGraph._original_generate_dot = InheritanceGraph._generate_dot
    InheritanceGraph._generate_dot = _generate_dot_with_colors
    InheritanceGraph._original_generate_dot_public = InheritanceGraph.generate_dot
    InheritanceGraph.generate_dot = _generate_dot_with_colors
    return {"version": "1.0", "parallel_read_safe": True}