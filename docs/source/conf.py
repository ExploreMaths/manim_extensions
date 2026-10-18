# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""Sphinx configuration for manim_extensions documentation."""

from manim import Mobject, VMobject
import importlib
import os
import sys

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("_extensions"))

# Reuse CI-pre-rendered example media on Read the Docs instead of rendering
# every example during the build (see .github/workflows/docs-cache.yml and
# workflow/render_doc_examples.py). Examples missing from the cache still
# render normally as a fallback.
if os.environ.get("READTHEDOCS") == "True" and os.path.isdir("/tmp/rtd-cache"):
    os.environ["MANIM_MEDIA_CACHE_DIR"] = "/tmp/rtd-cache"

# -- Project information -----------------------------------------------------
project = "manim_extensions"
copyright = "2026, ExploreMaths"
author = "ExploreMaths"
release = "1.0.5"
version = "1.0.5"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "myst_parser",
    "sphinx_design",
    "manim_directive",
    "nbcell_directive",
    "autodoc_all",
    "inheritance_colors",
    "inline_link_colors",
    "autodoc_inheritance",
    "deprecated_warning",
    "vendored_status",
]

templates_path = ["_templates"]
exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_favicon = "_static/favicon.svg"
html_title = f"Manim Extensions v{release}"
html_short_title = "manim_extensions"

html_theme_options = {
    "source_repository": "https://github.com/ExploreMaths/manim_extensions/",
    "source_branch": "main",
    "source_directory": "docs/source/",
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
        "color-inline-code-background": "#262626",
        "color-foreground-secondary": "#ffffffd9",
    },
}

# -- Extension configuration -------------------------------------------------

# autodoc
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
}
# Instance constants (e.g. Zr = MCElement(...)) must not display the class
# docstring: show a docstring only when the object itself defines one.
autodoc_inherit_docstrings = False
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_typehints_format = "short"

# manim 0.22 annotates Scene.__init__ as ``CairoRenderer | OpenGLRenderer``
# under ``from __future__ import annotations``; sphinx-autodoc-typehints'
# guarded import then evaluates ``type | str`` and raises
# ``TypeError: unsupported operand type(s) for |`` on every build.  This
# lives in third-party code, so suppress the specific warning class
# rather than the whole typehints machinery.
suppress_warnings = ["sphinx_autodoc_typehints.guarded_import"]

# sphinx-copybutton: keep nbcell/manim prompts ("In [1]:", "$") out of the
# copied text; the buttons themselves are hidden on prompts by nbcell.css.
copybutton_exclude = ".linenos, .gp, .prompt"

# myst-parser: generate heading anchors so that in-document links like
# ``[text](#getting-started)`` resolve to local headings instead of
# falling through to intersphinx (which can match unrelated labels).
myst_heading_anchors = 3

# sphinx_autodoc_typehints: emit short names with leading "~" so intersphinx
# resolves them to :py:class: references displaying just the class name.
typehints_fully_qualified = False

# Collapse selected union aliases instead of expanding every member type.
# ``ParsableManimColor`` is a bare ``types.UnionType`` (manim assigns
# ``ParsableManimColor = str | int | ManimColor | ...``), so the typehints
# formatter cannot recover its name at runtime and would otherwise render a
# parameter as a 15-item union. ``typehints_formatter`` is the extension's
# official per-annotation hook: return a reST string to override rendering.
# The four ``manim_extensions.algorithm.node`` aliases are likewise bare
# objects at runtime (``Vector3D is manim.typing.Vector3DLike`` etc.), and
# sphinx-autodoc-typehints would otherwise expand them into
# ``GenericAlias[numpy.double]``-style numpy 2.x scalar text.  Each value is
# the dotted path of the *project* alias, so the rendered reference resolves
# to the local ``.. autodata::`` entry on the algorithm constants page and
# displays the project name.  Matching is deliberately layered:
# identity first (true alias annotations), then flattened unions (Python
# flattens ``ParsableManimColor | None`` into its atomic members, so the
# alias object itself is no longer present), then structural equality
# (``Point3DLike`` and ``Vector3DLike`` are separate objects with
# identical members; one name per object, the project alias wins).
# ``numpy.typing.NDArray`` generics are handled separately because the
# plugin mis-renders them as ``GenericAlias[...]``.
import types as _types
import typing as _typing

_TYPE_ALIASES = {
    "ParsableManimColor": "manim.utils.color.core.ParsableManimColor",
    "NodeValue": "manim_extensions.algorithm.node.NodeValue",
    "NodeBoxType": "manim_extensions.algorithm.node.NodeBoxType",
    "Vector3D": "manim_extensions.algorithm.node.Vector3D",
    "Point3D": "manim_extensions.algorithm.node.Point3D",
}


def _resolve_alias(_dotted):
    _module, _, _attr = _dotted.rpartition(".")
    return getattr(importlib.import_module(_module), _attr)


def _simple_type_repr(x):
    if x is _typing.Any:
        return ":py:obj:`~typing.Any`"
    if x is type(None):
        return ":py:obj:`None`"
    if isinstance(x, type):
        _mod = x.__module__
        _q = x.__qualname__
        if _mod == "builtins":
            return f":py:obj:`{_q}`"
        return f":py:obj:`~{_mod}.{_q}`"
    return str(x)


def _typehints_formatter(annotation, *args):
    for _name, _dotted in _TYPE_ALIASES.items():
        try:
            _target = _resolve_alias(_dotted)
        except Exception:
            continue
        if annotation is _target:  # exact alias object
            return f":py:obj:`~{_dotted}`"
        if isinstance(annotation, _types.UnionType) and isinstance(_target, _types.UnionType):
            _ann = set(annotation.__args__)
            _tgt = set(_target.__args__)
            if _tgt <= _ann and _ann - _tgt <= {type(None)}:
                _none = " | :py:obj:`None`" if _ann - _tgt else ""
                return f":py:obj:`~{_dotted}`{_none}"
        # Structural match (the typehints plugin rebuilds annotations via
        # ``get_all_type_hints``, so identity is lost for every alias; the
        # rebuilt ``NDArray[numpy.float64]`` is equal to ``Point3D`` etc.).
        if annotation == _target:
            return f":py:obj:`~{_dotted}`"
    # numpy 2.x: ``numpy.typing.NDArray`` is a TypeAliasType; the plugin
    # renders ``NDArray[...]`` generics as ``GenericAlias[...]``.  Only
    # reaches here for args that do not structurally match ``Point3D``
    # (``NDArray[numpy.float64]``), e.g. ``NDArray[Any]``.
    _origin = getattr(annotation, "__origin__", None)
    if (
        type(annotation) is _types.GenericAlias
        and isinstance(_origin, _typing.TypeAliasType)
        and getattr(_origin, "__name__", None) == "NDArray"
        and getattr(_origin, "__module__", "").startswith("numpy")
    ):
        _args = ", ".join(_simple_type_repr(a) for a in annotation.__args__)
        # ``\ \[`` mirrors the plugin's own generic-args escaping (a bare
        # ``[`` right after a role would be mis-parsed as reference suffix).
        return f":py:obj:`~numpy.typing.NDArray`\\ \\[{_args}]"
    return None


typehints_formatter = _typehints_formatter

# napoleon (Google / NumPy style docstrings)
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
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
    "splines": "spline",
    "concentrate": "true",
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
    "pymunk": ("https://www.pymunk.org/en/latest/", None),
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


# -- autodoc: drop inherited class docstrings on instance constants -------------
#
# Instance constants (e.g. ``Zr = MCElement(...)``) cannot define their own
# ``__doc__`` attribute; ``inspect.getdoc`` falls back to the class docstring.
# ``autodoc_inherit_docstrings = False`` does not prevent this, because the
# fallback happens before autodoc's own MRO walk. Clear the docstring only when
# it matches the owning type's docstring, so ``#:`` source comments are kept.
#
# Priority 0 runs this handler before sphinx.ext.napoleon (priority 500), so
# the lines are still the raw docstring and the string comparison matches.
def _drop_inherited_instance_docstring(app, what, name, obj, options, lines):
    if what != "data" or isinstance(obj, type) or callable(obj):
        return
    type_doc = inspect.getdoc(type(obj)) or ""
    rendered = "\n".join(lines).strip()
    # The instance's ``__doc__`` falls back to the owning type's docstring,
    # but numpy versions can differ between the instance attribute (e.g. the
    # two-signature ndarray docstring with a ``--`` separator) and the one
    # ``inspect.getdoc`` returns, so match containment rather than equality.
    if rendered.startswith(type_doc) or type_doc in rendered:
        lines.clear()


def setup(app):
    app.connect(
        "autodoc-process-docstring",
        _drop_inherited_instance_docstring,
        priority=0,
    )
