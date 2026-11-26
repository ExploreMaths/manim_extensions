# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Tests for the final-hold rule in ``validate_manim_directives``."""

import sys
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / "workflow"
sys.path.insert(0, str(WORKFLOW))

import validate_manim_directives as checker  # noqa: E402


def block(code: str, *, gif: bool = False) -> dict:
    """Build the subset of a directive block the final-hold check reads."""
    return {
        "class_name": "Demo",
        "has_save_last_frame": False,
        "has_save_as_gif": gif,
        "code": code,
        "start_line": 1,
        "code_start_line": 1,
    }


def scene(body: str) -> str:
    """Wrap *body* in a minimal Manim scene."""
    return (
        "from manim import *\n\n"
        "class Demo(Scene):\n"
        "    def construct(self):\n"
        f"{body}"
    )


def test_final_wait_accepts_default_one_second() -> None:
    """``self.wait()`` is one second, so it satisfies the rule."""
    assert checker.check_final_wait(block(scene("        self.wait()\n"))) == []


def test_final_wait_accepts_long_wait() -> None:
    """A wait longer than one second also satisfies the rule."""
    assert checker.check_final_wait(block(scene("        self.wait(2)\n"))) == []


def test_final_wait_rejects_short_wait() -> None:
    """A hold shorter than one second fails."""
    issues = checker.check_final_wait(block(scene("        self.wait(0.5)\n")))
    assert [issue["type"] for issue in issues] == ["ANIMATED_SHORT_FINAL_WAIT"]


def test_final_wait_rejects_missing_wait() -> None:
    """An animation followed by no hold fails."""
    issues = checker.check_final_wait(
        block(scene("        self.play(Create(Dot()))\n"))
    )
    assert [issue["type"] for issue in issues] == ["ANIMATED_MISSING_FINAL_WAIT"]


def test_final_wait_accepts_loop_marker() -> None:
    """An explicit seamless-loop marker exempts the example."""
    code = scene("        self.play(Create(Dot()))\n        # loops seamlessly\n")
    assert checker.check_final_wait(block(code)) == []


def test_final_wait_accepts_gif() -> None:
    """GIF examples loop and do not need a final hold."""
    assert (
        checker.check_final_wait(
            block(scene("        self.play(Create(Dot()))\n"), gif=True)
        )
        == []
    )


def test_final_wait_accepts_delegated_construct() -> None:
    """A scene that delegates to its parent is checked at the parent."""
    code = (
        "from manim import *\n\n"
        "class Demo(Parent):\n"
        "    def construct(self):\n"
        "        super().construct()\n"
    )
    assert checker.check_final_wait(block(code)) == []
