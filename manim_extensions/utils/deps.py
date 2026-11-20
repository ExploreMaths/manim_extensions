# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Lazy loaders for the optional dependencies of ``manim_extensions``.

The packages listed in ``[project.optional-dependencies]`` are not needed
to import ``manim_extensions``; each vendored module pulls in its own
extra (``physics``, ``chemistry``, ``qr``, ...).  Use
:func:`~manim_extensions.utils.deps.require` inside the function or
method that needs such a package, passing the extra that provides it, so
the ImportError names the right
``pip install manim_extensions[...]`` command.
"""

from typing import overload

import importlib
from types import ModuleType


@overload
def require(extra: str, name: str, /) -> ModuleType:
    """Import a single optional dependency, raising a helpful error naming the extra.

    Parameters
    ----------
    extra
        Name of the ``[project.optional-dependencies]`` extra.
    name
        Name of the optional package to import.

    Returns
    -------
        The imported module.
    """
    ...


@overload
def require(
    extra: str, name1: str, name2: str, /, *names: str
) -> tuple[ModuleType, ...]:
    """Import several optional dependencies, raising a helpful error naming the extra.

    Parameters
    ----------
    extra
        Name of the ``[project.optional-dependencies]`` extra.
    name1
        First optional package to import.
    name2
        Second optional package to import.
    *names
        Names of any further optional packages to import.

    Returns
    -------
        The imported modules in the order of ``names``.
    """
    ...


def require(
    extra: str, name1: str = "", name2: str = "", *names: str
) -> ModuleType | tuple[ModuleType, ...]:
    """Import optional dependencies, raising a helpful error naming the extra.

    Parameters
    ----------
    extra
        Name of the ``[project.optional-dependencies]`` extra that provides
        the packages (e.g. ``"physics"``).
    name1
        First optional package to import, when importing several at once.
    name2
        Second optional package to import, when importing several at once.
    *names
        Names of any further optional packages to import (e.g. ``"pymunk"``).

    Returns
    -------
        The imported module when a single name is given, otherwise a tuple
        with the imported modules in the order of ``names``.

    Raises
    ------
    ImportError
        If one of the packages is not installed.  The error message names
        the missing package and the ``pip install`` extra that provides it.

    Examples
    --------
    .. nbcell::

       from manim_extensions.utils.deps import require

       try:
           require("physics", "not_installed_package")
       except ImportError as error:
           print(error)
    """
    modules = []
    for name in (name1, name2, *names):
        if not name:
            continue
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
