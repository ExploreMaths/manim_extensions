from manim import *
from manim.typing import Point3D, Vector3DLike
import numpy as np
from typing import Any, Union


class ChineseMathTex(MathTex):
    r"""A :class:`manim.MathTex` subclass that supports Chinese characters.

    Automatically wraps Chinese characters in ``\text{}`` and configures
    ``xelatex`` with the ``xeCJK`` package so that CJK fonts are rendered
    correctly.

    .. inheritance-diagram:: manim_extensions.mobjects.ChineseMathTex
       :parts: 1

    Parameters
    ----------
    *texts : str
        LaTeX text strings to render.
    font : str, optional
        Name of the Chinese font to use. Defaults to ``"SimSun"``.
    tex_to_color_map : dict, optional
        Mapping from text substrings to colours. Defaults to ``{}``.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.MathTex`.

    Examples
    --------

    .. manim:: ChineseMathTexDocExample
       :no_title:
       :save_last_frame:

       from manim import *
       from manim_extensions import ChineseMathTex

       class ChineseMathTexDocExample(Scene):
           def construct(self):
               formula = ChineseMathTex(
                   r"\frac{1}{2} + \text{hello} = x",
                   font="SimSun",
                   tex_to_color_map={r"\text{hello}": RED},
               )
               self.add(formula)
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
    """A dot with a :class:`manim.MathTex` label.

    Creates a :class:`manim.Dot` at the given position and places a
    :class:`manim.MathTex` label next to it.

    .. inheritance-diagram:: manim_extensions.mobjects.LabelDot
       :parts: 1

    Parameters
    ----------
    dot_label : str
        Text content of the label.
    dot_pos : numpy.ndarray
        Position of the dot.
    label_pos : numpy.ndarray, optional
        Direction of the label relative to the dot. Defaults to ``DOWN``.
    buff : float, optional
        Buffer between the label and the dot. Defaults to ``0.1``.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.VGroup`.

    Attributes
    ----------
    dot : :class:`manim.Dot`
        The underlying dot mobject.
    dot_pos : numpy.ndarray
        The position of the dot.

    Examples
    --------

    .. manim:: LabelDotDocExample
       :no_title:
       :save_last_frame:

       from manim_extensions import LabelDot

       class LabelDotDocExample(Scene):
           def construct(self):
               dot = LabelDot("A", [0, 0, 0], label_pos=UP, buff=0.2)
               self.add(dot)
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
    """A line segment paired with a :class:`manim.MathTex` formula.

    Creates a :class:`manim.Line` and places a :class:`manim.MathTex`
    formula next to it in the specified direction.

    .. inheritance-diagram:: manim_extensions.mobjects.MathTexLine
       :parts: 1

    Parameters
    ----------
    formula : :class:`manim.MathTex`
        The formula to place beside the line.
    direction : numpy.ndarray, optional
        Direction of the formula relative to the line. Defaults to ``UP``.
    buff : float, optional
        Buffer between the formula and the line. Defaults to ``0.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.Line`.

    Examples
    --------

    .. manim:: MathTexLineDocExample
       :no_title:
       :save_last_frame:

       from manim_extensions import MathTexLine

       class MathTexLineDocExample(Scene):
           def construct(self):
               line = MathTexLine(MathTex("y = x"), direction=UP, color=BLUE)
               self.add(line)
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
    r"""A brace with a :class:`manim.MathTex` formula.

    Creates a :class:`manim.Brace` around a target mobject and places a
    :class:`manim.MathTex` formula next to the brace.

    .. inheritance-diagram:: manim_extensions.mobjects.MathTexBrace
       :parts: 1

    Parameters
    ----------
    target : :class:`manim.mobject.mobject.Mobject`
        The mobject to be braced (e.g. a line, rectangle, etc.).
    formula : :class:`manim.MathTex`
        The formula to place beside the brace.
    direction : numpy.ndarray, optional
        Direction of the brace and formula relative to the target.
        Defaults to ``UP``.
    buff : float, optional
        Buffer between the formula and the brace. Defaults to ``0.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.Brace`.

    Examples
    --------

    .. manim:: MathTexBraceDocExample
       :no_title:
       :save_last_frame:

       from manim_extensions import MathTexBrace

       class MathTexBraceDocExample(Scene):
           def construct(self):
               line = Line(LEFT * 2, RIGHT * 2)
               brace = MathTexBrace(line, MathTex(r"\Delta x"), direction=UP)
               self.add(line, brace)
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
    r"""A double arrow with a :class:`manim.MathTex` formula.

    Creates a :class:`manim.DoubleArrow` and places a :class:`manim.MathTex`
    formula next to it in the specified direction.

    .. inheritance-diagram:: manim_extensions.mobjects.MathTexDoublearrow
       :parts: 1

    Parameters
    ----------
    formula : :class:`manim.MathTex`
        The formula to place beside the double arrow.
    direction : numpy.ndarray, optional
        Direction of the formula relative to the double arrow.
        Defaults to ``UP``.
    buff : float, optional
        Buffer between the formula and the double arrow. Defaults to ``0.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.DoubleArrow`.

    Examples
    --------

    .. manim:: MathTexDoublearrowDocExample
       :no_title:
       :save_last_frame:

       from manim_extensions import MathTexDoublearrow

       class MathTexDoublearrowDocExample(Scene):
           def construct(self):
               arrow = MathTexDoublearrow(MathTex(r"\Leftrightarrow"), direction=UP)
               self.add(arrow)
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
    """A perpendicular line segment from a point to a given line.

    Computes the foot of the perpendicular from *point* onto *line* and
    creates a :class:`manim.Line` from *point* to that foot.

    .. inheritance-diagram:: manim_extensions.mobjects.PerpendicularLine
       :parts: 1

    Parameters
    ----------
    point : Union[numpy.ndarray, tuple, list, :class:`manim.mobject.mobject.Mobject`]
        The point from which the perpendicular is dropped.  If an
        :class:`manim.Mobject` is given, its centre is used.
    line : :class:`manim.Line`
        The target line.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.Line`.

    Attributes
    ----------
    point : numpy.ndarray
        The 3‑D point from which the perpendicular is drawn.
    target_line : :class:`manim.Line`
        The line onto which the perpendicular is dropped.
    foot : numpy.ndarray
        The foot of the perpendicular on *target_line*.

    Examples
    --------

    .. manim:: PerpendicularLineDocExample
       :no_title:
       :save_last_frame:

       from manim_extensions import PerpendicularLine

       class PerpendicularLineDocExample(Scene):
           def construct(self):
               base = Line(LEFT * 3, RIGHT * 3)
               perp = PerpendicularLine(UP * 1.5, base, color=YELLOW)
               self.add(base, perp)
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
    """A line segment extended at both ends.

    Takes an existing :class:`manim.Line` and extends it by
    *extend_distance* along its original direction on both sides.
    The style of the original line is preserved.

    .. inheritance-diagram:: manim_extensions.mobjects.ExtendedLine
       :parts: 1

    Parameters
    ----------
    line : :class:`manim.Line`
        The original line segment to extend.
    extend_distance : float
        Distance to extend at each end.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.Line`.

    Examples
    --------

    .. manim:: ExtendedLineDocExample
       :no_title:
       :save_last_frame:

       from manim_extensions import ExtendedLine

       class ExtendedLineDocExample(Scene):
           def construct(self):
               base = Line(LEFT, RIGHT, color=BLUE)
               extended = ExtendedLine(base, extend_distance=1.0, color=RED)
               self.add(base, extended)
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
    """A right‑angle (perpendicular) sign.

    Draws a small L‑shaped corner at the intersection of two lines to
    indicate that they are perpendicular.  The sign consists of two short
    line segments.

    .. inheritance-diagram:: manim_extensions.mobjects.PerpendicularSign
       :parts: 1

    Parameters
    ----------
    line1 : :class:`manim.Line`
        The first line.
    line2 : :class:`manim.Line`
        The second line.
    length : float, optional
        Length of each leg of the corner. Defaults to ``0.25``.
    corner_direction : Union[numpy.ndarray, tuple, list, None], optional
        A direction vector that selects on which side of the intersection
        the corner is drawn.  If ``None`` (the default), the side that
        points toward the nearer endpoints of the two lines is chosen
        automatically.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.VGroup`.

    Attributes
    ----------
    intersection : numpy.ndarray
        The 3‑D intersection point of the two lines.  If the lines are
        parallel this attribute is not set.

    Examples
    --------

    .. manim:: PerpendicularSignDocExample
       :no_title:
       :save_last_frame:

       from manim_extensions import PerpendicularLine, PerpendicularSign

       class PerpendicularSignDocExample(Scene):
           def construct(self):
               base = Line(LEFT * 3, RIGHT * 3)
               perp = PerpendicularLine(UP * 1.5, base, color=YELLOW)
               sign = PerpendicularSign(base, perp, length=0.25, color=WHITE)
               self.add(base, perp, sign)
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

        # Compute the intersection of the two lines
        intersection = self._compute_intersection(line1, line2)
        if intersection is None:
            return

        # Get unit direction vectors on both sides of each line
        dirs1 = self._get_both_directions(line1, intersection)
        dirs2 = self._get_both_directions(line2, intersection)

        # Select the best pair of directions
        d1, d2 = self._select_directions(
            dirs1, dirs2, corner_direction
        )

        # Three vertices of the corner
        corner1 = intersection + length * d1
        corner2 = intersection + length * d2
        # Inner vertex: move along the sum of the two directions
        inner = intersection + length * d1 + length * d2

        # Two line segments that form the corner
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
        """Return the two unit direction vectors from *point* toward the line's endpoints."""
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
        """Select the best pair of directions based on *corner_direction*."""
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
            # Default: choose the pair pointing toward the nearer endpoints
            # (the pair with the largest norm of inner_dir)
            best = max(candidates, key=lambda c: np.linalg.norm(c[0] + c[1]))
            return best[0], best[1]

        corner_direction = np.array(corner_direction)
        corner_direction = corner_direction / np.linalg.norm(corner_direction)

        # Select the pair with the largest dot product with corner_direction
        best = max(
            candidates,
            key=lambda c: np.dot(c[2], corner_direction),
        )
        return best[0], best[1]
