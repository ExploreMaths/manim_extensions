"""Custom Sphinx extension to color inheritance diagram nodes by module origin.

Manim Extensions classes get a distinct fill color from base Manim classes
so users can tell them apart at a glance.  The two colours are Furo's own
admonition colours: manim uses --color-admonition-title--seealso (#448AFF,
tint #DAE8FF = rgba(68,138,255,.2) over white) and manim_extensions
--color-admonition-title--important (#00BFA5, tint #CCF2ED).  Furo keeps
these variables theme-independent, so light and dark share the same
values; the dark canvas look comes from responsiveSvg.js re-applying the
rgba tints over the dark SVG background.
"""

from sphinx.ext.inheritance_diagram import InheritanceGraph

_EXTENSIONS_FILL = "#CCF2ED"
_EXTENSIONS_FONT = "#00BFA5"
_MANIM_FILL = "#DAE8FF"
_MANIM_FONT = "#448AFF"


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