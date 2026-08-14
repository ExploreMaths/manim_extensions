from manim import Paragraph, VGroup, Integer, Dot, DOWN, Code

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
        Additional keyword arguments forwarded to :class:`Integer`.

    Returns
    -------
    VGroup
        A group of :class:`Integer` labels, one per paragraph line.
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

def index_code_labels(
    code: Code,
    label_height: float = 0.1,
    **kwargs,
) -> VGroup:
    """Add integer index labels below each code line.

    Parameters
    ----------
    code : Code
        The code block whose lines will be labelled.
    label_height : float
        Height of each label mobject.
    **kwargs
        Additional keyword arguments forwarded to :class:`Integer`.

    Returns
    -------
    VGroup
        A group of :class:`Integer` labels, one per code line.
    """
    ret = VGroup()
    code_paragraph = (
        getattr(code, "code", None)
        or getattr(code, "code_lines", None)
    )
    if code_paragraph is None:
        return ret
    for row in code_paragraph:
        ret.add(index_paragraph_labels(row, label_height, **kwargs))
    return ret