# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Lazy loaders for the optional dependencies of ``manim_extensions``.

The packages listed in ``[project.optional-dependencies]`` are not needed
to import ``manim_extensions``; each vendored module pulls in its own
extra (``physics``, ``chemistry``, ``qr``, ...).  Use :func:`require`
inside the function or method that needs such a package, passing the
extra that provides it, so the ImportError names the right
``pip install manim_extensions[...]`` command.
"""

import importlib


def require(extra, *names):
    """Import optional dependencies, raising a helpful error naming the extra.

    Parameters
    ----------
    extra
        Name of the ``[project.optional-dependencies]`` extra that provides
        the packages (e.g. ``"physics"``).
    *names
        Names of the optional packages to import (e.g. ``"pymunk"``).

    Returns
    -------
    module or tuple of module
        The imported module when a single name is given, otherwise a tuple
        with the imported modules in the order of *names*.

    Raises
    ------
    ImportError
        If one of the packages is not installed.  The error message names
        the missing package and the ``pip install`` extra that provides it.
    """
    modules = []
    for name in names:
        try:
            modules.append(importlib.import_module(name))
        except ImportError as exc:
            raise ImportError(
                f"This feature requires '{name}'. "
                f"Install it with: pip install manim_extensions[{extra}]"
            ) from exc
    if len(modules) == 1:
        return modules[0]
    return tuple(modules)
