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

from manim_extensions.qr_codes import QRCode


@pytest.mark.skipif(not _HAS_SEGNO, reason="segno not installed")
class TestQRCode:
    def test_basic_construction(self):
        """QRCode should return a VGroup for a simple payload."""
        result = QRCode("https://example.com")
        assert isinstance(result, VGroup)
        # The group should contain corner group and data group
        assert len(result.submobjects) >= 2

    def test_circles_data_shape(self):
        """QRCode should work with data_shape='circles'."""
        result = QRCode("hello", data_shape="circles")
        assert isinstance(result, VGroup)
        assert len(result.submobjects) >= 2

    def test_invalid_data_shape_raises(self):
        """QRCode should raise ValueError for invalid data_shape."""
        with pytest.raises(ValueError, match="Invalid data_shape"):
            QRCode("test", data_shape="triangles")

    def test_with_corner_color(self):
        """QRCode should accept custom corner_color."""
        result = QRCode("test", corner_color="#FF0000")
        assert isinstance(result, VGroup)

    def test_empty_payload(self):
        """QRCode should handle an empty string payload."""
        result = QRCode("")
        assert isinstance(result, VGroup)
