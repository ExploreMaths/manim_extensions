# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT


from manim import *
import shutil
import subprocess
import platform

import numpy as np
import pytest
from PIL import Image

from manim_extensions.mobjects import (
    ChineseMathTex,
    LabelDot,
    MathTexLine,
    MathTexBrace,
    MathTexDoublearrow,
    ExtendedLine,
    PerpendicularLine,
    PerpendicularSign,
    FileTree,
    CropImageMobject,
    VideoMobject,
)

_HAS_XELATEX = shutil.which("xelatex") is not None

_CJK_FONT = "SimSun" if platform.system() == "Windows" else "Noto Serif CJK SC"

try:
    import cv2
except ImportError:
    cv2 = None


@pytest.mark.skipif(not _HAS_XELATEX, reason="xelatex not installed")
class TestChineseMathTex:
    def test_is_math_tex_subclass(self):
        tex = ChineseMathTex("x + y = 1")
        assert isinstance(tex, MathTex)

    def test_font_parameter(self):
        tex = ChineseMathTex("x = 1", font=_CJK_FONT)
        assert isinstance(tex, MathTex)


class TestLabelDot:
    def test_creation(self):
        dot = LabelDot("A", [1, 2, 0])
        assert isinstance(dot, VGroup)
        assert len(dot.submobjects) == 2

    def test_direction_and_buff(self):
        dot = LabelDot("B", [0, 0, 0], label_pos=UP, buff=0.2)
        assert isinstance(dot, VGroup)


class TestMathTexLine:
    def test_creation(self):
        formula = MathTex("y = x")
        obj = MathTexLine(formula, direction=UP, buff=0.5)
        assert isinstance(obj, VGroup)
        assert len(obj.submobjects) == 2


class TestMathTexBrace:
    def test_creation(self):
        formula = MathTex(r"\Delta x")
        target = Line(LEFT, RIGHT)
        obj = MathTexBrace(target, formula, direction=UP, buff=0.3)
        assert isinstance(obj, VGroup)
        assert len(obj.submobjects) == 2


class TestMathTexDoublearrow:
    def test_creation(self):
        formula = MathTex(r"\Leftrightarrow")
        obj = MathTexDoublearrow(formula, direction=DOWN, buff=0.4)
        assert isinstance(obj, VGroup)
        assert len(obj.submobjects) == 2


class TestExtendedLine:
    def test_extend(self):
        original = Line(LEFT, RIGHT)
        extended = ExtendedLine(original, extend_distance=1.0)
        assert isinstance(extended, Line)
        # Original line has length 2 (from -1 to 1 on x-axis)
        # Extended by 1.0 on each end should give length 4
        start = extended.get_start()
        end = extended.get_end()
        assert abs(start[0] - (-2.0)) < 1e-6
        assert abs(end[0] - 2.0) < 1e-6

    def test_degenerate_line(self):
        original = Line(ORIGIN, ORIGIN)
        extended = ExtendedLine(original, extend_distance=1.0)
        assert isinstance(extended, Line)


class TestPerpendicularLine:
    def test_basic_perpendicular(self):
        line = Line(LEFT, RIGHT)
        perp = PerpendicularLine(UP, line)
        assert isinstance(perp, Line)
        start, end = perp.get_start(), perp.get_end()
        assert np.allclose(start, UP) or np.allclose(end, UP)
        foot = perp.foot
        assert np.allclose(foot, ORIGIN)

    def test_with_mobject_point(self):
        line = Line(LEFT, RIGHT)
        dot = LabelDot("P", UP * 2)
        perp = PerpendicularLine(dot, line)
        assert isinstance(perp, Line)
        assert np.allclose(perp.foot, ORIGIN)

    def test_degenerate_line(self):
        line = Line(ORIGIN, ORIGIN)
        perp = PerpendicularLine(UP, line)
        assert isinstance(perp, Line)
        # Falls back to the degenerate point
        assert np.allclose(perp.foot, ORIGIN)


class TestFileTree:
    def test_is_code_subclass(self):
        tree = FileTree({"src": {"main.py": None}})
        assert isinstance(tree, Code)

    def test_creation(self):
        tree = FileTree(
            {
                "src": {
                    "main.py": None,
                    "utils": {
                        "helpers.py": None,
                    },
                },
                "README.md": None,
            }
        )
        assert isinstance(tree, Code)
        # The first submobject (the line numbers) is removed
        assert len(tree.submobjects) == 1

    def test_invalid_tree_dict(self):
        with pytest.raises(TypeError):
            FileTree("not a dict")

    def test_build_tree(self):
        lines = FileTree._build_tree(
            {
                "src": {
                    "main.py": None,
                    "utils": {
                        "helpers.py": None,
                    },
                },
                "README.md": None,
            }
        )
        assert lines[0] == "src/"
        assert "├── main.py" in lines
        assert "└── utils/" in lines
        assert "    └── helpers.py" in lines
        assert "README.md" in lines

    def test_highlight(self):
        tree = FileTree(
            {
                "src": {
                    "main.py": None,
                },
                "README.md": None,
            }
        )
        anim = tree.highlight(1, color=RED)
        assert anim is not None

    def test_highlight_out_of_range(self):
        tree = FileTree({"src": {"main.py": None}})
        with pytest.raises(ValueError):
            tree.highlight(10)


class TestCropImageMobject:
    def test_is_image_mobject_subclass(self):
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        mob = CropImageMobject(arr)
        assert isinstance(mob, ImageMobject)

    def test_from_numpy_array(self):
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        arr[:] = (255, 0, 0)
        mob = CropImageMobject(arr)
        # RGBA conversion adds an alpha channel
        assert mob.pixel_array.shape[2] == 4

    def test_from_pil_image(self):
        img = Image.new("RGB", (64, 64), (0, 255, 0))
        mob = CropImageMobject(img)
        assert isinstance(mob, ImageMobject)
        assert mob.pixel_array.shape[2] == 4

    def test_corner_radius_pixel_value(self):
        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        mob = CropImageMobject(arr, corner_radius=20)
        assert isinstance(mob, ImageMobject)


@pytest.mark.skipif(cv2 is None, reason="opencv-python not installed")
class TestVideoMobject:
    @staticmethod
    def _make_video(path) -> None:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(str(path), fourcc, 30.0, (64, 64))
        for _ in range(30):
            out.write(np.zeros((64, 64, 3), dtype=np.uint8))
        out.release()

    def test_is_image_mobject_subclass(self, tmp_path):
        video_path = tmp_path / "video.mp4"
        self._make_video(video_path)
        mob = VideoMobject(str(video_path))
        assert isinstance(mob, ImageMobject)

    def test_duration(self, tmp_path):
        video_path = tmp_path / "video.mp4"
        self._make_video(video_path)
        mob = VideoMobject(str(video_path), rate=2.0)
        assert mob.duration == mob._duration / 2.0

    def test_invalid_file_raises(self):
        with pytest.raises(ValueError):
            VideoMobject("does_not_exist.mp4")

    def test_play_and_stop(self, tmp_path):
        video_path = tmp_path / "video.mp4"
        self._make_video(video_path)
        mob = VideoMobject(str(video_path))
        mob.play()
        assert mob._playing
        mob.stop()
        assert not mob._playing
        assert mob._updater_ref not in mob.updaters

    def test_reset(self, tmp_path):
        video_path = tmp_path / "video.mp4"
        self._make_video(video_path)
        mob = VideoMobject(str(video_path))
        mob._frame_idx = 10
        mob._elapsed = 0.5
        mob._finished = True
        mob.reset()
        assert mob._frame_idx == 0
        assert mob._elapsed == 0.0
        assert not mob._finished

    def test_seek(self, tmp_path):
        video_path = tmp_path / "video.mp4"
        self._make_video(video_path)
        mob = VideoMobject(str(video_path))
        mob.seek(0.2)
        assert mob._frame_idx >= 0


class TestPerpendicularSign:
    def test_creation(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        sign = PerpendicularSign(line1, line2, length=0.2)
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2

    def test_intersection_at_origin(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        sign = PerpendicularSign(line1, line2, length=0.2)
        # The sign should be created and its intersection should be near origin
        assert np.allclose(sign.intersection, ORIGIN, atol=1e-6)

    def test_parallel_lines(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(UP, UP + RIGHT)
        sign = PerpendicularSign(line1, line2, length=0.2)
        # Parallel lines have no intersection, so sign should be empty
        assert len(sign.submobjects) == 0

    def test_different_lengths(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        sign = PerpendicularSign(line1, line2, length=0.5)
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2

    def test_corner_direction_ur(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        # 指定折角画在右上（第一象限）
        sign = PerpendicularSign(line1, line2, length=0.2, corner_direction=[1, 1, 0])
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2
        # 内角顶点应该在第一象限
        inner = sign.submobjects[0].get_end()
        assert inner[0] > 0
        assert inner[1] > 0

    def test_corner_direction_dl(self):
        line1 = Line(LEFT, RIGHT)
        line2 = Line(DOWN, UP)
        # 指定折角画在左下（第三象限）
        sign = PerpendicularSign(line1, line2, length=0.2, corner_direction=[-1, -1, 0])
        assert isinstance(sign, VGroup)
        assert len(sign.submobjects) == 2
        # 内角顶点应该在第三象限
        inner = sign.submobjects[0].get_end()
        assert inner[0] < 0
        assert inner[1] < 0


# --- Ported from manim-kindergarten/manim_sandbox -------------------

from manim_extensions.mobjects import (
    ColorText,
    Trail,
    ShadowAround,
    ObjectBorder,
    ThreeDVector,
    TreeDiagram,
)


class TestColorText:
    def test_is_text_subclass(self):
        ct = ColorText([150, 60, 200])
        assert isinstance(ct, Text)

    def test_normalized_values(self):
        ct = ColorText([0.5, 0.2, 0.8])
        assert isinstance(ct, Text)

    def test_named_text(self):
        ct = ColorText("blue", name="colour")
        assert isinstance(ct, Text)


class TestTrail:
    def test_creation(self):
        trail = Trail(Dot())
        assert isinstance(trail, VGroup)

    def test_start_stop_trace(self):
        trail = Trail(Dot())
        trail.start_trace()
        assert trail.trail.updaters
        trail.stop_trace()
        assert not trail.trail.updaters


class TestShadowAround:
    def test_with_circle(self):
        shadow = ShadowAround(Circle(radius=1))
        assert isinstance(shadow, VGroup)
        assert len(shadow.blur_outline.submobjects) > 0

    def test_with_points(self):
        shadow = ShadowAround([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
        assert isinstance(shadow, VGroup)


class TestObjectBorder:
    def test_creation(self):
        border = ObjectBorder(Text("Hi"))
        assert isinstance(border, VGroup)

    def test_no_track(self):
        border = ObjectBorder(Text("Hi"), track=False)
        assert not border.updaters


class TestThreeDVector:
    def test_creation(self):
        vec = ThreeDVector([2, 1, 1.5])
        assert isinstance(vec, VGroup)

    def test_zero_vector_empty(self):
        vec = ThreeDVector([0, 0, 0])
        assert isinstance(vec, VGroup)


class TestTreeDiagram:
    def test_creation(self):
        tree = {"A": {"B": {"D", "E"}, "C": {"F", "G"}}}
        diagram = TreeDiagram(tree)
        assert isinstance(diagram, VGroup)

    def test_simple_tree(self):
        diagram = TreeDiagram({"root": {"a", "b"}})
        assert isinstance(diagram, VGroup)