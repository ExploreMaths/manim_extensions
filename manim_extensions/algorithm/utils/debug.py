# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Debug utilities for algorithm visualization."""

from typing import Any

from manim import DOWN, Dot, Integer, Paragraph, VGroup


def index_paragraph_labels(
    paragraph: Paragraph,
    label_height: float = 0.1,
    **kwargs: Any,
) -> VGroup:
    """Add integer index labels below each paragraph line.

    Parameters
    ----------
    paragraph
        The paragraph whose lines will be labelled.
    label_height
        Height of each label mobject.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.text.numbers.Integer`.

    Returns
    -------
        A group of :class:`~manim.mobject.text.numbers.Integer` labels, one per paragraph line.

    Examples
    --------
    .. manim:: IndexParagraphLabelsExample
       :save_last_frame:

       from manim import *
       from manim_extensions.algorithm.utils.debug import index_paragraph_labels

       class IndexParagraphLabelsExample(Scene):
           def construct(self):
               paragraph = Paragraph("alpha", "beta", "gamma", line_spacing=1)
               labels = index_paragraph_labels(paragraph, label_height=0.25)
               self.add(paragraph, labels)
    """
    labels = VGroup()
    idx = 0
    for i in range(len(paragraph)):
        if not isinstance(paragraph[i], Dot):
            label = Integer(i, **kwargs)
            idx += 1
            label.height = label_height
            label.next_to(paragraph[i], DOWN, buff=0)
            labels.add(label)
    return labels
