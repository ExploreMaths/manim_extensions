from manim import *
from manim.typing import Point3D, Vector3DLike
import numpy as np
import platform
from typing import Any, Optional, Union

from PIL import Image, ImageChops, ImageDraw
import cv2


DEFAULT_CJK_FONT = "SimSun" if platform.system() == "Windows" else "Noto Serif CJK SC"
DEFAULT_MONO_FONT = "Cascadia Code" if platform.system() == "Windows" else "Ubuntu Mono"


class ChineseMathTex(MathTex):
    r"""A :class:`~manim.mobject.text.tex_mobject.MathTex` subclass that supports Chinese characters.

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
        Additional keyword arguments forwarded to :class:`~manim.mobject.text.tex_mobject.MathTex`.

    Examples
    --------

    .. manim:: ChineseMathTexDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import ChineseMathTex

       class ChineseMathTexDocExample(Scene):
           def construct(self):
               formula = ChineseMathTex(
                   r"\frac{1}{2} + \text{hello} = x",
                   tex_to_color_map={r"\text{hello}": RED},
               )
               self.add(formula)
    """


    def __init__(
        self,
        *texts: str,
        font: str = DEFAULT_CJK_FONT,
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
    """A dot with a :class:`~manim.mobject.text.tex_mobject.MathTex` label.

    Creates a :class:`~manim.mobject.geometry.Dot` at the given position and places a
    :class:`~manim.mobject.text.tex_mobject.MathTex` label next to it.

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
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Attributes
    ----------
    dot : :class:`~manim.mobject.geometry.Dot`
        The underlying dot mobject.
    dot_pos : numpy.ndarray
        The position of the dot.

    Examples
    --------

    .. manim:: LabelDotDocExample
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
        """Return the center of the underlying dot.

        Examples
        --------
        """
        return self.dot.get_center()

    def get_boundary_point(self, direction: Vector3DLike) -> Point3D:
        """Return the center of the underlying dot (boundary approximation).

        Examples
        --------
        """
        return self.dot.get_center()


class MathTexLine(VGroup):
    """A line segment paired with a :class:`~manim.mobject.text.tex_mobject.MathTex` formula.

    Creates a :class:`~manim.mobject.geometry.Line` and places a :class:`~manim.mobject.text.tex_mobject.MathTex`
    formula next to it in the specified direction.

    .. inheritance-diagram:: manim_extensions.mobjects.MathTexLine
       :parts: 1

    Parameters
    ----------
    formula : :class:`~manim.mobject.text.tex_mobject.MathTex`
        The formula to place beside the line.
    direction : numpy.ndarray, optional
        Direction of the formula relative to the line. Defaults to ``UP``.
    buff : float, optional
        Buffer between the formula and the line. Defaults to ``0.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.geometry.Line`.

    Examples
    --------

    .. manim:: MathTexLineDocExample
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
    r"""A brace with a :class:`~manim.mobject.text.tex_mobject.MathTex` formula.

    Creates a :class:`~manim.mobject.geometry.Brace` around a target mobject and places a
    :class:`~manim.mobject.text.tex_mobject.MathTex` formula next to the brace.

    .. inheritance-diagram:: manim_extensions.mobjects.MathTexBrace
       :parts: 1

    Parameters
    ----------
    target : :class:`~manim.mobject.mobject.Mobject`
        The mobject to be braced (e.g. a line, rectangle, etc.).
    formula : :class:`~manim.mobject.text.tex_mobject.MathTex`
        The formula to place beside the brace.
    direction : numpy.ndarray, optional
        Direction of the brace and formula relative to the target.
        Defaults to ``UP``.
    buff : float, optional
        Buffer between the formula and the brace. Defaults to ``0.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.geometry.Brace`.

    Examples
    --------

    .. manim:: MathTexBraceDocExample
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
    r"""A double arrow with a :class:`~manim.mobject.text.tex_mobject.MathTex` formula.

    Creates a :class:`~manim.mobject.geometry.DoubleArrow` and places a :class:`~manim.mobject.text.tex_mobject.MathTex`
    formula next to it in the specified direction.

    .. inheritance-diagram:: manim_extensions.mobjects.MathTexDoublearrow
       :parts: 1

    Parameters
    ----------
    formula : :class:`~manim.mobject.text.tex_mobject.MathTex`
        The formula to place beside the double arrow.
    direction : numpy.ndarray, optional
        Direction of the formula relative to the double arrow.
        Defaults to ``UP``.
    buff : float, optional
        Buffer between the formula and the double arrow. Defaults to ``0.5``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.geometry.DoubleArrow`.

    Examples
    --------

    .. manim:: MathTexDoublearrowDocExample
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
    creates a :class:`~manim.mobject.geometry.Line` from *point* to that foot.

    .. inheritance-diagram:: manim_extensions.mobjects.PerpendicularLine
       :parts: 1

    Parameters
    ----------
    point : Union[numpy.ndarray, tuple, list, :class:`~manim.mobject.mobject.Mobject`]
        The point from which the perpendicular is dropped.  If an
        :class:`~manim.mobject.mobject.Mobject` is given, its centre is used.
    line : :class:`~manim.mobject.geometry.Line`
        The target line.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.geometry.Line`.

    Attributes
    ----------
    point : numpy.ndarray
        The 3‑D point from which the perpendicular is drawn.
    target_line : :class:`~manim.mobject.geometry.Line`
        The line onto which the perpendicular is dropped.
    foot : numpy.ndarray
        The foot of the perpendicular on *target_line*.

    Examples
    --------

    .. manim:: PerpendicularLineDocExample
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

    Takes an existing :class:`~manim.mobject.geometry.Line` and extends it by
    *extend_distance* along its original direction on both sides.
    The style of the original line is preserved.

    .. inheritance-diagram:: manim_extensions.mobjects.ExtendedLine
       :parts: 1

    Parameters
    ----------
    line : :class:`~manim.mobject.geometry.Line`
        The original line segment to extend.
    extend_distance : float
        Distance to extend at each end.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.geometry.Line`.

    Examples
    --------

    .. manim:: ExtendedLineDocExample
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
    line1 : :class:`~manim.mobject.geometry.Line`
        The first line.
    line2 : :class:`~manim.mobject.geometry.Line`
        The second line.
    length : float, optional
        Length of each leg of the corner. Defaults to ``0.25``.
    corner_direction : Union[numpy.ndarray, tuple, list, None], optional
        A direction vector that selects on which side of the intersection
        the corner is drawn.  If ``None`` (the default), the side that
        points toward the nearer endpoints of the two lines is chosen
        automatically.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Attributes
    ----------
    intersection : numpy.ndarray
        The 3‑D intersection point of the two lines.  If the lines are
        parallel this attribute is not set.

    Examples
    --------

    .. manim:: PerpendicularSignDocExample
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


class FileTree(Code):
    """An ASCII file tree generated from a nested dictionary.

    Directories are automatically suffixed with ``/``.  Highlighting is
    performed by dynamically slicing each line based on physical coordinates,
    compatible with Manim 0.19.1 (spaces have no submobjects).

    .. inheritance-diagram:: manim_extensions.mobjects.FileTree
       :parts: 1

    Parameters
    ----------
    tree_dict : dict[str, dict | None]
        Nested dictionary representing the tree.  ``None`` or ``{}`` denotes
        an empty directory; a non-empty ``dict`` denotes a directory with
        children.
    font_size : float, optional
        Font size of the rendered text.  Defaults to ``DEFAULT_FONT_SIZE``.
    color : :class:`~manim.utils.color.ParsableManimColor`, optional
        Default colour of the tree text.  Defaults to ``WHITE``.
    **kwargs
        Additional keyword arguments forwarded to
        :class:`~manim.mobject.text.code_mobject.Code`.

    Examples
    --------

    .. manim:: FileTreeDocExample
       :save_last_frame:

       from manim import *
       from manim_extensions import FileTree

       class FileTreeDocExample(Scene):
           def construct(self):
               tree = FileTree({
                   "src": {
                       "main.py": None,
                       "utils": {
                           "helpers.py": None,
                       },
                   },
                   "README.md": None,
               })
               self.add(tree)
    """

    def __init__(
        self,
        tree_dict: dict[str, dict | None],
        font_size: float = DEFAULT_FONT_SIZE,
        color: ParsableManimColor = WHITE,
        **kwargs,
    ) -> None:
        if not isinstance(tree_dict, dict):
            raise TypeError(
                f"tree_dict must be a dict, got {type(tree_dict).__name__}"
            )
        self._tree = self._build_tree(tree_dict)
        super().__init__(
            code_string="\n".join(self._tree),
            language="text",
            add_line_numbers=False,
            paragraph_config={
                "font": DEFAULT_MONO_FONT,
                "font_size": font_size,
                "color": color,
                "line_spacing": 1,
            },
            **kwargs,
        )
        del self.submobjects[0]

    def highlight(
        self, line: int, color: ParsableManimColor = WHITE
    ) -> AnimationGroup:
        """Highlight the content of a specific line (excluding tree prefixes).

        Parameters
        ----------
        line : int
            Zero-based line index.
        color : :class:`~manim.utils.color.ParsableManimColor`, optional
            Highlight colour.  Defaults to ``WHITE``.

        Returns
        -------
        :class:`~manim.animation.composition.AnimationGroup`
            An animation that colours the line content.
        """
        if not self.submobjects:
            raise ValueError("Cannot highlight an empty tree.")
        if not (0 <= line < len(self.submobjects[0])):
            raise ValueError(
                f"Line index {line} out of range "
                f"[0, {len(self.submobjects[0]) - 1}]"
            )

        this_line = self._tree[line]
        content_start = len(this_line) - len(this_line.lstrip("─├└│ "))
        prefix = this_line[:content_start]
        begin_index = len(prefix.replace(" ", ""))

        if not self.submobjects[0]:
            return Wait(0)

        return AnimationGroup(
            VGroup(self.submobjects[0][line][begin_index:]).animate.set_color(
                color
            )
        )

    @staticmethod
    def _build_tree(
        data, prefix: str = "", is_root: bool = True
    ) -> list[str]:
        """Recursively build ASCII tree lines from a nested dictionary."""
        lines: list[str] = []
        if not isinstance(data, dict):
            return lines
        items = list(data.items())
        count = len(items)
        for i, (name, value) in enumerate(items):
            is_last = i == count - 1
            is_dir = isinstance(value, dict)
            display_name = name + ("/" if is_dir else "")
            if is_root:
                lines.append(display_name)
                if is_dir:
                    lines.extend(FileTree._build_tree(value, "", False))
            else:
                connector = "└── " if is_last else "├── "
                lines.append(prefix + connector + display_name)
                if is_dir:
                    extension = "    " if is_last else "│   "
                    lines.extend(
                        FileTree._build_tree(value, prefix + extension, False)
                    )
        return lines


class CropImageMobject(ImageMobject):
    """An :class:`~manim.mobject.types.image_mobject.ImageMobject` with rounded-corner
    cropping applied through an alpha mask.

    Accepts a file path, a NumPy array, or a PIL image as input.

    .. inheritance-diagram:: manim_extensions.mobjects.CropImageMobject
       :parts: 1

    Parameters
    ----------
    filename_or_array : Union[str, numpy.ndarray, :class:`~PIL.Image.Image`]
        The image source: a path to an image file, a NumPy array, or a PIL image.
    corner_radius : Union[int, float], optional
        Radius of the rounded corners.  A value in ``(0, 1]`` is interpreted as
        a fraction of the smaller image dimension; larger values are treated as
        pixel radii.  Defaults to ``0.1``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.image_mobject.ImageMobject`.
    """

    def __init__(
        self,
        filename_or_array: Union[str, np.ndarray, Image.Image],
        corner_radius: Union[int, float] = 0.1,
        **kwargs: Any
    ) -> None:
        if isinstance(filename_or_array, str):
            img = Image.open(filename_or_array)
        elif isinstance(filename_or_array, np.ndarray):
            img = Image.fromarray(filename_or_array)
        elif isinstance(filename_or_array, Image.Image):
            img = filename_or_array
        else:
            super().__init__(filename_or_array, **kwargs)
            return

        img = img.convert("RGBA")
        if isinstance(corner_radius, (int, float)):
            if 0 < corner_radius <= 1.0:
                radius = int(min(img.size) * corner_radius)
            else:
                radius = int(corner_radius)
        else:
            radius = 0

        mask = Image.new("L", img.size, 0)
        if radius > 0:
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle(
                (0, 0, img.size[0], img.size[1]),
                radius=radius,
                fill=255
            )
        else:
            mask.paste(255, (0, 0, img.size[0], img.size[1]))

        r, g, b, a = img.split()
        a = ImageChops.multiply(a, mask)
        img = Image.merge("RGBA", (r, g, b, a))
        super().__init__(np.array(img), **kwargs)


class VideoMobject(ImageMobject):
    """An :class:`~manim.mobject.types.image_mobject.ImageMobject` that plays a video
    file via OpenCV.

    The video can be looped, rate-changed, and controlled with ``play``,
    ``pause``, ``stop``, ``seek``, and ``reset``.

    .. inheritance-diagram:: manim_extensions.mobjects.VideoMobject
       :parts: 1

    Parameters
    ----------
    filename : str
        Path to the video file.
    loop : bool, optional
        Whether the video loops once it reaches the end.  Defaults to ``False``.
    rate : float, optional
        Playback speed multiplier.  Defaults to ``1.0``.
    **kwargs
        Additional keyword arguments forwarded to :class:`~manim.mobject.types.image_mobject.ImageMobject`.

    Attributes
    ----------
    filename : str
        Path to the video file.
    """

    def __init__(
        self,
        filename: str,
        loop: bool = False,
        rate: float = 1.0,
        **kwargs: Any
    ) -> None:
        self.filename = filename
        self.loop = loop
        self.rate = float(rate)

        cap = cv2.VideoCapture(filename)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise ValueError(f"Cannot read video file: {filename}")

        first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        super().__init__(first_frame, **kwargs)

        self._cap = cv2.VideoCapture(filename)
        self._fps = self._cap.get(cv2.CAP_PROP_FPS) or 30.0
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._duration = (
            self._total_frames / self._fps if self._fps > 0 else 0.0
        )

        self._frame_idx = 0
        self._elapsed = 0.0
        self._finished = False
        self._playing = False
        self._updater_ref = lambda mob, dt: self._video_updater(mob, dt)

    @property
    def duration(self) -> float:
        """Total playback duration in seconds, adjusted by the rate."""
        return self._duration / self.rate if self.rate > 0 else 0.0

    def _video_updater(self, mob: "VideoMobject", dt: float) -> None:
        """Internal updater that advances the video frame on each render step."""
        if not self._playing or self._finished:
            return

        self._elapsed += dt
        target_idx = int(self._elapsed * self._fps * self.rate)

        while self._frame_idx < target_idx:
            ret, frame = self._cap.read()
            if not ret:
                if self.loop:
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self._frame_idx = 0
                    self._elapsed = 0.0
                    target_idx = int(self._elapsed * self._fps * self.rate)
                    continue
                else:
                    self._finished = True
                    self._playing = False
                    self.remove_updater(self._updater_ref)
                    return

            self._frame_idx += 1
            self.pixel_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    def __deepcopy__(self, memo: dict) -> "VideoMobject":
        """Deep-copy the mobject, reopening the video capture for the clone."""
        cap = self._cap
        self._cap = None
        try:
            result = super().__deepcopy__(memo)
        finally:
            self._cap = cap

        result._cap = cv2.VideoCapture(self.filename)
        result._frame_idx = self._frame_idx
        result._elapsed = self._elapsed
        result._finished = self._finished
        result._playing = False
        result._updater_ref = lambda mob, dt: result._video_updater(mob, dt)
        return result

    def play(self, scene: Optional[Scene] = None) -> "VideoMobject":
        """Start video playback and optionally block the scene for its duration.

        Args:
            scene: If given, the scene waits for the full video duration.

        Returns:
            The :class:`VideoMobject` instance for chaining.
        """
        if self._finished:
            self.reset()
        self._playing = True
        if self._updater_ref not in self.updaters:
            self.add_updater(self._updater_ref)
        if scene is not None:
            scene.wait(self.duration)
        return self

    def pause(self) -> "VideoMobject":
        """Pause playback without removing the updater."""
        self._playing = False
        return self

    def resume(self) -> "VideoMobject":
        """Resume paused playback."""
        self._playing = True
        return self

    def stop(self) -> "VideoMobject":
        """Stop playback and remove the updater."""
        self._playing = False
        if self._updater_ref in self.updaters:
            self.remove_updater(self._updater_ref)
        return self

    def reset(self) -> "VideoMobject":
        """Seek to the first frame and reset all playback state."""
        if self._cap.isOpened():
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self._frame_idx = 0
        self._elapsed = 0.0
        self._finished = False
        return self

    def seek(self, time: float) -> "VideoMobject":
        """Seek to a specific timestamp in seconds.

        Args:
            time: Target time in seconds, clamped to ``[0, duration]``.

        Returns:
            The :class:`VideoMobject` instance for chaining.
        """
        if not self._cap.isOpened():
            return self
        frame_idx = int(np.clip(time, 0, self._duration) * self._fps)
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        self._frame_idx = frame_idx
        self._elapsed = time
        ret, frame = self._cap.read()
        if ret:
            self._frame_idx += 1
            self.pixel_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        return self

    def __del__(self) -> None:
        """Release the OpenCV capture on garbage collection."""
        if (
            hasattr(self, "_cap")
            and self._cap is not None
            and self._cap.isOpened()
        ):
            self._cap.release()
