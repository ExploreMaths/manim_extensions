# SPDX-FileCopyrightText: 2022 bmmtstb, 99Vicky
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


"""
A place for all decorators.
"""

import warnings
from typing import Any, Callable, ParamSpec, TypeVar, cast

P = ParamSpec("P")
R = TypeVar("R")


def dangling_vert_decorator() -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator for mesh operations to check for dangling vertices.

    Warns if any vertices are not part of a face after the decorated function runs.

    Returns
    -------
    callable
        The decorator that wraps a mesh operation function.
    """

    def decorator_func(func: Callable[P, R]) -> Callable[P, R]:
        """Wrap a mesh operation with a dangling-vertex check.

        Parameters
        ----------
        func : callable
            The mesh operation to wrap.

        Returns
        -------
        callable
            The wrapped function.
        """

        def wrapper_func(*args: P.args, **kwargs: P.kwargs) -> R:
            """Execute the function and warn about dangling vertices.

            Parameters
            ----------
            *args
                Positional arguments forwarded to the wrapped function.
            **kwargs
                Keyword arguments forwarded to the wrapped function.
            """
            mesh = cast(Any, args[0])
            return_value = func(*args, **kwargs)
            if mesh.test_for_dangling and mesh.dangling_vert_check():
                warnings.warn(f"Dangling vertices in {func.__name__}")
            return return_value

        return wrapper_func

    return decorator_func


def dangling_face_decorator() -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator for mesh operations to check for dangling faces.

    Warns if any faces are not part of a part after the decorated function runs.

    Returns
    -------
    callable
        The decorator that wraps a mesh operation function.
    """

    def decorator_func(func: Callable[P, R]) -> Callable[P, R]:
        """Wrap a mesh operation with a dangling-face check.

        Parameters
        ----------
        func : callable
            The mesh operation to wrap.

        Returns
        -------
        callable
            The wrapped function.
        """

        def wrapper_func(*args: P.args, **kwargs: P.kwargs) -> R:
            """Execute the function and warn about dangling faces.

            Parameters
            ----------
            *args
                Positional arguments forwarded to the wrapped function.
            **kwargs
                Keyword arguments forwarded to the wrapped function.
            """
            mesh = cast(Any, args[0])
            return_value = func(*args, **kwargs)
            if mesh.test_for_dangling and mesh.dangling_face_check():
                warnings.warn(f"Dangling faces in {func.__name__}")
            return return_value

        return wrapper_func

    return decorator_func
