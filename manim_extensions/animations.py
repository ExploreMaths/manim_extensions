from manim import *
import numpy as np


def VisDrawArc(
    scene: Scene,
    arc: Arc,
    axis: np.ndarray = OUT,
    run_time: float = 1,
) -> None:
    """可视化绘制圆弧的动画。

    在场景中播放绘制圆弧的动画，同时显示一个沿圆弧移动的点及半径虚线。

    Args:
        scene: Manim 场景对象。
        arc: 要绘制的圆弧。
        axis: 旋转轴方向，``OUT`` 为逆时针，``IN`` 为顺时针。默认为 ``OUT``。
        run_time: 动画持续时间（秒）。默认为 1。
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
    """打字机效果动画。

    逐个字符显示 ``Text`` 对象的内容，模拟打字机输入效果。
    默认自动根据字符数量与间隔计算动画总时长。

    Args:
        mobject: 要动画显示的 ``Text`` 对象。
        interval: 字符间显示间隔（秒）。默认为 2。
        **kwargs: 传递给 ``Animation`` 的其他关键字参数。
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
