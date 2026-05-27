from manim import *
from manim.typing import Point3D, Vector3DLike
import numpy as np
from typing import Any, Union


class ChineseMathTex(MathTex):
    """支持中文显示的 MathTex 类。

    自动将输入文本中的中文字符用 ``\\text{}`` 包裹，
    并配置 ``xelatex`` 与 ``xeCJK`` 宏包以支持中文字体渲染。

    Args:
        *texts: 要渲染的 LaTeX 文本字符串。
        font: 中文字体名称。默认为 ``"SimSun"``。
        tex_to_color_map: 文本到颜色的映射字典。默认为 ``{}``。
        **kwargs: 传递给 ``MathTex`` 的其他关键字参数。
    """

    def __init__(
        self,
        *texts: str,
        font: str = "SimSun",
        tex_to_color_map: dict = {},
        **kwargs,
    ) -> None:
        tex_template = TexTemplate(tex_compiler="xelatex", output_format=".xdv")
        tex_template.add_to_preamble(r"\usepackage{amsmath}")
        tex_template.add_to_preamble(r"\usepackage{xeCJK}")
        tex_template.add_to_preamble(rf"\setCJKmainfont{{{font}}}")

        combined_chinesetext = []
        for text in texts:
            chinesetext = ""
            for i in range(len(text)):
                if (
                    ("\u4e00" <= text[i] <= "\u9fff")
                    or ("\u3000" <= text[i] <= "\u303f")
                    or ("\uff00" <= text[i] <= "\uffef")
                ):
                    chinesetext += rf"\text{{{text[i]}}}"
                else:
                    chinesetext += text[i]
            combined_chinesetext.append(chinesetext)

        new_dict = {}
        for key in tex_to_color_map.keys():
            new_key = ""
            for char in key:
                if (
                    ("\u4e00" <= char <= "\u9fff")
                    or ("\u3000" <= char <= "\u303f")
                    or ("\uff00" <= char <= "\uffef")
                ):
                    new_key += rf"\text{{{char}}}"
                else:
                    new_key += char
            new_dict[new_key] = tex_to_color_map[key]

        super().__init__(
            *combined_chinesetext,
            tex_template=tex_template,
            tex_to_color_map=new_dict,
            **kwargs,
        )


class LabelDot(VGroup):
    """带标签的圆点。

    在指定位置创建一个圆点，并在其旁边添加 MathTex 标签。

    Args:
        dot_label: 标签文本内容。
        dot_pos: 圆点的位置坐标。
        label_pos: 标签相对圆点的方向。默认为 ``DOWN``。
        buff: 标签与圆点之间的间距。默认为 0.1。
        **kwargs: 传递给 ``VGroup`` 的其他关键字参数。
    """

    def __init__(
        self,
        dot_label: str,
        dot_pos: np.ndarray,
        label_pos: np.ndarray = DOWN,
        buff: float = 0.1,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        dot = Dot().move_to(dot_pos)
        label = MathTex(dot_label).next_to(dot, label_pos, buff=buff)
        self.add(dot, label)
        self.dot = dot
        self.dot_pos = dot_pos

    def get_center(self) -> Point3D:
        return self.dot.get_center()

    def get_boundary_point(self, direction: Vector3DLike) -> Point3D:
        return self.dot.get_center()


class MathTexLine(VGroup):
    """带 MathTex 公式的线段。

    创建一条线段，并在其指定方向旁放置一个 MathTex 公式。

    Args:
        formula: 要放置的 MathTex 公式对象。
        direction: 公式相对线段的方向。默认为 ``UP``。
        buff: 公式与线段之间的间距。默认为 0.5。
        **kwargs: 传递给 ``Line`` 的其他关键字参数。
    """

    def __init__(
        self,
        formula: MathTex,
        direction: np.ndarray = UP,
        buff: float = 0.5,
        **kwargs,
    ) -> None:
        super().__init__()
        line = Line(**kwargs)
        tex = formula.next_to(line, direction, buff=buff)
        self.add(line, tex)


class MathTexBrace(VGroup):
    """带 MathTex 公式的花括号。

    为指定对象创建一个花括号，并在其旁边放置一个 MathTex 公式。

    Args:
        target: 要被花括号标注的目标对象（如线段、矩形等）。
        formula: 要放置的 MathTex 公式对象。
        direction: 公式与花括号相对目标的方向。默认为 ``UP``。
        buff: 公式与花括号之间的间距。默认为 0.5。
        **kwargs: 传递给 ``Brace`` 的其他关键字参数。
    """

    def __init__(
        self,
        target,
        formula: MathTex,
        direction: np.ndarray = UP,
        buff: float = 0.5,
        **kwargs,
    ) -> None:
        super().__init__()
        brace = Brace(target, direction=direction, **kwargs)
        tex = formula.next_to(brace, direction, buff=buff)
        self.add(brace, tex)


class MathTexDoublearrow(VGroup):
    """带 MathTex 公式的双向箭头。

    创建一个双向箭头，并在其指定方向旁放置一个 MathTex 公式。

    Args:
        formula: 要放置的 MathTex 公式对象。
        direction: 公式相对双向箭头的方向。默认为 ``UP``。
        buff: 公式与双向箭头之间的间距。默认为 0.5。
        **kwargs: 传递给 ``DoubleArrow`` 的其他关键字参数。
    """

    def __init__(
        self,
        formula: MathTex,
        direction: np.ndarray = UP,
        buff: float = 0.5,
        **kwargs,
    ) -> None:
        super().__init__()
        doublearrow = DoubleArrow(**kwargs)
        tex = formula.next_to(doublearrow, direction, buff=buff)
        self.add(doublearrow, tex)


class PerpendicularLine(Line):
    """过指定点作线段所在直线的垂线段。

    自动计算给定点在目标线段所在直线上的垂足，并创建从该点到垂足的线段。

    Args:
        point: 给定点坐标或 Mobject。
        line: 目标线段。
        **kwargs: 传递给 ``Line`` 的其他关键字参数。
    """

    def __init__(
        self,
        point: Union[np.ndarray, tuple, list, Mobject],
        line: Line,
        **kwargs: Any,
    ) -> None:
        if isinstance(point, Mobject):
            self.point = point.get_center()
        else:
            self.point = np.array(point)
        self.target_line = line
        self.foot = self._compute_foot()
        super().__init__(self.point, self.foot, **kwargs)

    def _compute_foot(self) -> np.ndarray:
        a = self.target_line.get_start()
        b = self.target_line.get_end()
        ab = b - a
        ap = self.point - a
        ab_dot_ab = np.dot(ab, ab)
        if ab_dot_ab < 1e-12:
            return a
        t = np.dot(ap, ab) / ab_dot_ab
        return a + t * ab


class ExtendedLine(Line):
    """可延长的线段。

    基于一条已有的 ``Line``，在其两端按原方向各延长指定距离。

    Args:
        line: 作为基准的原始线段。
        extend_distance: 两端各延长的距离。
        **kwargs: 传递给 ``Line`` 的其他关键字参数。
    """

    def __init__(self, line: Line, extend_distance: float, **kwargs) -> None:
        start_point = line.get_start()
        end_point = line.get_end()
        direction_vector = end_point - start_point
        vector_length = np.linalg.norm(direction_vector)
        if vector_length < 1e-8:
            super().__init__(start_point, end_point, **kwargs)
        else:
            unit_direction_vector = direction_vector / vector_length
            new_start_point = start_point - extend_distance * unit_direction_vector
            new_end_point = end_point + extend_distance * unit_direction_vector
            super().__init__(new_start_point, new_end_point, **kwargs)
        self.match_style(line)


class PerpendicularSign(VGroup):
    """垂直符号（直角折角）。

    在两条线的交点处绘制一个直角符号，表示两线垂直。
    符号由两条短线段组成，形成一个L形折角。

    Args:
        line1: 第一条线。
        line2: 第二条线。
        length: 折角每段的长度。默认为 0.25。
        corner_direction: 指定折角画在哪一侧的方向向量。
            折角会放置在该方向对应的象限中。若不指定，则自动选择
            指向两条线段较近端点的那一侧。
        **kwargs: 传递给 ``VGroup`` 的其他关键字参数。
    """

    def __init__(
        self,
        line1: Line,
        line2: Line,
        length: float = 0.25,
        corner_direction: Union[np.ndarray, tuple, list, None] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        # 计算两线交点
        intersection = self._compute_intersection(line1, line2)
        if intersection is None:
            return

        # 获取两线各自两侧的单位方向向量
        dirs1 = self._get_both_directions(line1, intersection)
        dirs2 = self._get_both_directions(line2, intersection)

        # 选择最佳的组合
        d1, d2 = self._select_directions(
            dirs1, dirs2, corner_direction
        )

        # 折角的三个顶点
        corner1 = intersection + length * d1
        corner2 = intersection + length * d2
        # 内角顶点：沿两个方向的和的方向移动
        inner = intersection + length * d1 + length * d2

        # 组成折角的两条线段
        leg1 = Line(corner1, inner, **kwargs)
        leg2 = Line(corner2, inner, **kwargs)

        self.add(leg1, leg2)
        self.intersection = intersection

    def _compute_intersection(
        self, line1: Line, line2: Line
    ) -> Union[np.ndarray, None]:
        a1 = line1.get_start()
        b1 = line1.get_end()
        a2 = line2.get_start()
        b2 = line2.get_end()

        d1 = b1 - a1
        d2 = b2 - a2

        # Use full 3D vectors for cross product to avoid NumPy 2.0 deprecation
        cross = np.cross(d1, d2)
        if abs(cross[2]) < 1e-12:
            return None

        t = np.cross(a2 - a1, d2)[2] / cross[2]
        return a1 + t * d1

    def _get_both_directions(
        self, line: Line, point: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """返回从交点指向线段两个端点的单位方向向量。"""
        start = line.get_start()
        end = line.get_end()
        d1 = start - point
        d2 = end - point
        d1_len = np.linalg.norm(d1)
        d2_len = np.linalg.norm(d2)

        if d1_len > 1e-12:
            d1 = d1 / d1_len
        else:
            d1 = np.array([0.0, 0.0, 0.0])

        if d2_len > 1e-12:
            d2 = d2 / d2_len
        else:
            d2 = np.array([0.0, 0.0, 0.0])

        return d1, d2

    def _select_directions(
        self,
        dirs1: tuple[np.ndarray, np.ndarray],
        dirs2: tuple[np.ndarray, np.ndarray],
        corner_direction: Union[np.ndarray, tuple, list, None],
    ) -> tuple[np.ndarray, np.ndarray]:
        """根据 corner_direction 选择最佳的两侧方向。"""
        candidates = []
        for d1 in dirs1:
            for d2 in dirs2:
                inner_dir = d1 + d2
                norm = np.linalg.norm(inner_dir)
                if norm < 1e-12:
                    continue
                candidates.append((d1, d2, inner_dir / norm))

        if not candidates:
            return dirs1[0], dirs2[0]

        if corner_direction is None:
            # 默认：选择指向较近端点的组合（即 inner_dir 模长最大的）
            best = max(candidates, key=lambda c: np.linalg.norm(c[0] + c[1]))
            return best[0], best[1]

        corner_direction = np.array(corner_direction)
        corner_direction = corner_direction / np.linalg.norm(corner_direction)

        # 选择与 corner_direction 点积最大的组合
        best = max(
            candidates,
            key=lambda c: np.dot(c[2], corner_direction),
        )
        return best[0], best[1]
