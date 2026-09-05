# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Space scene for Pymunk physics.

This module provides the SpaceScene class for creating physics simulations with Pymunk.

"""
from manim import *
from ..constraints.constraint import VConstraint
import pymunk
from typing import Any, Callable, Dict, Tuple

from . import VSpace

from ..utils.logger_tool import manim_pymunk_logger


class SpaceScene(ZoomedScene):
    """A scene that hosts and manages a Pymunk physics simulation.

    When the actual relative angle deviates from the target angle,
    the spring torque pulls it back; the damping torque dampens the oscillation.

    Parameters
    ----------
    gravity
        The gravity acceleration vector $(g_x, g_y)$ applied to the physical
        space. Defaults to $(0, -9.81)$.
    **kwargs
        Forwarded to the parent :class:`~manim.scene.zoomed_scene.ZoomedScene`.

    Examples
    --------
    .. manim:: SpaceSceneExample

        from manim import *
        from manim_extensions.pymunk import *

        class SpaceSceneExample(SpaceScene):
            def construct(self):
                # a floor and three balls driven by the Pymunk physics space
                floor = Line(LEFT * 6, RIGHT * 6, stroke_width=8, color=GREY)
                floor.to_edge(DOWN, buff=0.5)
                balls = VGroup(*[
                    Circle(radius=0.3, color=BLUE, fill_opacity=0.8).move_to(
                        UP * 3 + (i - 1) * RIGHT
                    )
                    for i in range(3)
                ])

                self.play(FadeIn(floor), FadeIn(balls))
                self.add_static_body(floor)
                self.add_dynamic_body(*balls)
                self.add_shapes_filter(*balls, group=1)
                self.apply_impulse_at_world_point(
                    balls[0], impulse=(4, 2, 0), point=tuple(balls[0].get_center())
                )
                self.wait(5)
    """

    def __init__(self, gravity: Tuple[float, float] = (0, -9.81), **kwargs):
        super().__init__(**kwargs)
        self.vspace = VSpace(gravity=gravity)
        manim_pymunk_logger.debug("SpaceScene initional~")

    def setup(self):
        """Instance initialization configuration.
        Automatically add physical space to the scene and start the physics state updater.
        """
        self.add(self.vspace)
        self.vspace.init_updater()

    def add_shapes_filter(
        self,
        *mobs,
        group: int = 0,
        categories: int = 4294967295,
        mask: int = 4294967295,
    ):
        """Sets the collision filter for the shapes associated with the given Mobjects.
        This determines which shapes can collide with each other based on groups,
        categories, and masks.

        Parameters
        ----------
        mobs
            The Mobjects whose physical shapes will have the filter applied.
        group
            A group ID. Shapes in the same non-zero group do not collide.
            Useful for creating multi-part objects where internal parts ignore each other.
        categories
            A bitmask of the categories this shape belongs to. Default is all categories (0xFFFFFFFF).
        mask
            A bitmask of the categories this shape can collide with. Default is all categories (0xFFFFFFFF).
        """
        for mob in mobs:
            self.vspace._add_shape_filter(mob, group, categories, mask)

    def add_static_body(
        self,
        *mobs,
        family_members=False,
        is_solid=True,
        # shapes 相关
        elasticity: float = 0.8,
        friction: float = 0.8,
        density: float = 1.0,
        sensor: bool = False,
        surface_velocity: Tuple[float, float] = (0.0, 0.0),
        # body 相关
        center_of_gravity: Tuple[float, float] = (0.0, 0.0),
        velocity: Tuple[float, float] = (0.0, 0.0),
        angular_velocity: float = 0.0,
    ):
        """Adds Mobjects to the physical space as static bodies.
        Static bodies do not move under the influence of gravity or collisions
        and are typically used for environment boundaries like floors and walls.

        Parameters
        ----------
        mobs
            The Mobjects to be treated as static physical objects.
        family_members
            If True, all sub-mobjects (children) will also be added to the physical space.
        is_solid
            Determines if the body is solid. If False, it might be treated as a hollow
            boundary or wireframe depending on the implementation.
        elasticity
            The elasticity (restitution) of the shape. A value of 0.0 means no bounce,
            while 1.0 represents a perfectly elastic collision.
        friction
            The friction coefficient. Determines how much the object resists
            sliding along surfaces.
        density
            The density of the object. For static bodies, this is primarily used
            to calculate mass if the body is ever converted to dynamic.
        sensor
            If True, the shape will detect collisions but will not produce a
            physical collision response (objects will pass through it).
        surface_velocity
            The surface velocity of the shape. Useful for creating conveyor
            belt effects.
        center_of_gravity
            The center of gravity relative to the Mobject's center.
        velocity
            The initial linear velocity of the body. Though static, this can
            affect how objects bounce off it.
        angular_velocity
            The initial angular velocity of the body.
        """
        self.add(*mobs)
        for mob in mobs:
            targets = mob.family_members_with_points() if family_members else [mob]
            for target in targets:
                # 显式传递每一个变量
                self.vspace.set_body_and_shapes(
                    target,
                    body_type=pymunk.Body.STATIC,
                    is_solid=is_solid,
                    # shapes 映射
                    elasticity=elasticity,
                    friction=friction,
                    density=density,
                    sensor=sensor,
                    surface_velocity=surface_velocity,
                    # body 映射
                    center_of_gravity=center_of_gravity,
                    velocity=velocity,
                    angular_velocity=angular_velocity,
                )

    def add_dynamic_body(
        self,
        *mobs,
        family_members=False,
        is_solid=True,
        # shapes 相关
        elasticity: float = 0.8,
        friction: float = 0.8,
        density: float = 1.0,
        sensor: bool = False,
        surface_velocity: Tuple[float, float] = (0.0, 0.0),
        # body 相关
        center_of_gravity: Tuple[float, float] = (0.0, 0.0),
        velocity: Tuple[float, float] = (0.0, 0.0),
        angular_velocity: float = 0.0,
    ):
        """Adds Mobjects to the physical space as static bodies.
        Static bodies do not move under the influence of gravity or collisions
        and are typically used for environment boundaries like floors and walls.

        Parameters
        ----------
        mobs
            The Mobjects to be treated as static physical objects.
        family_members
            If True, all sub-mobjects (children) will also be added to the physical space.
        is_solid
            Determines if the body is solid. If False, it might be treated as a hollow
            boundary or wireframe depending on the implementation.
        elasticity
            The elasticity (restitution) of the shape. A value of 0.0 means no bounce,
            while 1.0 represents a perfectly elastic collision.
        friction
            The friction coefficient. Determines how much the object resists
            sliding along surfaces.
        density
            The density of the object. For static bodies, this is primarily used
            to calculate mass if the body is ever converted to dynamic.
        sensor
            If True, the shape will detect collisions but will not produce a
            physical collision response (objects will pass through it).
        surface_velocity
            The surface velocity of the shape. Useful for creating conveyor
            belt effects.
        center_of_gravity
            The center of gravity relative to the Mobject's center.
        velocity
            The initial linear velocity of the body. Though static, this can
            affect how objects bounce off it.
        angular_velocity
            The initial angular velocity of the body.
        """
        self.add(*mobs)
        for mob in mobs:
            targets = mob.family_members_with_points() if family_members else [mob]
            for target in targets:
                # 显式传递每一个变量
                self.vspace.set_body_and_shapes(
                    target,
                    body_type=pymunk.Body.DYNAMIC,
                    is_solid=is_solid,
                    # shapes 映射
                    elasticity=elasticity,
                    friction=friction,
                    density=density,
                    sensor=sensor,
                    surface_velocity=surface_velocity,
                    # body 映射
                    center_of_gravity=center_of_gravity,
                    velocity=velocity,
                    angular_velocity=angular_velocity,
                )

    def add_kinematic_body(
        self,
        *mobs,
        family_members=False,
        is_solid=True,
        # shapes 相关
        elasticity: float = 0.8,
        friction: float = 0.8,
        density: float = 1.0,
        sensor: bool = False,
        surface_velocity: Tuple[float, float] = (0.0, 0.0),
        # body 相关
        center_of_gravity: Tuple[float, float] = (0.0, 0.0),
        velocity: Tuple[float, float] = (0.0, 0.0),
        angular_velocity: float = 0.0,
    ):
        """Adds Mobjects to the physical space as static bodies.
        Static bodies do not move under the influence of gravity or collisions
        and are typically used for environment boundaries like floors and walls.

        Parameters
        ----------
        mobs
            The Mobjects to be treated as static physical objects.
        family_members
            If True, all sub-mobjects (children) will also be added to the physical space.
        is_solid
            Determines if the body is solid. If False, it might be treated as a hollow
            boundary or wireframe depending on the implementation.
        elasticity
            The elasticity (restitution) of the shape. A value of 0.0 means no bounce,
            while 1.0 represents a perfectly elastic collision.
        friction
            The friction coefficient. Determines how much the object resists
            sliding along surfaces.
        density
            The density of the object. For static bodies, this is primarily used
            to calculate mass if the body is ever converted to dynamic.
        sensor
            If True, the shape will detect collisions but will not produce a
            physical collision response (objects will pass through it).
        surface_velocity
            The surface velocity of the shape. Useful for creating conveyor
            belt effects.
        center_of_gravity
            The center of gravity relative to the Mobject's center.
        velocity
            The initial linear velocity of the body. Though static, this can
            affect how objects bounce off it.
        angular_velocity
            The initial angular velocity of the body.
        """
        self.add(*mobs)
        for mob in mobs:
            targets = mob.family_members_with_points() if family_members else [mob]
            for target in targets:
                # 显式传递每一个变量
                self.vspace.set_body_and_shapes(
                    target,
                    body_type=pymunk.Body.KINEMATIC,
                    is_solid=is_solid,
                    # shapes 映射
                    elasticity=elasticity,
                    friction=friction,
                    density=density,
                    sensor=sensor,
                    surface_velocity=surface_velocity,
                    # body 映射
                    center_of_gravity=center_of_gravity,
                    velocity=velocity,
                    angular_velocity=angular_velocity,
                )

    def add_constraints(self, *mobs: VConstraint):
        """Adds constraint Mobjects to the scene and installs them into the physical space.
        This method ensures that the constraints (such as springs, joints, or motors)
        are both visually rendered in Manim and physically simulated in Pymunk.

        Parameters
        ----------
        mobs
            The VConstraint objects to be added. Each must implement an `install`
            method to link with the physical space.
        """
        self.add(*mobs)
        for mob in mobs:
            mob.install(space=self.vspace.space)

    def active_body(self, *mobs: Mobject) -> None:
        """Activates the physical bodies of the given Mobjects if they are sleeping.
        In physics simulations, bodies that have come to rest are often put to 'sleep'
        to save computation. This method forces those bodies back into an active state.

        Parameters
        ----------
        mobs
            The Mobjects whose associated physical bodies should be activated.
            This includes all sub-mobjects within the family tree of each provided Mobject.
        """
        for mob in mobs:
            family = mob.family_members_with_points()
            for sub_mob in family:
                if (
                    hasattr(sub_mob, "body")
                    and sub_mob.body.body_type is pymunk.Body.DYNAMIC
                    and sub_mob.body.is_sleeping
                ):
                    sub_mob.body.activate()

    def sleep_body(self, *mobs: Mobject) -> None:
        """Forces the physical bodies of the given Mobjects into a sleeping state.
        Sleeping bodies are removed from the physics simulation update loop until
        they are touched by another active body or manually activated, which
        helps reduce CPU usage.

        Parameters
        ----------
        mobs
            The Mobjects whose associated physical bodies should be put to sleep.
            This iterates through all sub-mobjects within the family tree of
            each provided Mobject.
        """
        for mob in mobs:
            # 解决组的问题
            family = mob.family_members_with_points()
            for sub_mob in family:
                if (
                    hasattr(sub_mob, "body")
                    and sub_mob.body.body_type is pymunk.Body.DYNAMIC
                ):
                    sub_mob.body.sleep()

    def draw_debug_img(self, option: int = None, xlim=(-8, 8), ylim=(-5, 5)) -> None:
        """Pops up a Matplotlib window to render a debug view of the physical space.
        This is an essential diagnostic tool used to verify if collision shapes,
        constraints, and pivots are correctly aligned when they are not behaving
        as expected in the Manim render.

        .. note::
            This method will block the execution of the program until the
            pop-up window is manually closed.

        Parameters
        ----------
        option
            Pymunk debug draw options (e.g., `pymunk.SpaceDebugDrawOptions`).
            Determines what physical elements (shapes, constraints, collision points) are visible.
        xlim
            The display range for the X-axis in the plot.
        ylim
            The display range for the Y-axis in the plot.
        """
        import matplotlib.pyplot as plt
        import pymunk.matplotlib_util
        import matplotlib

        matplotlib.use("TkAgg")

        _, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal")

        draw_options = pymunk.matplotlib_util.DrawOptions(ax)
        if option is not None:
            draw_options.flags = option
        else:
            draw_options.flags = (
                pymunk.SpaceDebugDrawOptions.DRAW_SHAPES
                | pymunk.SpaceDebugDrawOptions.DRAW_COLLISION_POINTS
                # | pymunk.SpaceDebugDrawOptions.DRAW_CONSTRAINTS
            )

        self.vspace.space.debug_draw(draw_options)

        # block=True 会阻塞程序直到你手动关闭窗口
        plt.show(block=True)

    @staticmethod
    def get_body(mob: Mobject) -> pymunk.Body | None:
        """Extracts the bound Pymunk Body object from a Manim Mobject.

        This method retrieves the physical body associated with the Mobject,
        allowing for direct manipulation of physical properties like mass or velocity.

        Parameters
        ----------
        mob
            The target Mobject to extract the body from.

        Returns
        -------
        pymunk.Body | None
            The bound physical body.

        Raises
        ------
        RuntimeError
            If the Mobject has not been added to the physical space yet.
        """
        if hasattr(mob, "body"):
            return mob.body
        else:
            raise RuntimeError("Please add 'mobject' to the space first!")

    @staticmethod
    def get_shapes(mob: Mobject) -> list[pymunk.Shape] | None:
        """Retrieves the list of Pymunk Shape objects associated with a Mobject.

        Shapes define the collision boundaries of a body. One Mobject may consist
        of multiple physical shapes.

        Parameters
        ----------
        mob
            The Mobject whose physical shapes are to be retrieved.

        Returns
        -------
        list[pymunk.Shape] | None
            A list of Pymunk shapes defining the collision boundaries.

        Raises
        ------
        RuntimeError
            If the Mobject has not been added to the physical space yet.
        """
        if hasattr(mob, "shapes"):
            return mob.shapes
        else:
            raise RuntimeError("Please add 'mobject' to the space first!")

    # collision ID setter
    def set_collision_type(self, *mobs: Mobject, collision_type: int = 4):
        for mob in mobs:
            self.vspace._set_collision_type(mob, collision_type)

    # collision detection handlser setter
    def set_wildcard_collision_handler(
        self,
        collision_type_a: int,
        begin: Callable[[pymunk.Arbiter, pymunk.Space, Dict], bool] = None,
        pre_solve: Callable[[pymunk.Arbiter, pymunk.Space, Dict], bool] = None,
        post_solve: Callable[[pymunk.Arbiter, pymunk.Space, Dict], None] = None,
        separate: Callable[[pymunk.Arbiter, pymunk.Space, Dict], None] = None,
        data: Dict[Any, Any] = None,
    ):
        self.vspace._wildcard_collision_handler(
            collision_type_a, begin, pre_solve, post_solve, separate, data
        )

    def set_collision_detection_handler(
        self,
        collision_type_a: int,
        collision_type_b: int,
        begin: Callable[[pymunk.Arbiter, pymunk.Space, Dict], bool] = None,
        pre_solve: Callable[[pymunk.Arbiter, pymunk.Space, Dict], bool] = None,
        post_solve: Callable[[pymunk.Arbiter, pymunk.Space, Dict], None] = None,
        separate: Callable[[pymunk.Arbiter, pymunk.Space, Dict], None] = None,
        data: Dict[Any, Any] = None,
    ):
        self.vspace._collision_detection_handler(
            collision_type_a,
            collision_type_b,
            begin,
            pre_solve,
            post_solve,
            separate,
            data,
        )

    # force setter
    def apply_force_at_local_point(
        self,
        *mobs: Mobject,
        force: Tuple[float, float, float],
        point: Tuple[float, float, float] = (0, 0, 0),
    ):
        for mob in mobs:
            self.vspace.apply_force_at_local_point(mob, force, point)

    def apply_force_at_world_point(
        self,
        *mobs: Mobject,
        force: Tuple[float, float, float],
        point: Tuple[float, float, float] = (0, 0, 0),
    ):
        for mob in mobs:
            self.vspace.apply_force_at_world_point(mob, force, point)

    # impulse setter
    def apply_impulse_at_local_point(
        self,
        *mobs: Mobject,
        impulse: Tuple[float, float, float],
        point: Tuple[float, float, float] = (0, 0, 0),
    ) -> None:
        for mob in mobs:
            self.vspace.apply_impulse_at_local_point(mob, impulse, point)

    def apply_impulse_at_world_point(
        self,
        *mobs: Mobject,
        impulse: Tuple[float, float, float],
        point: Tuple[float, float, float] = (0, 0, 0),
    ) -> None:
        for mob in mobs:
            self.vspace.apply_impulse_at_world_point(mob, impulse, point)

    # pos utils
    def local_to_world(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    ):
        self.vspace.local_to_world(mob, point)

    def world_to_local(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    ):
        self.vspace.world_to_local(mob, point)

    # custom positon | velocity
    def set_position_func(
        self, *mobs: Mobject, callback: Callable[[pymunk.Body, float], None] = None
    ):
        for mob in mobs:
            self.vspace.set_position_func(mob, callback)

    def set_velocity_func(
        self,
        *mobs: Mobject,
        callback: Callable[
            [pymunk.Body, tuple[float, float], float, float], None
        ] = None,
    ):
        for mob in mobs:
            self.vspace.set_velocity_func(mob, callback)

    # get velocity info
    def get_velocity_at_local_point(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    )-> Tuple[float, float, float]:
        return self.vspace.velocity_at_local_point(mob, point)

    def velocity_at_world_point(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    )-> Tuple[float, float, float]:
        return self.vspace.velocity_at_world_point(mob, point)

    # get point info
    def get_point_query_info(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    ) -> list:
        return self.vspace.get_point_query_info(
            mob,
            point,
        )

    def get_line_query(
        self,
        mob: Mobject,
        start: Tuple[float, float, float],
        end: Tuple[float, float, float],
        stroke_width: float,
    ) -> list:
        return self.vspace.get_line_query(mob, start, end, stroke_width)

    def get_shapea_shapeb_info(
        self, shape_a: pymunk.Shape, shape_b: pymunk.Shape
    ) -> list:
        return self.vspace.get_shapea_shapeb_info(
            shape_a,
            shape_b,
        )