# SPDX-FileCopyrightText: 2022 Hammad Nasir
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Contains enums used throughout the package."""

from enum import Enum


class MArrayElementComp(Enum):
    r"""Refers to individual component :class:`~manim.mobject.mobject.Mobject`\ s of :class:`~manim_extensions.data_structures.m_array.MArrayElement`.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.data_structures.m_enum import MArrayElementComp

        component = MArrayElementComp.BODY
    """

    BODY = 0
    """:class:`~manim.mobject.geometry.polygram.Square` that represents the body."""

    VALUE = 1
    """:class:`~manim.mobject.text.text_mobject.Text` that represents the value."""

    INDEX = 2
    """:class:`~manim.mobject.text.text_mobject.Text` that represents the index."""

    LABEL = 3
    """:class:`~manim.mobject.text.text_mobject.Text` that represents the label."""


class MArrayDirection(Enum):
    """Serves as the direction for :class:`~manim_extensions.data_structures.m_array.MArray`.

    Examples
    --------
    .. code-block:: python

        from manim_extensions.data_structures.m_enum import MArrayDirection

        direction = MArrayDirection.RIGHT
    """

    UP = 0
    """Upward direction."""

    DOWN = 1
    """Downward direction."""

    RIGHT = 2
    """Rightward direction."""

    LEFT = 3
    """Leftward direction."""
