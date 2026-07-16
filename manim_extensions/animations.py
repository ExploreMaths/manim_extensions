from manim import *
import numpy as np


def VisDrawArc(
    scene: Scene,
    arc: Arc,
    axis: np.ndarray = OUT,
    run_time: float = 1,
) -> None:
    """Visualised arc-drawing animation.

    Plays an animation in *scene* that draws *arc* while simultaneously
    showing a moving dot travelling along the arc and a dashed radius line.

    .. note::

        This is a **convenience function** — call it directly; there is no
        need to wrap it in ``self.play()``.

    Parameters
    ----------
    scene : :class:`manim.scene.scene.Scene`
        The Manim scene in which the animation is played.
    arc : :class:`manim.Arc`
        The arc to draw.
    axis : numpy.ndarray, optional
        Rotation axis. ``OUT`` gives counter‑clockwise motion, ``IN`` gives
        clockwise motion. Defaults to ``OUT``.
    run_time : float, optional
        Duration of the animation in seconds. Defaults to ``1``.

    Examples
    --------
    .. code-block:: python

        from manim_extensions import VisDrawArc

        class MyScene(Scene):
            def construct(self):
                arc = Arc(start_angle=0, angle=PI, radius=2)
                VisDrawArc(self, arc, axis=OUT, run_time=2)
    """
    # 获取弧线的起点、终点和圆心
    start_point = arc.point_from_proportion(0)
    end_point = arc.point_from_proportion(1)
    center = arc.get_arc_center()

    # 根据轴方向确定旋转的起始点和方向
    if np.array_equal(axis, OUT):  # 逆时针
        draw_arc = arc  # 使用原始弧线
        rotation_start = start_point
        total_angle = arc.get_angle()
    else:  # 顺时针 (axis=IN)
        # 创建一个与原弧线方向相反的新弧线
        draw_arc = Arc(
            start_angle=angle_of_vector(end_point - center),
            angle=-arc.get_angle(),  # 负角度表示相反方向
            radius=np.linalg.norm(end_point - center),
            arc_center=center,
            color=arc.get_color(),
            stroke_width=arc.get_stroke_width(),
        )
        rotation_start = end_point
        total_angle = -arc.get_angle()

    # 创建移动点的标记
    moving_dot = Dot(point=rotation_start)

    # 创建从圆心到移动点的虚线
    radius_line = DashedLine(center, rotation_start)

    # 计算实际弧线的半径和起始角度
    r = np.linalg.norm(rotation_start - center)
    start_angle = angle_of_vector(rotation_start - center)

    # 创建一个跟踪旋转进度的变量
    progress = ValueTracker(0)

    # 更新移动点的位置
    moving_dot.add_updater(
        lambda d: d.move_to(
            center
            + r
            * np.array(
                [
                    np.cos(start_angle + progress.get_value() * total_angle),
                    np.sin(start_angle + progress.get_value() * total_angle),
                    0,
                ]
            )
        )
    )

    # 更新半径线
    radius_line.add_updater(
        lambda l: l.become(DashedLine(center, moving_dot.get_center()))
    )

    # 添加所有元素到场景
    scene.add(moving_dot, radius_line)

    # 同步执行弧线绘制和点的旋转动画（1秒持续时间）
    scene.play(
        Create(draw_arc, rate_func=linear),  # 使用调整后的弧线
        progress.animate.set_value(1),
        run_time=run_time,
        rate_func=linear,
    )

    # 清除更新器
    moving_dot.clear_updaters()
    radius_line.clear_updaters()

    # 移除临时元素
    scene.remove(moving_dot, radius_line)


class TypeWriter(Animation):
    """Typewriter effect animation.

    Reveals the content of a :class:`manim.Text` object character by
    character, simulating a typewriter.  The total run time is automatically
    calculated from the character count and *interval* unless an explicit
    ``run_time`` is passed in ``kwargs``.

    .. inheritance-diagram:: manim_extensions.animations.TypeWriter
       :parts: 1

    Parameters
    ----------
    mobject : :class:`manim.Text`
        The ``Text`` object to animate.
    interval : float, optional
        Display interval between consecutive characters in seconds.
        Defaults to ``2``.
    **kwargs
        Additional keyword arguments forwarded to :class:`manim.Animation`.

    Attributes
    ----------
    interval : float
        The stored interval between characters.
    char_count : int
        Number of characters in *mobject*.

    Examples
    --------
    .. code-block:: python

        from manim_extensions import TypeWriter

        class MyScene(Scene):
            def construct(self):
                text = Text("Hello World")
                self.play(TypeWriter(text, interval=0.1))
    """

    def __init__(self, mobject: Text, interval: float = 2, **kwargs) -> None:
        assert isinstance(mobject, Text), "TypeWriter only supports Text mobjects."
        self.interval = interval
        self.char_count = len(mobject.submobjects)

        # 自动计算run_time
        if "run_time" not in kwargs:
            kwargs["run_time"] = self.char_count * self.interval

        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> Text:
        current_index = int(alpha * self.char_count)
        for i, char in enumerate(self.mobject.submobjects):
            char.set_opacity(1 if i < current_index else 0)
        return self.mobject
