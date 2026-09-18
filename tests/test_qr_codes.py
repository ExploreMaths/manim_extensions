# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the qr_codes module."""

import pytest
from manim import VGroup

try:
    import segno
    _HAS_SEGNO = True
except ImportError:
    _HAS_SEGNO = False

from manim_extensions.qr_codes import qr_code


@pytest.mark.skipif(not _HAS_SEGNO, reason="segno not installed")
class TestQRCode:
    def test_basic_construction(self):
        """qr_code should return a VGroup for a simple payload."""
        result = qr_code("https://example.com")
        assert isinstance(result, VGroup)
        # The group should contain corner group and data group
        assert len(result.submobjects) >= 2

    def test_circles_data_shape(self):
        """qr_code should work with data_shape='circles'."""
        result = qr_code("hello", data_shape="circles")
        assert isinstance(result, VGroup)
        assert len(result.submobjects) >= 2

    def test_invalid_data_shape_raises(self):
        """qr_code should raise ValueError for invalid data_shape."""
        with pytest.raises(ValueError, match="Invalid data_shape"):
            qr_code("test", data_shape="triangles")

    def test_with_corner_color(self):
        """qr_code should accept custom corner_color."""
        result = qr_code("test", corner_color="#FF0000")
        assert isinstance(result, VGroup)

    def test_empty_payload(self):
        """qr_code should handle an empty string payload."""
        result = qr_code("")
        assert isinstance(result, VGroup)
