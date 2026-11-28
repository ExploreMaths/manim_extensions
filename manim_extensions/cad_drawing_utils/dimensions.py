# SPDX-FileCopyrightText: 2020 GarryBGoode
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""CAD dimension mobjects: linear and angular dimensions with arrows and labels."""

from __future__ import annotations
from typing import Any, Self, cast
from collections.abc import Hashable, Mapping

from manim.typing import Point3D, Vector3D
from manim import (
    Arc,
    DEFAULT_ARROW_TIP_LENGTH,
    DEFAULT_STROKE_WIDTH,
    DEGREES,
    DOWN,
    LEFT,
    Line,
    Mobject,
    ORIGIN,
    PI,
    RIGHT,
    Text,
    UP,
    VDict,
    VMobject,
    angle_of_vector,
    normalize,
    rotate_vector,
)
import numpy as np
from .utils import angle_between_vectors_signed
from .round_corners import *
from .path_mapper import *


class _VDictAddMixin(VDict):
    """A :class:`~manim.mobject.types.vectorized_mobject.VDict` accepting any Mobject value."""

    def add(self, *mobjects: object) -> Self:
        """Insert a named mapping or ordinary Mobjects, narrowing values for VDict.

        Parameters
        ----------
        mobjects
            A single mapping of names to Mobjects, or ordinary Mobjects.

        Returns
        -------
            This mixin instance.
        """
        if len(mobjects) == 1 and isinstance(mobjects[0], Mapping):
            mapping = cast(Mapping[str, Mobject], mobjects[0])
            entries: dict[Hashable, VMobject] = {
                key: cast(VMobject, value) for key, value in mapping.items()
            }
            VDict.add(self, entries)
        else:
            Mobject.add(self, *cast(tuple[Mobject, ...], mobjects))
        return self


class PointerLabelFree(_VDictAddMixin):
    """A labelled pointer that is not attached to a mobject.

    Parameters
    ----------
    point
        Anchor point of the pointer.
    text
        Label text or a mobject used as the label.
    offset_vector
        Direction and length of the leader line.
    pointer_offset
        Extra gap between the anchor and the arrow tip.
    **kwargs
        Keyword arguments forwarded to the text mobject.

    Examples
    --------
    .. manim:: PointerLabelFreeScene
       :save_last_frame:

       from manim import *
       from manim_extensions.cad_drawing_utils import PointerLabelFree

       class PointerLabelFreeScene(Scene):
           def construct(self):
               pointer = PointerLabelFree(LEFT, "radius", offset_vector=UP + RIGHT)
               self.add(pointer.scale(2))
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        point: Point3D,
        text: str | Mobject,
        offset_vector: Vector3D = RIGHT + DOWN,
        pointer_offset: float = 0,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        text_buff = 0.1
        if not "stroke_width" in kwargs:
            kwargs["stroke_width"] = DEFAULT_STROKE_WIDTH
        super().__init__(**kwargs)

        textmob: Mobject
        if isinstance(text, str):
            textmob = Text(text, **kwargs)
        elif isinstance(text, Mobject):
            textmob = text
        else:
            textmob = Text("A", **kwargs)
        self.add({"text": textmob})
        self.twidth = (
            self["text"].get_critical_point(RIGHT)
            - self["text"].get_critical_point(LEFT)
        )[0]
        self.twidth = self.twidth + text_buff * 2

        if "stroke_width" in kwargs:
            stroke_width_loc = kwargs["stroke_width"]
        else:
            stroke_width_loc = DEFAULT_STROKE_WIDTH

        self.pointer_offset = pointer_offset + stroke_width_loc / 100

        dim_line = VMobject(**kwargs).set_points_as_corners(
            [
                point + normalize(offset_vector) * self.pointer_offset,
                point + offset_vector,
                point + offset_vector + self.twidth * np.sign(offset_vector[0]) * RIGHT,
            ]
        )
        self.add({"line": dim_line})
        self.add({"arrow": CADArrowHead(self["line"], anchor_point=0, **kwargs)})
        self["arrow"].arrowhead.rotate(PI, about_point=ORIGIN)
        self["arrow"].add_updater(self["arrow"].default_updater)
        self["arrow"].update()
        theight = (
            self["text"].get_critical_point(UP) - self["text"].get_critical_point(DOWN)
        )[1]
        self["text"].move_to(
            self["line"].points[3, :] + UP * theight * 0.75,
            aligned_edge=LEFT * np.sign(offset_vector[0]),
        )

    def update_point(
        self, point: Point3D, offset_vector: Vector3D = RIGHT + DOWN
    ) -> None:
        """Move the pointer to a new anchor point.

        Parameters
        ----------
        point
            New anchor point.
        offset_vector
            Direction and length of the leader line.

        Returns
        -------
            The line and text positions are updated in place.
        """
        self["line"].set_points_as_corners(
            [
                point + normalize(offset_vector) * self.pointer_offset,
                point + offset_vector,
                point + offset_vector + self.twidth * np.sign(offset_vector[0]) * RIGHT,
            ]
        )

        theight = (
            self["text"].get_critical_point(UP) - self["text"].get_critical_point(DOWN)
        )[1]
        self["text"].move_to(
            self["line"].points[3, :] + UP * theight * 0.75,
            aligned_edge=LEFT * np.sign(offset_vector[0]),
        )


class PointerToMob(PointerLabelFree):
    """A labelled pointer attached to a point on a mobject.

    Parameters
    ----------
    mob
        Mobject to point at.
    proportion
        Normalized position along the mobject.
    text
        Label text or a mobject used as the label.
    dist
        Distance of the label from the anchor.
    pointer_offset
        Extra gap between the anchor and the arrow tip.
    **kwargs
        Keyword arguments forwarded to the label and leader line.

    Examples
    --------
    .. manim:: PointerToMobScene
       :save_last_frame:

       from manim import *
       from manim_extensions.cad_drawing_utils import PointerToMob

       class PointerToMobScene(Scene):
           def construct(self):
               circle = Circle(radius=1).shift(LEFT * 2)
               pointer = PointerToMob(circle, 0.25, "P", dist=1)
               self.add(circle, pointer)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        mob: Mobject,
        proportion: float,
        text: str | Mobject,
        dist: float = 1,
        pointer_offset: float = 0,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        point = mob.point_from_proportion(proportion)

        # if the mob center and point happens to be the same, it causes problems
        # it can happen if all the mob is 1 point
        offset_ref = point - mob.get_center()
        if "offset" in kwargs:
            offset = kwargs["offset"]
            kwargs.pop("offset")
        else:
            if np.linalg.norm(offset_ref) > 1e-6:
                offset = normalize(point - mob.get_center()) * dist
            else:
                # I had no better idea to handle this than to go upright
                offset = normalize(RIGHT + UP) * dist
        super().__init__(
            point, text, offset_vector=offset, pointer_offset=pointer_offset, **kwargs
        )

    def update_mob(self, mob: Mobject, proportion: float, dist: float = 1) -> None:
        """Follow a point on a mobject and update the pointer.

        Parameters
        ----------
        mob
            Mobject to point at.
        proportion
            Normalized position along the mobject.
        dist
            Distance of the label from the point.

        Returns
        -------
            The pointer is repositioned in place.
        """
        point = mob.point_from_proportion(proportion)
        # if the mob center and point happens to be the same, it causes problems
        # it can happen if all the mob is 1 point
        offset_ref = point - mob.get_center()
        if np.linalg.norm(offset_ref) > 1e-6:
            offset = normalize(point - mob.get_center()) * dist
        else:
            # I had no better idea to handle this than to go upright
            offset = normalize(RIGHT + UP) * dist
        super().update_point(point, offset)


class LinearDimension(_VDictAddMixin):
    """A linear dimension with arrows and a measurement label.

    Parameters
    ----------
    start
        First measured point.
    end
        Second measured point.
    text
        Measurement label; a distance label is generated when omitted.
    direction
        Direction of the dimension line; derived from the points when
        zero.
    outside_arrow
        Whether the arrow heads point outward.
    offset
        Distance of the dimension line from the measured points.
    ext_line_offset
        Length of the extension lines.
    tip_len
        Length of the arrow tips.
    **kwargs
        Keyword arguments forwarded to the dimension components.

    Examples
    --------
    .. manim:: LinearDimensionScene
       :save_last_frame:

       from manim import *
       from manim_extensions.cad_drawing_utils import LinearDimension

       class LinearDimensionScene(Scene):
           def construct(self):
               line = Line(LEFT * 2, RIGHT * 2)
               dimension = LinearDimension(line.get_start(), line.get_end(), offset=0.7)
               self.add(line, dimension)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        start: Point3D,
        end: Point3D,
        text: str | Mobject | None = None,
        direction: Vector3D = ORIGIN,
        outside_arrow: bool = False,
        offset: float = 2,
        ext_line_offset: float = 0,
        tip_len: float = DEFAULT_ARROW_TIP_LENGTH,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        super().__init__(**kwargs)
        self.start = start
        self.end = end
        diff_vect = end - start
        norm_vect = normalize(rotate_vector(diff_vect, PI / 2))

        if direction is ORIGIN:
            ofs_vect = norm_vect * offset
            ofs_dir = norm_vect
        else:
            ofs_dir = normalize(direction)
            ofs_vect = ofs_dir * offset
        if not "stroke_width" in kwargs:
            kwargs["stroke_width"] = DEFAULT_STROKE_WIDTH

        startpoint = start + ofs_dir * np.dot((diff_vect), ofs_dir) / 2 + ofs_vect
        endpoint = end - ofs_dir * np.dot((diff_vect), ofs_dir) / 2 + ofs_vect

        self.arrow_offset: float = 0
        if not outside_arrow:
            if "stroke_width" in kwargs:
                self.arrow_offset = kwargs["stroke_width"] * 1 / 100
            else:
                self.arrow_offset = DEFAULT_STROKE_WIDTH * 1 / 100
            ext_dir = normalize(endpoint - startpoint)
            main_line = Line(
                start=startpoint + self.arrow_offset * ext_dir,
                end=endpoint - self.arrow_offset * ext_dir,
                **kwargs,
            )
            arrow1 = CADArrowHead(
                main_line, anchor_point=1, arrow_size=tip_len, reversed_arrow=False
            )
            arrow2 = CADArrowHead(
                main_line, anchor_point=0, arrow_size=tip_len, reversed_arrow=True
            )
        else:
            extension = tip_len * 3 * (normalize(endpoint - startpoint))
            main_line = Line(
                start=startpoint - extension, end=endpoint + extension, **kwargs
            )
            arrow1 = CADArrowHead(
                main_line, anchor_point=1, arrow_size=tip_len, reversed_arrow=True
            )
            arrow1.arrowhead.shift(-np.linalg.norm(extension) * RIGHT)
            arrow1.default_updater(0)
            arrow2 = CADArrowHead(
                main_line, anchor_point=0, arrow_size=tip_len, reversed_arrow=False
            )
            arrow2.arrowhead.shift(np.linalg.norm(extension) * RIGHT)
            arrow2.default_updater(0)
            arrow1.update()
            arrow2.update()

        self.add(
            {
                "ext_line_1": Line(
                    start=start + ofs_dir * ext_line_offset,
                    end=startpoint + 0.25 * (normalize(startpoint - start)),
                    **kwargs,
                ),
            }
        )
        self.add(
            {
                "ext_line_2": Line(
                    start=end + ofs_dir * ext_line_offset,
                    end=endpoint + 0.25 * (normalize(endpoint - end)),
                    **kwargs,
                ),
            }
        )
        self.add({"main_line": main_line})
        self.add({"arrow1": arrow1})
        self.add({"arrow2": arrow2})

        textmob: Mobject
        if isinstance(text, str):
            textmob = Text(text, **kwargs)
            textmob.set_stroke(opacity=0)
        elif isinstance(text, Mobject):
            textmob = text
        else:
            dist = np.linalg.norm(startpoint - endpoint)
            textmob = Text(f"{dist:.2}", **kwargs)
            textmob.set_stroke(opacity=0)

        text_angle = (main_line.get_angle() + PI / 2) % PI - PI / 2
        if abs(text_angle + PI / 2) < 1e-8:
            text_angle = PI / 2
        self.text_h = textmob.height
        text_w = textmob.width
        if not outside_arrow:
            text_space = np.linalg.norm(self.start - self.end) - tip_len * 2
        else:
            text_space = np.linalg.norm(self.start - self.end)

        if text_w > (text_space * 0.8):
            textmob.scale((text_space * 0.8) / text_w)
            self.text_h = textmob.height

        textmob.rotate(text_angle)
        textmob.move_to(
            self["main_line"].get_center() + rotate_vector(UP, text_angle) * self.text_h
        )
        self.add({"text": textmob})


class AngleDimension3Point(_VDictAddMixin):
    """An angular dimension defined by three points.

    Parameters
    ----------
    start
        First point on the angle.
    end
        Second point on the angle.
    arc_center
        Vertex of the angle.
    offset
        Radius of the dimension arc.
    text
        Measurement label; an angle label is generated when omitted.
    outside_arrow
        Whether the arrow heads point outward.
    ext_line_offset
        Length of the extension lines.
    tip_len
        Length of the arrow tips.
    **kwargs
        Keyword arguments forwarded to the dimension components.

    Examples
    --------
    .. manim:: AngleDimension3PointScene
       :save_last_frame:

       from manim import *
       from manim_extensions.cad_drawing_utils import AngleDimension3Point

       class AngleDimension3PointScene(Scene):
           def construct(self):
               center, start, end = ORIGIN, RIGHT * 2, UP * 2
               dimension = AngleDimension3Point(start, end, center, offset=0.4)
               self.add(dimension)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        start: Point3D,
        end: Point3D,
        arc_center: Point3D,
        offset: float = 2,
        text: str | Mobject | None = None,
        outside_arrow: bool = False,
        ext_line_offset: float = 0,
        tip_len: float = DEFAULT_ARROW_TIP_LENGTH,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        super().__init__(**kwargs)

        if not "stroke_width" in kwargs:
            kwargs["stroke_width"] = DEFAULT_STROKE_WIDTH

        self.angle = angle_between_vectors_signed(start - arc_center, end - arc_center)
        radius = (
            np.linalg.norm(start - arc_center) + np.linalg.norm(end - arc_center)
        ) / 2 + offset
        angle_0 = angle_of_vector(start - arc_center)
        angle_1 = angle_between_vectors_signed(start - arc_center, end - arc_center)

        base_arc = Arc(
            radius=radius,
            start_angle=angle_0,
            arc_center=arc_center,
            angle=angle_1,
            **kwargs,
        )
        arc_p0 = base_arc.point_from_proportion(0)
        arc_p1 = base_arc.point_from_proportion(1)
        line1 = Line(
            start=start + normalize(arc_p0 - start) * ext_line_offset,
            end=arc_p0 + normalize(arc_p0 - start) * tip_len,
            **kwargs,
        )
        line2 = Line(
            start=end + normalize(arc_p1 - end) * ext_line_offset,
            end=arc_p1 + normalize(arc_p1 - end) * tip_len,
            **kwargs,
        )
        # self.add(line1,line2)
        self.add({"ext_line_1": line1})
        self.add({"ext_line_2": line2})
        if not outside_arrow:

            if "stroke_width" in kwargs:
                self.arrow_offset = kwargs["stroke_width"] * 1 / 100
            else:
                self.arrow_offset = DEFAULT_STROKE_WIDTH * 1 / 100

            arrow1 = CADArrowHead(
                base_arc, anchor_point=1, arrow_size=tip_len, reversed_arrow=False
            )
            arrow2 = CADArrowHead(
                base_arc, anchor_point=0, arrow_size=tip_len, reversed_arrow=True
            )

            arrow1.arrowhead.shift(LEFT * self.arrow_offset)
            arrow2.arrowhead.shift(RIGHT * self.arrow_offset)
            arrow1.generate_points()
            arrow2.generate_points()
            self.add({"base_arc": base_arc})
            self.add({"arrow_1": arrow1})
            self.add({"arrow_2": arrow2})
        else:
            extension = tip_len * 3 * np.sign(angle_1)
            angle_ext = extension / radius

            base_arc = Arc(
                radius=radius,
                start_angle=angle_0 - angle_ext,
                angle=+self.angle + angle_ext * 2,
                arc_center=arc_center,
                **kwargs,
            )
            arrow1 = CADArrowHead(
                base_arc, anchor_point=1, arrow_size=tip_len, reversed_arrow=True
            )
            arrow1.arrowhead.shift(extension * RIGHT)
            arrow1.default_updater(0)
            arrow2 = CADArrowHead(
                base_arc, anchor_point=0, arrow_size=tip_len, reversed_arrow=False
            )
            arrow2.arrowhead.shift(-extension * RIGHT)
            arrow2.default_updater(0)
            self.add({"base_arc": base_arc})
            self.add({"arrow_1": arrow1})
            self.add({"arrow_2": arrow2})

        textmob: Mobject
        if isinstance(text, str):
            textmob = Text(text, **kwargs)
            textmob.set_stroke(opacity=0)
        elif isinstance(text, Mobject):
            textmob = text
        else:
            textmob = Text(f"{abs(angle_1/DEGREES):.0f}°", **kwargs)
            textmob.set_stroke(opacity=0)

        pos_text = base_arc.point_from_proportion(0.5)
        angle_text = (
            angle_of_vector(
                base_arc.point_from_proportion(0.5 + 1e-6)
                - (base_arc.point_from_proportion(0.5 - 1e-6))
            )
            + PI / 2
        ) % PI - PI / 2
        if abs(angle_text + PI / 2) < 1e-8:
            angle_text = PI / 2
        self.text_h = textmob.height
        textmob.rotate(angle_text)
        textmob.move_to(pos_text + rotate_vector(UP, angle_text) * self.text_h)
        self.add({"text": textmob})


class AngleDimensionMob(AngleDimension3Point):
    """An angular dimension measured between two mobject points.

    Parameters
    ----------
    Mob
        Mobject that defines the angle.
    start_proportion
        Normalized position of the first point.
    end_proportion
        Normalized position of the second point.
    **kwargs
        Keyword arguments forwarded to the parent dimension.

    Examples
    --------
    .. manim:: AngleDimensionMobScene
       :save_last_frame:

       from manim import *
       from manim_extensions.cad_drawing_utils import AngleDimensionMob

       class AngleDimensionMobScene(Scene):
           def construct(self):
               arc = Arc(radius=2, start_angle=0, angle=PI / 2)
               dimension = AngleDimensionMob(arc, 0, 1)
               self.add(arc, dimension)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        Mob: Mobject,
        start_proportion: float,
        end_proportion: float,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:
        start = Mob.point_from_proportion(start_proportion)
        end = Mob.point_from_proportion(end_proportion)
        start_diff_points = np.clip(
            np.array([start_proportion + 1e-6, start_proportion - 1e-6]), 0, 1
        )
        end_diff_points = np.clip(
            np.array([end_proportion + 1e-6, end_proportion - 1e-6]), 0, 1
        )
        v_start = normalize(
            Mob.point_from_proportion(start_diff_points[1])
            - Mob.point_from_proportion(start_diff_points[0])
        )
        v_end = normalize(
            Mob.point_from_proportion(end_diff_points[1])
            - Mob.point_from_proportion(end_diff_points[0])
        )
        v_mat = np.concatenate(
            (np.reshape(v_start[0:2], (2, 1)), np.reshape(-v_end[0:2], (2, 1))), axis=1
        )
        dP = end - start
        k = np.linalg.solve(v_mat, dP[0:2])
        center = start + k[0] * v_start
        # center = np.reshape(center,(3,0))
        super().__init__(start, end, center.flatten(), **kwargs)


class CADArrowHead(CurveWarp):
    """An arrow head that follows a target curve.

    Parameters
    ----------
    target_curve
        Curve along which the arrow head travels.
    anchor_point
        Proportion of the curve where the arrow is anchored.
    arrow_size
        Width of the arrow head.
    reversed_arrow
        Whether the arrow points backwards.
    **kwargs
        Keyword arguments forwarded to the curve warp.

    Examples
    --------
    .. manim:: CADArrowHeadScene
       :save_last_frame:

       from manim import *
       from manim_extensions.cad_drawing_utils import CADArrowHead

       class CADArrowHeadScene(Scene):
           def construct(self):
               curve = Arc(radius=2, start_angle=0, angle=PI / 2)
               head = CADArrowHead(curve, anchor_point=1, arrow_size=0.2)
               self.add(curve, head)
    """

    def __init__(  # explicit-any-ok: **kwargs forwarded through Manim's untyped boundary
        self,
        target_curve: VMobject,
        anchor_point: float = 1,
        arrow_size: float = DEFAULT_ARROW_TIP_LENGTH,
        reversed_arrow: bool = False,
        **kwargs: Any,  # explicit-any-ok: forwarded unchanged through Manim's untyped **kwargs boundary
    ) -> None:

        # set default value
        self.__reversed_arrow = False
        self.arrowhead = VMobject()
        self.arrowhead.set_points_as_corners([(LEFT * 2 + UP), ORIGIN, LEFT * 2 + DOWN])

        # set input value
        self.reversed_arrow = reversed_arrow
        self.set_arrow_size(arrow_size)
        self.arrowhead.match_style(target_curve)

        super().__init__(
            self.arrowhead, target_curve, anchor_point=anchor_point, **kwargs
        )

    def default_updater(self, mob: Mobject | float = 0) -> None:
        """Refresh the arrow geometry after the target curve changes.

        Parameters
        ----------
        mob
            Target curve supplied by the updater.

        Returns
        -------
            The arrow points are regenerated in place.
        """
        self.PM.generate_length_map()
        self.generate_points()

    def get_tip_pos(self) -> float:
        """Return the x coordinate of the arrow tip.

        Returns
        -------
            The horizontal position of the tip along the target curve.
        """
        if self.__reversed_arrow:
            return cast(float, self.arrowhead.get_critical_point(LEFT)[0])
        else:
            return cast(float, self.arrowhead.get_critical_point(RIGHT)[0])

    def set_arrow_size(self, arrow_size: float) -> None:
        """Resize the arrow head while keeping its tip fixed.

        Parameters
        ----------
        arrow_size
            Target width of the arrow head.

        Returns
        -------
            The arrow head is scaled in place.
        """
        act_size = (
            self.arrowhead.get_critical_point(RIGHT)
            - self.arrowhead.get_critical_point(LEFT)
        )[0]
        if act_size != 0:
            self.arrowhead.shift(-self.get_tip_pos() * RIGHT)
            self.arrowhead.points *= arrow_size / act_size
            self.arrowhead.shift(+self.get_tip_pos() * RIGHT)

    def flip_arrow(self) -> None:
        """Flip the arrow head horizontally.

        Returns
        -------
            The arrow head is flipped in place.
        """
        self.arrowhead.flip()

    @property
    def reversed_arrow(self) -> bool:
        """Set whether the arrow points backwards.

        Parameters
        ----------
        rev
            New reversed state.

        Returns
        -------
            The arrow is flipped when the state changes.
        """
        return self.__reversed_arrow

    @reversed_arrow.setter
    def reversed_arrow(self, rev: bool) -> None:
        """Set whether the arrow points backwards.

        Parameters
        ----------
        rev
            New reversed state.

        Returns
        -------
            The arrow is flipped when the state changes.
        """
        if rev != self.__reversed_arrow:
            self.flip_arrow()
        self.__reversed_arrow = rev
