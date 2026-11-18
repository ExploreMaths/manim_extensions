import pytest
from manim import Dot, Paragraph

from manim_extensions.algorithm.utils.debug import index_paragraph_labels


def test_index_paragraph_labels_skips_dots():
    paragraph = Paragraph("first", "second")
    paragraph.add(Dot())
    labels = index_paragraph_labels(paragraph)
    assert len(labels) == 2
    assert labels[0].height == pytest.approx(0.1)
