# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Debug utilities for algorithm visualization."""

from typing import Any

from manim import DOWN, Dot, Integer, Paragraph, VGroup


class ParagraphLineIndices(VGroup):
    """Integer labels placed below each paragraph line.

    One label is created for every entry that is not a ``Dot``.

    Parameters
    ----------
    paragraph
        The paragraph whose lines will be labelled.
    label_height
        Height of each label mobject.
    **kwargs
        Additional keyword arguments forwarded to
        :class:`~manim.mobject.text.numbers.Integer`.

    Examples
    --------
    .. manim:: ParagraphLineLabels
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.utils import ParagraphLineIndices

       class ParagraphLineLabels(Scene):
           def construct(self):
               paragraph = Paragraph("alpha", "beta", "gamma", line_spacing=1)
               labels = ParagraphLineIndices(paragraph, label_height=0.25)
               self.add(paragraph, labels)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        paragraph: Paragraph,
        label_height: float = 0.1,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        super().__init__()
        for i in range(len(paragraph)):
            if not isinstance(paragraph[i], Dot):
                label = Integer(i, **kwargs)
                label.height = label_height
                label.next_to(paragraph[i], DOWN, buff=0)
                self.add(label)
