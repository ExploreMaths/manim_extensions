# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the video mobject transport controls."""

import subprocess

import pytest

pytest.importorskip("cv2")

from manim_extensions.mobjects import VideoMobject


@pytest.fixture(scope="module")
def video_file(tmp_path_factory):
    target = tmp_path_factory.mktemp("video") / "sample.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=duration=1:size=160x120:rate=10",
            str(target),
        ],
        check=True,
        capture_output=True,
    )
    return target


@pytest.fixture()
def video(video_file):
    return VideoMobject(str(video_file))


def test_duration_is_read(video):
    assert video.duration > 0


def test_transport_state_transitions(video):
    video.play()
    video.pause()
    video.resume()
    video.stop()
    video.reset()


def test_seek_clamps_inside_range(video):
    video.seek(0.5)
    video.seek(0)
    video.seek(-1)


def test_deepcopy(video):
    clone = video.__deepcopy__({})

    assert clone is not video
