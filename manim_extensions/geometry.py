from manim import *
import math
import numpy as np
from typing import Optional, Tuple, Union


def CircleInt(
    circle1: Circle, circle2: Circle
) -> Optional[Tuple[list[float], list[float]]]:
    """Compute the intersection points of two circles.

    Solves the geometric intersection of two circles in the XY‑plane.

    Parameters
    ----------
    circle1 : :class:`manim.Circle`
        The first circle.
    circle2 : :class:`manim.Circle`
        The second circle.

    Returns
    -------
    Optional[Tuple[list[float], list[float]]]
        A tuple ``(point1, point2)`` where each point is ``[x, y, 0]`` if the
        circles intersect; otherwise ``None``.

    Examples
    --------
    .. code-block:: python

        from manim_extensions import CircleInt

        c1 = Circle(radius=2).shift(LEFT)
        c2 = Circle(radius=2).shift(RIGHT)
        result = CircleInt(c1, c2)  # ([x1, y1, 0], [x2, y2, 0]) or None
    """
    circle1_center = circle1.get_center()
    circle1_radius = circle1.radius
    circle2_center = circle2.get_center()
    circle2_radius = circle2.radius
    x1, y1, _ = circle1_center
    x2, y2, _ = circle2_center
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if d > circle1_radius + circle2_radius or d < abs(circle1_radius - circle2_radius):
        return None
    a = (circle1_radius**2 - circle2_radius**2 + d**2) / (2 * d)
    h = math.sqrt(circle1_radius**2 - a**2)
    xm = x1 + a * (x2 - x1) / d
    ym = y1 + a * (y2 - y1) / d
    xs1 = xm + h * (y2 - y1) / d
    xs2 = xm - h * (y2 - y1) / d
    ys1 = ym - h * (x2 - x1) / d
    ys2 = ym + h * (x2 - x1) / d
    return [xs1, ys1, 0], [xs2, ys2, 0]


def LineCircleInt(
    line: Line, circle: Circle
) -> Optional[Union[Tuple[np.ndarray, np.ndarray], np.ndarray]]:
    """Compute the intersection points of a line segment and a circle.

    Only points that lie within the segment parameter range ``[0, 1]``
    are returned.

    Parameters
    ----------
    line : :class:`manim.Line`
        The line segment.
    circle : :class:`manim.Circle`
        The circle.

    Returns
    -------
    Optional[Union[Tuple[numpy.ndarray, numpy.ndarray], numpy.ndarray]]
        * Two intersection points as a tuple if the segment cuts the circle
          twice.
        * A single :class:`numpy.ndarray` if the segment is tangent to the
          circle.
        * ``None`` if there is no intersection.

    Examples
    --------
    .. code-block:: python

        from manim_extensions import LineCircleInt

        line = Line(LEFT * 3, RIGHT * 3)
        circle = Circle(radius=1)
        result = LineCircleInt(line, circle)
    """
    p1 = line.get_start()
    p2 = line.get_end()
    c = circle.get_center()
    r = circle.radius
    dx, dy, _ = p2 - p1
    cx, cy, _ = p1 - c
    a = dx**2 + dy**2
    b = 2 * (dx * cx + dy * cy)
    c = cx**2 + cy**2 - r**2
    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        return None
    t1 = (-b + math.sqrt(discriminant)) / (2 * a)
    t2 = (-b - math.sqrt(discriminant)) / (2 * a)
    intersections = []
    for t in [t1, t2]:
        if 0 <= t <= 1:
            intersection = p1 + t * (p2 - p1)
            intersections.append(intersection)
    try:
        return intersections[0], intersections[1]
    except Exception:
        try:
            return intersections[0]
        except Exception:
            return None


def LineInt(line1: Line, line2: Line) -> Optional[list[float]]:
    """Compute the intersection of two (infinitely extended) lines.

    Calculates the intersection point in the 2‑D plane.  The result is
    **not** restricted to the segment endpoints.

    Parameters
    ----------
    line1 : :class:`manim.Line`
        The first line.
    line2 : :class:`manim.Line`
        The second line.

    Returns
    -------
    Optional[list[float]]
        The intersection point ``[x, y, 0]`` if the lines are not parallel;
        otherwise ``None``.

    Examples
    --------
    .. code-block:: python

        from manim_extensions import LineInt

        l1 = Line(LEFT, RIGHT)
        l2 = Line(DOWN, UP)
        result = LineInt(l1, l2)  # [0.0, 0.0, 0] or None
    """

    def det(a: tuple[float, float], b: tuple[float, float]) -> float:
        return a[0] * b[1] - a[1] * b[0]

    p1 = line1.get_start()[:2]
    p2 = line1.get_end()[:2]
    p3 = line2.get_start()[:2]
    p4 = line2.get_end()[:2]
    xdiff = (p1[0] - p2[0], p3[0] - p4[0])
    ydiff = (p1[1] - p2[1], p3[1] - p4[1])
    div = det(xdiff, ydiff)
    if div == 0:
        return None
    d = (det(p1, p2), det(p3, p4))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return [x, y, 0]


def LineArcInt(
    line: Line, arc: Arc
) -> Optional[Union[Tuple[list[float], list[float]], list[float]]]:
    """Compute the intersection points of a line segment and an arc.

    The function checks whether each candidate intersection point actually
    lies within the angular span of the arc.

    Parameters
    ----------
    line : :class:`manim.Line`
        The line segment.
    arc : :class:`manim.Arc`
        The arc.

    Returns
    -------
    Optional[Union[Tuple[list[float], list[float]], list[float]]]
        * A tuple of two points ``([x1, y1, 0], [x2, y2, 0])`` for two
          intersections.
        * A single point ``[x, y, 0]`` for one intersection.
        * ``None`` if there is no intersection.

    Examples
    --------
    .. code-block:: python

        from manim_extensions import LineArcInt

        line = Line(LEFT, RIGHT)
        arc = Arc(start_angle=0, angle=np.pi, radius=1)
        result = LineArcInt(line, arc)
    """
    # 获取线段起点和终点（仅x,y坐标）
    p1 = line.start[:2]
    p2 = line.end[:2]

    # 处理线段退化为点的情况
    direction = p2 - p1
    length = np.linalg.norm(direction)
    if length < 1e-8:
        return None

    # 获取圆弧参数（关键修正：使用ManimCE的正确属性）
    center = arc.arc_center[:2]  # 圆弧中心（x,y）
    radius = arc.radius  # 半径
    start_angle = arc.start_angle  # 起始角度（弧度）
    angle = arc.angle  # 角度跨度（弧度，正=逆时针，负=顺时针）

    # 线段参数方程转换（以圆弧中心为原点）
    p1_centered = p1 - center
    p2_centered = p2 - center
    dx = p2_centered[0] - p1_centered[0]
    dy = p2_centered[1] - p1_centered[1]

    # 联立线段与圆的方程（二次方程）
    a = dx**2 + dy**2
    b = 2 * (p1_centered[0] * dx + p1_centered[1] * dy)
    c = p1_centered[0] ** 2 + p1_centered[1] ** 2 - radius**2
    discriminant = b**2 - 4 * a * c

    # 无实根（直线与圆无交点）
    if discriminant < 0:
        return None

    # 计算t值（线段参数）
    sqrt_d = np.sqrt(discriminant)
    t1 = (-b + sqrt_d) / (2 * a)
    t2 = (-b - sqrt_d) / (2 * a)
    t_values = []
    for t in [t1, t2]:
        if 0 <= t <= 1 and (len(t_values) == 0 or abs(t - t_values[0]) > 1e-8):
            t_values.append(t)

    # 检查交点是否在圆弧范围内（关键修正：角度判断+容差）
    intersections = []
    TOLERANCE = 1e-6  # 角度容差（弧度）
    for t in t_values:
        # 计算交点相对圆弧中心的坐标
        x = p1_centered[0] + t * dx
        y = p1_centered[1] + t * dy
        theta = np.arctan2(y, x) % (2 * np.pi)  # 交点角度（0~2π弧度）

        # 圆弧的角度范围（模2π处理）
        start_angle_mod = start_angle % (2 * np.pi)
        end_angle_mod = (start_angle + angle) % (2 * np.pi)

        # 判断角度是否在圆弧范围内（带容差）
        if angle > 0:  # 逆时针圆弧
            if start_angle_mod < end_angle_mod:
                valid = (
                    start_angle_mod - TOLERANCE
                    <= theta
                    <= end_angle_mod + TOLERANCE
                )
            else:
                valid = (theta >= start_angle_mod - TOLERANCE) or (
                    theta <= end_angle_mod + TOLERANCE
                )
        else:  # 顺时针圆弧
            if end_angle_mod < start_angle_mod:
                valid = (
                    end_angle_mod - TOLERANCE
                    <= theta
                    <= start_angle_mod + TOLERANCE
                )
            else:
                valid = (theta <= start_angle_mod + TOLERANCE) or (
                    theta >= end_angle_mod - TOLERANCE
                )

        if valid:
            # 转换为绝对坐标（添加z=0）
            intersection = [x + center[0], y + center[1], 0.0]
            intersections.append(intersection)
    try:
        return intersections[0], intersections[1]
    except Exception:
        try:
            return intersections[0]
        except Exception:
            return None


def TangentPoint(
    p1: Union[np.ndarray, tuple, list],
    p2: Union[np.ndarray, tuple, list],
    line_start: Union[np.ndarray, tuple, list],
    line_end: Union[np.ndarray, tuple, list],
) -> Optional[np.ndarray]:
    """Compute the tangent point of a circle through two points and a line.

    Given two points *p1* and *p2* that lie on a circle, and a line segment
    defined by *line_start* and *line_end*, this function finds the point
    on the line segment where the circle is tangent to the line.

    Parameters
    ----------
    p1 : Union[numpy.ndarray, tuple, list]
        First point on the circle, as ``(x, y)`` or ``(x, y, z)``.
    p2 : Union[numpy.ndarray, tuple, list]
        Second point on the circle, as ``(x, y)`` or ``(x, y, z)``.
    line_start : Union[numpy.ndarray, tuple, list]
        Start point of the line segment, as ``(x, y)`` or ``(x, y, z)``.
    line_end : Union[numpy.ndarray, tuple, list]
        End point of the line segment, as ``(x, y)`` or ``(x, y, z)``.

    Returns
    -------
    Optional[numpy.ndarray]
        The tangent point ``(x, y, 0)`` as a :class:`numpy.ndarray`, or
        ``None`` if no valid tangent point exists.

    Examples
    --------
    .. code-block:: python

        from manim_extensions import TangentPoint

        p = TangentPoint(
            [1, 0, 0], [-1, 0, 0],
            line_start=[0, -2, 0], line_end=[0, 2, 0]
        )
    """

    def to_3d(point: Union[np.ndarray, tuple, list]) -> np.ndarray:
        if len(point) == 2:
            return np.array([point[0], point[1], 0.0])
        return np.array(point[:3])

    p1 = to_3d(p1)
    p2 = to_3d(p2)
    line_start = to_3d(line_start)
    line_end = to_3d(line_end)

    # 计算线段方向向量
    line_direction = line_end - line_start
    line_length = np.linalg.norm(line_direction)

    # 处理线段退化为点的情况
    if line_length < 1e-8:
        # 检查线段端点是否在圆上
        dist_p1 = np.linalg.norm(line_start - p1)
        dist_p2 = np.linalg.norm(line_start - p2)
        if abs(dist_p1 - dist_p2) < 1e-8:
            return line_start
        return None

    line_direction = line_direction / line_length

    # 计算线段p1-p2的中点
    midpoint = (p1 + p2) / 2

    # 计算线段p1-p2的方向向量
    p1p2_direction = p2 - p1
    p1p2_length = np.linalg.norm(p1p2_direction)

    if p1p2_length < 1e-8:
        # p1和p2重合，无法确定唯一的圆
        return None

    p1p2_direction = p1p2_direction / p1p2_length

    # 计算线段p1-p2的垂直向量（在二维平面上）
    perpendicular_dir = np.array([-p1p2_direction[1], p1p2_direction[0], 0.0])

    # 构建线性方程组求解圆心c = midpoint + t * perpendicular_dir
    cross_perp_line = np.cross(perpendicular_dir, line_direction)
    cross_mid_line = np.cross(midpoint - line_start, line_direction)

    a = np.dot(perpendicular_dir, perpendicular_dir) - np.dot(
        cross_perp_line, cross_perp_line
    )
    b = 2 * (
        np.dot(midpoint - p1, perpendicular_dir)
        - np.dot(cross_mid_line, cross_perp_line)
    )
    c = np.dot(midpoint - p1, midpoint - p1) - np.dot(
        cross_mid_line, cross_mid_line
    )

    # 处理a接近零的特殊情况（退化为一次方程）
    if abs(a) < 1e-8:
        if abs(b) < 1e-8:
            return None  # 无解或无穷多解
        t = -c / b
        centers = [midpoint + t * perpendicular_dir]
    else:
        # 计算判别式
        discriminant = b**2 - 4 * a * c

        if discriminant < 0:
            # 无实数解
            return None

        # 求解t
        sqrt_d = np.sqrt(discriminant)
        t1 = (-b + sqrt_d) / (2 * a)
        t2 = (-b - sqrt_d) / (2 * a)

        # 计算可能的圆心
        centers = [midpoint + t * perpendicular_dir for t in [t1, t2]]

    # 计算对应的切点（在直线上）
    valid_tangents = []
    for center in centers:
        # 计算从line_start到center的向量在直线方向上的投影
        projection = np.dot(center - line_start, line_direction)

        # 检查投影是否在线段范围内 [0, line_length]
        if 0 <= projection <= line_length:
            # 计算切点
            tangent_point = line_start + projection * line_direction

            # 验证切点到圆心的距离是否等于圆心到p1的距离
            radius = np.linalg.norm(center - p1)
            dist_to_tangent = np.linalg.norm(center - tangent_point)

            if abs(radius - dist_to_tangent) < 1e-6:
                valid_tangents.append(tangent_point)

    # 选择距离p1和p2较近的解
    if not valid_tangents:
        return None

    # 如果有多个解，选择第一个
    return valid_tangents[0]
