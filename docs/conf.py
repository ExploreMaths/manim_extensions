"""Sphinx configuration for manim_extensions documentation."""

import os
import sys

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("_extensions"))
sys.path.insert(0, os.path.abspath("../third_party/manim-GearBox/src"))
sys.path.insert(0, os.path.abspath("../third_party/manim-mindmap/src"))
sys.path.insert(0, os.path.abspath("../third_party/manim-compass/src"))

# -- Project information -----------------------------------------------------
project = "manim_extensions"
copyright = "2026, ExploreMaths"
author = "ExploreMaths"
release = "1.0.3"
version = "1.0.3"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "manim_directive",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_favicon = "_static/favicon.svg"
html_title = f"Manim Extensions v{release}"
html_short_title = "manim_extensions"

html_theme_options = {
    "source_repository": "https://github.com/ExploreMaths/manim_extensions/",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_logo": "logo.svg",
    "dark_logo": "logo-dark.svg",
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "light_css_variables": {
        "font-stack--headings": "Georgia, serif",
        "color-content-foreground": "#000000",
        "color-background-primary": "#ffffff",
        "color-background-border": "#ffffff",
        "color-sidebar-background": "#f8f9fb",
        "color-brand-content": "#1c00e3",
        "color-brand-primary": "#192bd0",
        "color-link": "#c93434",
        "color-link--hover": "#5b0000",
        "color-inline-code-background": "#f6f6f6",
        "color-foreground-secondary": "#000",
    },
    "dark_css_variables": {
        "color-content-foreground": "#ffffffd9",
        "color-background-primary": "#131416",
        "color-background-border": "#303335",
        "color-sidebar-background": "#1a1c1e",
        "color-brand-content": "#2196f3",
        "color-brand-primary": "#007fff",
        "color-link": "#51ba86",
        "color-link--hover": "#9cefc6",
        "color-inline-code-background": "#262626",
        "color-foreground-secondary": "#ffffffd9",
    },
}

# -- Extension configuration -------------------------------------------------

# autodoc
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# napoleon (Google / NumPy style docstrings)
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# inheritance_graph settings (matching Manim Community documentation)
inheritance_graph_attrs = {
    "size": '""',
    "splines": "polyline",
    "nodesep": 0.15,
    "ranksep": 0.3,
}

inheritance_node_attrs = {
    "penwidth": 0,
    "shape": "box",
    "width": 0.05,
    "height": 0.05,
    "margin": 0.05,
}

inheritance_edge_attrs = {
    "penwidth": 1,
}

graphviz_output_format = "svg"

# Locate the Graphviz ``dot`` executable.  On Windows it is often installed
# outside the PATH (e.g. ``C:\Program Files\Graphviz\bin``); on Linux /
# ReadTheDocs the system package installs it into the PATH as ``dot``.
import shutil

_dot_candidates = [
    shutil.which("dot"),
    r"C:\Program Files\Graphviz\bin\dot.exe",
    r"C:\Program Files (x86)\Graphviz\bin\dot.exe",
]
graphviz_dot = next((p for p in _dot_candidates if p and os.path.isfile(p)), "dot")

html_js_files = ["responsiveSvg.js"]

# intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "manim": ("https://docs.manim.community/en/stable/", None),
    "pillow": ("https://pillow.readthedocs.io/en/stable/", None),
}

# -- Custom roles ------------------------------------------------------------
rst_epilog = """
.. |pypi| replace:: `PyPI <https://pypi.org/project/manim_extensions/>`__
.. |github| replace:: `GitHub <https://github.com/ExploreMaths/manim_extensions>`__
"""

html_css_files = ["custom.css"]

latex_engine = "lualatex"


# -- autodoc: skip inherited Mobject attributes --------------------------------

import inspect


def _manim_mobject_attribute_names():
    """Return public, non-callable attribute names inherited from Manim Mobjects."""
    try:
        from manim.mobject.mobject import Mobject
        from manim.mobject.types.vectorized_mobject import VMobject

        attrs = set()
        for cls in (Mobject, VMobject):
            try:
                instance = cls()
                for name in dir(instance):
                    if name.startswith("_"):
                        continue
                    value = getattr(instance, name, None)
                    if not callable(value) and not inspect.isroutine(value):
                        attrs.add(name)
            except Exception:
                pass
        return attrs
    except Exception:
        return set()


_MANIM_MOBJECT_ATTRS = _manim_mobject_attribute_names()

# Update autodoc defaults to hide inherited Manim attributes (e.g. background_stroke_color).
autodoc_default_options["exclude-members"] = ",".join(sorted(_MANIM_MOBJECT_ATTRS))

