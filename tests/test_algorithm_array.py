# SPDX-FileCopyrightText: 2024 sinianluoye
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *
import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

import sys
import os

from manim_extensions.algorithm.array import Array
from manim_extensions.algorithm.utils.numpy_helper import NumpyHelper
import shutil


class TestArray:

    TEST_MEDIA_DIR = os.path.join(os.path.dirname(__file__), "__test_media_dir__")

    def setup_method(self):
        config.media_dir = self.TEST_MEDIA_DIR
        os.makedirs(self.TEST_MEDIA_DIR, exist_ok=True)

    def teardown_method(self):
        shutil.rmtree(self.TEST_MEDIA_DIR)

    @pytest.mark.parametrize(
        "data, total_width, box_type, box_color, text_scale",
        [
            ([1, 2, 3, " ", "a"], 10, Square, RED, 1.0),
        ],
    )
    def test_array_initialization(
        self, data, total_width, box_type, box_color, text_scale
    ):
        array = Array(data, total_width, box_type, box_color, text_scale)
        assert array is not None
        assert len(array.array) == len(data)
        assert array[0].value == data[0]
        assert array[1].value == data[1]
        assert array[2].value == data[2]
        assert array[3].value == data[3]
        assert array[4].value == data[4]
        assert array.values == data


if __name__ == "__main__":
    pytest.main()