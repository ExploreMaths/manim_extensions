from manim import *
import numpy as np


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
