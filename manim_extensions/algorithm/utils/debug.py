# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT



from manim import *
def index_paragraph_labels(
    paragraph: Paragraph,
    label_height: float = 0.1,
    **kwargs,
):
    """Add integer index labels below each paragraph line.

    Parameters
    ----------
    paragraph : Paragraph
        The paragraph whose lines will be labelled.
    label_height : float
        Height of each label mobject.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.text.numbers.Integer`.

    Returns
    -------
    VGroup
        A group of :class:`~manim.mobject.text.numbers.Integer` labels, one per paragraph line.
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