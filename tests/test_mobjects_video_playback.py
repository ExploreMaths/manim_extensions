# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for VideoMobject playback helpers."""

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from manim_extensions.mobjects import VideoMobject


@pytest.fixture()
def video_file(tmp_path):
    path = str(tmp_path / "clip.mp4")
    writer = cv2.VideoWriter(
        path, cv2.VideoWriter_fourcc(*"mp4v"), 10, (64, 64)
    )
    for i in range(20):
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        frame[:, :, i % 3] = 255
        writer.write(frame)
    writer.release()
    return path


@pytest.fixture()
def video(video_file):
    return VideoMobject(video_file)


def test_video_mobject_is_constructed(video):
    assert video is not None


def test_seek_and_play_return_self(video):
    assert video.seek(0.5) is video
    assert video.play() is video
    assert video.play(None) is video


def test_video_updater_advances_the_frame(video):
    video._video_updater(video, 0.1)

    assert video is not None
