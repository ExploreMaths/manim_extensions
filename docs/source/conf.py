# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Sphinx configuration for manim_extensions documentation."""

from manim import Mobject, VMobject
import ast
import importlib
import inspect
import os
import sys

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, os.path.abspath("../.."))
sys.path.insert(0, os.path.abspath("_extensions"))

# Workaround for a manim 0.21/0.22 camera regression that fails every
# ImageMobject render ("Invalid mode for data type"). Applied before any
# .. manim:: example is rendered.
from manim_image_patch import apply_manim_image_patch

apply_manim_image_patch()

# Manim's ``_AnimationBuilder`` has no docstring, so autosummary would list it
# with an empty summary.  The class is part of the documentation supplement
# because the official reference does not expose it; add the short summary the
# builder page and the Classes table need without modifying Manim.
try:
    from manim.mobject.mobject import _AnimationBuilder as _ManimAnimationBuilder

    if not _ManimAnimationBuilder.__doc__:
        _ManimAnimationBuilder.__doc__ = (
            "Fluent proxy returned by ``mobject.animate``; it records method "
            "calls and builds the real animation when passed to ``play``."
        )
except Exception:
    pass

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
release = "1.0.7"
version = "1.0.7"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "myst_parser",
    "sphinx_design",
    "manim_directive",
    "nbcell_directive",
    "autodoc_all",
    "dataclass_label",
    "inheritance_colors",
    "inline_link_colors",
    "default_value_links",
    "preserve_attribute_defaults",
    "autodoc_inheritance",
    "deprecated_warning",
    "vendored_status",
    "reference_module_index",
]

templates_path = ["_templates"]
exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
html_favicon = "_static/favicon.svg"
# Self-host MathJax (vendored under _static/mathjax) instead of loading it
# from the jsdelivr CDN: the CDN is intermittently unreachable from some
# regions, which made formulas randomly fail to render.  The SVG output
# component is used because MathJax 4's CHTML output loads its math fonts
# from a separate package (chtml/woff2) that would also need vendoring.
mathjax_path = "mathjax/tex-mml-svg.js"
html_title = f"Manim Extensions v{release}"
html_short_title = "manim_extensions"

# Render TODO comments produced by sphinx.ext.todo into the docs instead of dropping them
todo_include_todos = True

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
        "color-sidebar-background": "#f8f9fb",
        "color-foreground-secondary": "#000",
    },
    "dark_css_variables": {
        "color-content-foreground": "#ffffffd9",
        "color-background-primary": "#131416",
        "color-background-border": "#303335",
        "color-sidebar-background": "#1a1c1e",
        "color-foreground-secondary": "#ffffffd9",
    },
}

# -- Extension configuration -------------------------------------------------

# autodoc
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    # Document private (single-underscore) members as well, so that helpers
    # and module internals are visible instead of being silently dropped.
    "private-members": True,
}
# Instance constants (e.g. Zr = MCElement(...)) must not display the class
# docstring: show a docstring only when the object itself defines one.
autodoc_inherit_docstrings = False
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_typehints_format = "short"

# Keep the source spelling of default values (``color=WHITE``) instead of
# repr-ing them (``color=ManimColor('#FFFFFF')``) so signatures stay short
# and the names stay recognisable.
autodoc_preserve_defaults = True

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
    # ``manim_extensions.algorithm.node`` re-exports these names from
    # ``manim.typing`` (``Vector3D is manim.typing.Vector3DLike``), so the
    # rendered reference must point at Manim's own inventory entry —
    # the project has no ``autodata`` anchor for an imported name.
    "Vector3D": "manim.typing.Vector3D",
    "Point3D": "manim.typing.Point3D",
    # ``Point3DLike`` / ``Vector3DLike`` are unions expanded by
    # ``typing.get_type_hints`` into ``Point3D | tuple[...]``; we patch
    # the plugin below to hand the formatter the alias object itself (kept
    # from ``__annotations__``) so the reference shows the alias name and
    # links to Manim's own inventory entry.
    "Point3DLike": "manim.typing.Point3DLike",
    "Vector3DLike": "manim.typing.Vector3DLike",
}


def _is_type_alias(_obj):
    if inspect.isclass(_obj):
        return False
    if isinstance(_obj, _typing.TypeVar):
        return False
    if isinstance(_obj, (_types.GenericAlias, _types.UnionType)):
        return True
    if isinstance(_obj, getattr(_typing, "TypeAliasType", ())):
        return True
    return _typing.get_origin(_obj) is not None


def _resolve_alias(_dotted):
    _module, _, _attr = _dotted.rpartition(".")
    return getattr(importlib.import_module(_module), _attr)


def _dotted_name(_node):
    """Return the dotted name represented by a ``Name``/``Attribute`` node."""
    if isinstance(_node, ast.Name):
        return _node.id
    if isinstance(_node, ast.Attribute):
        _base = _dotted_name(_node.value)
        return f"{_base}.{_node.attr}" if _base else None
    return None


_ALIAS_DEFINED_NAMES = {}


def _module_defined_names(_mod):
    """Top-level assignment names of *mod*, cached for alias lookup."""
    _key = _mod.__name__
    if _key in _ALIAS_DEFINED_NAMES:
        return _ALIAS_DEFINED_NAMES[_key]
    _names = set()
    _path = getattr(_mod, "__file__", None)
    if _path and str(_path).endswith(".py"):
        try:
            _tree = ast.parse(open(_path, encoding="utf-8").read())
        except (OSError, SyntaxError, UnicodeDecodeError):
            _tree = None
        if _tree is not None:
            for _node in _tree.body:
                if isinstance(_node, ast.Assign):
                    _names.update(
                        _target.id
                        for _target in _node.targets
                        if isinstance(_target, ast.Name)
                    )
                elif isinstance(_node, ast.AnnAssign) and isinstance(
                    _node.target, ast.Name
                ):
                    _names.add(_node.target.id)
    _ALIAS_DEFINED_NAMES[_key] = _names
    return _names


def _canonical_alias_dotted(_alias, _fallback):
    """Return the dotted path of the module that actually defines *alias*.

    A type alias is often re-exported (``manim.utils.color`` exposes
    ``ParsableManimColor`` from ``manim.utils.color.core``).  Sphinx must link
    to the defining module, not the import site, so try the project modules,
    then the modules below the import path.
    """
    for _dotted in _TYPE_ALIASES.values():
        try:
            if _resolve_alias(_dotted) is _alias:
                return _dotted
        except Exception:
            continue
    for _name, _mod in list(sys.modules.items()):
        if not _name.startswith("manim_extensions.") or hasattr(_mod, "__path__"):
            continue
        for _attr in _module_defined_names(_mod):
            if getattr(_mod, _attr, None) is _alias:
                return f"{_name}.{_attr}"
    _module_name, _, _attr = _fallback.rpartition(".")
    if not _module_name:
        return _fallback
    try:
        _mod = importlib.import_module(_module_name)
    except Exception:
        return _fallback
    if getattr(_mod, _attr, None) is _alias:
        # The import path is a defining module (``manim.typing.Point3D``).
        # For a pure re-export the loop below finds the real definition.
        if _module_name in {
            _dotted.rpartition(".")[0] for _dotted in _TYPE_ALIASES.values()
        }:
            return _fallback
    _path = getattr(_mod, "__path__", None)
    if _path:
        import pkgutil

        for _info in pkgutil.walk_packages(_path, _mod.__name__ + "."):
            try:
                _sub = importlib.import_module(_info.name)
            except Exception:
                continue
            if getattr(_sub, _attr, None) is _alias:
                return f"{_sub.__name__}.{_attr}"
    if getattr(_mod, _attr, None) is _alias:
        return _fallback
    return _fallback


# Aliases discovered from annotations, keyed by object id so equal but distinct
# aliases (``Point3D`` / ``Vector3D``) keep their own names.  Each entry keeps
# the alias alive to make the id stable.
_ALIAS_REGISTRY = {}


def _alias_priority(_dotted):
    if _dotted in _TYPE_ALIASES.values():
        return 3
    if _dotted.startswith("manim_extensions."):
        return 2
    return 1


def _register_alias(_alias, _dotted):
    if not _is_type_alias(_alias):
        return None
    _dotted = _canonical_alias_dotted(_alias, _dotted)
    _entry = (_alias, _dotted, _alias_priority(_dotted))
    _previous = _ALIAS_REGISTRY.get(id(_alias))
    if _previous is None or _entry[2] >= _previous[2]:
        _ALIAS_REGISTRY[id(_alias)] = _entry
    return _ALIAS_REGISTRY[id(_alias)]


def _seed_alias_registry():
    for _dotted in _TYPE_ALIASES.values():
        try:
            _register_alias(_resolve_alias(_dotted), _dotted)
        except Exception:
            continue


class _AliasMarker:
    """Metadata attached to an annotation to preserve its source alias name.

    ``typing`` caches and flattens equivalent unions, so ``Optional[Point3DLike]``
    and ``Optional[Vector3DLike]`` can end up as the same object.  ``Annotated``
    gives each parameter its own wrapper, and the wrapper cannot be confused
    with another annotation that has the same members.
    """

    __slots__ = ("dotted", "optional")

    def __init__(self, dotted, optional):
        self.dotted = dotted
        self.optional = optional


def _register_annotation_value(_value, _obj):
    """Register any alias objects still present in an evaluated annotation."""
    _module_name = getattr(_obj, "__module__", "")
    _mod = sys.modules.get(_module_name)
    if _mod is None:
        return
    _origins = _module_import_origins(_mod)
    _stack = [_value]
    while _stack:
        _current = _stack.pop()
        if _is_type_alias(_current):
            for _name, _candidate in vars(_mod).items():
                if _candidate is _current:
                    _register_alias(
                        _current,
                        _origins.get(_name, f"{_mod.__name__}.{_name}"),
                    )
                    break
        _stack.extend(_typing.get_args(_current))


_IMPORT_ORIGINS = {}
_MODULE_ANNOTATION_TEXTS = {}


def _module_annotation_texts(_mod):
    """Return ``qualname -> {annotation name: source text}`` for *mod*."""
    _key = getattr(_mod, "__name__", "")
    if _key in _MODULE_ANNOTATION_TEXTS:
        return _MODULE_ANNOTATION_TEXTS[_key]
    _result = {}
    _path = getattr(_mod, "__file__", None)
    if _path and str(_path).endswith(".py"):
        try:
            _tree = ast.parse(open(_path, encoding="utf-8").read())
        except (OSError, SyntaxError, UnicodeDecodeError):
            _tree = None
        if _tree is not None:

            def _record_function(_node, _prefix):
                _annotations = {}
                _args = [
                    *_node.args.posonlyargs,
                    *_node.args.args,
                    *_node.args.kwonlyargs,
                ]
                if _node.args.vararg is not None:
                    _args.append(_node.args.vararg)
                if _node.args.kwarg is not None:
                    _args.append(_node.args.kwarg)
                for _arg in _args:
                    if _arg.annotation is not None:
                        _annotations[_arg.arg] = ast.unparse(_arg.annotation)
                if _node.returns is not None:
                    _annotations["return"] = ast.unparse(_node.returns)
                _result[_prefix + _node.name] = _annotations

            def _record_class(_node, _prefix):
                _annotations = {}
                for _item in _node.body:
                    if isinstance(_item, ast.AnnAssign) and isinstance(
                        _item.target, ast.Name
                    ):
                        _annotations[_item.target.id] = ast.unparse(_item.annotation)
                _result[_prefix + _node.name] = _annotations

            def _visit(_body, _prefix):
                for _node in _body:
                    if isinstance(_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        _record_function(_node, _prefix)
                    elif isinstance(_node, ast.ClassDef):
                        _record_class(_node, _prefix)
                        _visit(_node.body, _prefix + _node.name + ".")
                    elif isinstance(_node, ast.If):
                        _visit(_node.body, _prefix)
                        _visit(_node.orelse, _prefix)
                    elif isinstance(_node, ast.Try):
                        _visit(_node.body, _prefix)
                        for _handler in _node.handlers:
                            _visit(_handler.body, _prefix)
                        _visit(_node.orelse, _prefix)
                        _visit(_node.finalbody, _prefix)

            _visit(_tree.body, "")
    _MODULE_ANNOTATION_TEXTS[_key] = _result
    return _result


def _source_annotation_texts(_obj):
    _mod = sys.modules.get(getattr(_obj, "__module__", ""))
    if _mod is None:
        return {}
    return _module_annotation_texts(_mod).get(getattr(_obj, "__qualname__", ""), {})


def _module_import_origins(_mod):
    """Map a module-level imported name to the dotted path it came from."""
    _key = _mod.__name__
    if _key in _IMPORT_ORIGINS:
        return _IMPORT_ORIGINS[_key]
    _origins = {}
    _path = getattr(_mod, "__file__", None)
    if _path and str(_path).endswith(".py"):
        try:
            _tree = ast.parse(open(_path, encoding="utf-8").read())
        except (OSError, SyntaxError, UnicodeDecodeError):
            _tree = None
        if _tree is not None:
            for _node in ast.walk(_tree):
                if isinstance(_node, ast.ImportFrom):
                    if _node.level or not _node.module:
                        continue
                    for _alias in _node.names:
                        _origins[_alias.asname or _alias.name] = (
                            f"{_node.module}.{_alias.name}"
                        )
                elif isinstance(_node, ast.Import):
                    for _alias in _node.names:
                        _origins[_alias.asname or _alias.name.split(".")[0]] = (
                            _alias.name
                        )
    _IMPORT_ORIGINS[_key] = _origins
    return _origins


def _alias_from_annotation_string(_src, _obj):
    """Evaluate a postponed annotation string, preserving alias identities."""
    try:
        _node = ast.parse(_src.strip(), mode="eval").body
    except (SyntaxError, ValueError):
        return None
    _module_name = getattr(_obj, "__module__", "")
    _mod = sys.modules.get(_module_name)
    if _mod is None:
        try:
            _mod = importlib.import_module(_module_name)
        except Exception:
            return None
    _ns = vars(_mod)
    _origins = _module_import_origins(_mod)
    _eval_ns = dict(_ns)
    _found = False
    for _sub in ast.walk(_node):
        if not isinstance(_sub, (ast.Name, ast.Attribute)):
            continue
        _dotted = _dotted_name(_sub)
        if not _dotted:
            continue
        if isinstance(_sub, ast.Name):
            _candidate = _ns.get(_sub.id)
            _name = _sub.id
            _dotted_name_value = _origins.get(_name, f"{_mod.__name__}.{_name}")
        else:
            try:
                _candidate = _resolve_alias(_dotted)
            except Exception:
                continue
            _dotted_name_value = _dotted
        if _candidate is not None and _is_type_alias(_candidate):
            _entry = _register_alias(_candidate, _dotted_name_value)
            if isinstance(_sub, ast.Name) and _entry is not None:
                # Keep the alias object visible to the typehints walker even
                # when it sits inside a larger union: ``typing`` flattens
                # ``SurfaceConfig | dict | None`` and would otherwise expand
                # every member of ``SurfaceConfig``.
                _eval_ns[_sub.id] = _typing.Annotated[
                    _candidate,
                    _AliasMarker(_entry[1], False),
                ]
            _found = True
    if not _found:
        return None
    try:
        _value = eval(
            compile(ast.Expression(_node), "<annotation>", "eval"),
            _eval_ns,
            {},
        )
    except Exception:
        return None
    return _value


def _union_args(value):
    """Return the member set of a PEP 604 or ``typing.Union`` annotation."""
    if _typing.get_origin(value) in (_typing.Union, _types.UnionType):
        return set(_typing.get_args(value))
    return None


def _matching_aliases(_annotation):
    """Yield ``(alias entry, optional)`` whose members fit *annotation*."""
    _ann_args = _typing.get_args(_annotation)
    if not _ann_args or _typing.get_origin(_annotation) not in (
        _typing.Union,
        _types.UnionType,
    ):
        return []
    _matches = []
    for _entry in _ALIAS_REGISTRY.values():
        _alias, _dotted, _priority = _entry
        _alias_args = _union_args(_alias)
        if _alias_args is not None:
            _extra = set(_ann_args) - _alias_args
            if _alias_args <= set(_ann_args) and _extra <= {type(None)}:
                _matches.append((_entry, bool(_extra), False))
            continue
        # Non-union aliases survive inside ``Optional[...]`` as the alias
        # object itself (``Point3D``); match by identity so equal aliases
        # such as ``Point3D`` and ``Vector3D`` do not get mixed up.
        for _arg in _ann_args:
            if _arg is _alias:
                _extra = set(_ann_args) - {_arg}
                if _extra <= {type(None)}:
                    _matches.append((_entry, bool(_extra), True))
                break
    return _matches


# Names used only to resolve ambiguous structural ties; alias discovery and
# Optional folding themselves are generic.
_ALIAS_DISPLAY_ORDER = (
    "ParsableManimColor",
    "NodeValue",
    "NodeBoxType",
    "Point3D",
    "Vector3D",
    "Point3DLike",
    "Vector3DLike",
)


def _best_alias_match(_matches):
    if not _matches:
        return None
    _exact = [_match for _match in _matches if _match[2]]
    _pool = _exact or _matches
    _best = max(_match[0][2] for _match in _pool)
    _best = [_match for _match in _pool if _match[0][2] == _best]
    if len(_best) == 1:
        return _best[0]
    _by_name = {_match[0][1]: _match for _match in _best}
    for _name in _ALIAS_DISPLAY_ORDER:
        _dotted = _TYPE_ALIASES.get(_name)
        if _dotted in _by_name:
            return _by_name[_dotted]
    _names = {_match[0][1] for _match in _best}
    if len(_names) == 1:
        return _best[0]
    return None


def _render_alias(_dotted, _optional=False):
    _role = "py:type" if _dotted.startswith("manim_extensions.") else "py:obj"
    _ref = f":{_role}:`~{_dotted}`"
    if _optional:
        return f":py:obj:`~typing.Optional`\\ \\[{_ref}]"
    return _ref


def _simple_type_repr(x):
    if x is getattr(_typing, "Self", object()):
        return ":py:obj:`Self`"
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
    # The source annotation wrapper carries the exact alias name.  This is
    # needed because typing caches/flattens equal unions, so an id-based map
    # cannot distinguish ``Optional[Point3DLike]`` from ``Optional[Vector3DLike]``.
    if _typing.get_origin(annotation) is _typing.Annotated:
        for _metadata in _typing.get_args(annotation)[1:]:
            if isinstance(_metadata, _AliasMarker):
                return _render_alias(_metadata.dotted, _metadata.optional)
    _entry = _ALIAS_REGISTRY.get(id(annotation))
    if _entry is not None:
        return _render_alias(_entry[1])
    _match = _best_alias_match(_matching_aliases(annotation))
    if _match is not None:
        return _render_alias(_match[0][1], _match[1])
    # numpy 2.x: ``numpy.typing.NDArray`` is a TypeAliasType; the plugin
    # renders ``NDArray[...]`` generics as ``GenericAlias[...]``.  Only
    # reaches here for args that do not match a known alias.
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


_seed_alias_registry()

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

html_js_files = [
    "responsiveSvg.js",
    "attributes-single.js",
    "icon_gallery.js",
    "constant_values.js",
]

# intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "manim": ("https://docs.manim.community/en/stable/", None),
    "pillow": ("https://pillow.readthedocs.io/en/stable/", None),
    "pymunk": ("https://www.pymunk.org/en/latest/", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "networkx": ("https://networkx.org/documentation/stable/", None),
    "scikit-learn": ("https://scikit-learn.org/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
    "segno": ("https://segno.readthedocs.io/en/latest/", None),
    "typing_extensions": ("https://typing-extensions.readthedocs.io/en/latest/", None),
}

# -- Custom roles ------------------------------------------------------------
rst_epilog = """
.. |pypi| replace:: `PyPI <https://pypi.org/project/manim_extensions/>`__
.. |github| replace:: `GitHub <https://github.com/ExploreMaths/manim_extensions>`__
"""

html_css_files = ["custom.css", "icon_gallery.css", "constant_values.css"]

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


# -- autodoc: keep private members but drop internals and dunders ------------
#
# ``private-members`` is all-or-nothing in Sphinx: it also un-hides special
# members (``__len__`` ...) and autodoc/ABC bookkeeping attributes such as
# ``_original__init__`` and ``_abc_impl``.  Those are implementation details
# rather than the private API a reader is after, so skip them explicitly.
_INTERNAL_ATTRIBUTES = {"_abc_impl", "_original__init__"}


def _skip_internal_autodoc_member(app, what, name, obj, skip, options):
    """Skip special members and autodoc bookkeeping in private-members mode."""
    # Module pages only render the module docstring.  ``autoall`` sections and
    # member pages own the API listing, so an ``automodule`` directive must
    # not repeat every member after the description.
    if what == "module":
        return True
    short = name.rsplit(".", 1)[-1]
    if short in _INTERNAL_ATTRIBUTES:
        return True
    if short.startswith("__") and short.endswith("__"):
        return True
    return None


def setup(app):
    # Patch sphinx-autodoc-typehints so type aliases are not expanded into
    # their unions.  The original annotation strings are evaluated with the
    # owning module's globals, which keeps the alias objects (and their names)
    # instead of the flattened ``typing.Union[...]`` representation.
    try:
        from sphinx_autodoc_typehints._resolve import hints as _hints_mod
        from sphinx_autodoc_typehints._resolve.evaluate import (
            type_hints as _eval_type_hints,
        )
    except Exception:
        _hints_mod = None
        _eval_type_hints = None

    def _restore_aliases(_hints, _obj):
        _ann = getattr(_obj, "__annotations__", None) or {}
        _sources = None
        for _name, _src in _ann.items():
            if _name not in _hints:
                continue
            if isinstance(_src, str):
                _source = _src.strip()
            else:
                # Modules without ``from __future__ import annotations`` store
                # evaluated annotations, so recover the written annotation
                # from the module AST to keep the alias name.
                if _sources is None:
                    _sources = _source_annotation_texts(_obj)
                _source = _sources.get(_name)
            if _source:
                _value = _alias_from_annotation_string(_source, _obj)
                if _value is not None:
                    _hints[_name] = _value
                    continue
            if not isinstance(_src, str):
                _register_annotation_value(_src, _obj)
        return _hints

    def _patched_th(_obj, _globalns=None, _localns=None, **_kw):
        _hints = _eval_type_hints(_obj, _globalns, _localns)
        return _restore_aliases(_hints, _obj)

    if _hints_mod is not None:
        # ``_resolve.hints`` imports ``type_hints`` by name, so patch both the
        # definition and that module-level binding.
        _hints_mod.type_hints = _patched_th
    if _eval_type_hints is not None:
        import sphinx_autodoc_typehints._resolve.evaluate as _eval_mod

        _eval_mod.type_hints = _patched_th

    app.connect(
        "autodoc-process-docstring",
        _drop_inherited_instance_docstring,
        priority=0,
    )
    app.connect("autodoc-skip-member", _skip_internal_autodoc_member)
