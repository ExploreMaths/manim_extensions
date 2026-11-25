# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

import pytest
from manim import Dot, Paragraph

from manim_extensions.algorithm.utils.debug import ParagraphLineIndices


def test_ParagraphLineIndices_skips_dots():
    paragraph = Paragraph("first", "second")
    paragraph.add(Dot())
    labels = ParagraphLineIndices(paragraph)
    assert len(labels) == 2
    assert labels[0].height == pytest.approx(0.1)
