# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the visual queue data structure."""

import pytest
from manim import RIGHT

from manim_extensions.algorithm.node import Node
from manim_extensions.algorithm.queue import Queue


@pytest.fixture()
def queue():
    return Queue(capacity=5, init_data=[1, 2, 3], total_width=8)


def test_queue_is_built_with_initial_data(queue):
    assert len(queue.data) == 3
    assert queue.capacity == 5
    assert queue.item_width == 8 / 5


def test_enqueue_animation(queue):
    animation = Queue.Enqueue(queue, Node("4").next_to(queue, RIGHT, buff=1.5))

    assert animation is not None


def test_dequeue_animation(queue):
    animation = Queue.Dequeue(queue)

    assert animation is not None
