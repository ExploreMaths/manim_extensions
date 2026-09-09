# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Import-resolution regression tests.

These guard against namespace-shadowing bugs of the kind fixed in
``1afb187`` (``from manim import *`` leaking manim's own ``utils`` module
into subpackages and shadowing the real submodules) and against broken
chain imports anywhere in the public package tree.
"""

import importlib
import pkgutil

import manim_extensions


def _walk_modules(module):
    yield module.__name__
    if hasattr(module, "__path__"):
        prefix = module.__name__ + "."
        for info in pkgutil.iter_modules(module.__path__, prefix):
            yield from _walk_modules(importlib.import_module(info.name))


def test_all_submodules_importable():
    """Every module in the package tree must import cleanly."""
    modules = list(_walk_modules(manim_extensions))
    assert len(modules) > 50
    for name in modules:
        assert name in importlib.sys.modules or importlib.import_module(name)


def test_utils_attribute_not_shadowed_by_manim():
    """``from manim import *`` must not leak manim's ``utils`` into our packages."""
    import manim.utils as manim_utils

    for pkg_name in ("manim_extensions.algorithm", "manim_extensions.circuit"):
        pkg = importlib.import_module(pkg_name)
        assert pkg.utils is not manim_utils, (
            f"{pkg_name}.utils is shadowed by manim.utils"
        )
        assert pkg.utils.__name__.startswith("manim_extensions."), (
            f"{pkg_name}.utils resolves to {pkg.utils.__name__}"
        )


def test_dotted_utils_imports_resolve_inside_package():
    """Dotted import resolution must see the real submodules, not manim's."""
    from manim_extensions.algorithm.utils.numpy_helper import NumpyHelper
    from manim_extensions.circuit.utils import Circuit

    assert NumpyHelper.__module__.startswith("manim_extensions.")
    assert Circuit.__module__.startswith("manim_extensions.")


def test_submodule_attributes_match_dotted_imports():
    """``pkg.sub`` attribute access must agree with ``import pkg.sub``."""
    import manim.utils as manim_utils

    candidates = [
        "manim_extensions.algorithm.utils",
        "manim_extensions.circuit.utils",
        "manim_extensions.machine_learning.utils",
        "manim_extensions.automata.mobjects.automata_dependencies",
    ]
    for dotted in candidates:
        pkg_name, _, attr = dotted.rpartition(".")
        pkg = importlib.import_module(pkg_name)
        submodule = importlib.import_module(dotted)
        assert getattr(pkg, attr) is submodule, (
            f"{pkg_name}.{attr} does not resolve to the real submodule"
        )
        assert submodule is not manim_utils


def test_chain_imports_of_public_names():
    """Every name advertised in a package ``__all__`` must be importable."""
    failures = []
    for info in pkgutil.iter_modules(manim_extensions.__path__, "manim_extensions."):
        try:
            module = importlib.import_module(info.name)
        except Exception:
            continue
        all_names = getattr(module, "__all__", None)
        if not all_names:
            continue
        for name in all_names:
            try:
                getattr(module, name)
            except AttributeError:
                failures.append(f"{info.name}: missing __all__ entry {name}")
    assert failures == []
