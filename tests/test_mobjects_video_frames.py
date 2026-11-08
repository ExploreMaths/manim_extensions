# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for frame stepping in VideoMobject playback."""

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from manim_extensions.mobjects import VideoMobject


@pytest.fixture()
def video_file(tmp_path):
    path = str(tmp_path / "clip.mp4")
    writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), 10, (64, 64))
    for i in range(20):
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        frame[:, :, i % 3] = 255
        writer.write(frame)
    writer.release()
    return path


def test_updater_reads_frames_while_playing(video_file):
    video = VideoMobject(video_file)
    video.play()

    video._video_updater(video, 0.4)

    assert video.pixel_array is not None
    assert video.pixel_array.shape[-1] == 4


def test_updater_stops_at_end_without_loop(video_file):
    video = VideoMobject(video_file, loop=False)
    video.play()

    video._video_updater(video, 10.0)

    assert video._finished is True


def test_updater_rewinds_when_looping(video_file):
    video = VideoMobject(video_file, loop=True)
    video.play()

    video._video_updater(video, 10.0)

    assert video._frame_idx < 20
