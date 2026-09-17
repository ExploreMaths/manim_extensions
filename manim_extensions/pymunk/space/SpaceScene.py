# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
"""Space scene for Pymunk physics.

This module provides the SpaceScene class for creating physics simulations with Pymunk.

"""
from __future__ import annotations

from manim import Mobject, ZoomedScene
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING, Tuple

from . import VSpace
from ..constraints.constraint import VConstraint
from ..utils.logger_tool import manim_pymunk_logger

from ...utils.deps import require

if TYPE_CHECKING:
    import pymunk


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
        """Initialize the SpaceScene with a VSpace physics simulation
        using the specified gravity vector.
        """
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
        family_members: bool = False,
        is_solid: bool = True,
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
        pymunk = require("physics", "pymunk")
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
        family_members: bool = False,
        is_solid: bool = True,
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
        pymunk = require("physics", "pymunk")
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
        family_members: bool = False,
        is_solid: bool = True,
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
        pymunk = require("physics", "pymunk")
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
        pymunk = require("physics", "pymunk")
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
        pymunk = require("physics", "pymunk")
        for mob in mobs:
            # 解决组的问题
            family = mob.family_members_with_points()
            for sub_mob in family:
                if (
                    hasattr(sub_mob, "body")
                    and sub_mob.body.body_type is pymunk.Body.DYNAMIC
                ):
                    sub_mob.body.sleep()

    def draw_debug_img(self, option: Optional[int] = None, xlim: tuple = (-8, 8), ylim: tuple = (-5, 5)) -> None:
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
        pymunk = require("physics", "pymunk")

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
        """Set the collision type integer on the physical shapes of the
        given Mobjects, used by collision handlers to match pairs.

        Parameters
        ----------
        mobs
            The Mobjects whose shapes will have their collision type set.
        collision_type
            Integer identifier for the collision category (default 4).
        """
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
        data: Optional[Dict[Any, Any]] = None,
    ):
        """Register a wildcard collision handler that matches any collision
        involving the given collision type.

        Parameters
        ----------
        collision_type_a
            The collision type to match against all other types.
        begin
            Callback called when two shapes first start touching.
        pre_solve
            Callback called before collision forces are calculated.
        post_solve
            Callback called after collision forces are applied.
        separate
            Callback called when two shapes stop touching.
        data
            Optional user data dictionary passed to the callbacks.
        """
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
        data: Optional[Dict[Any, Any]] = None,
    ):
        """Register a collision handler between two specific collision types.

        Parameters
        ----------
        collision_type_a
            The first collision type identifier.
        collision_type_b
            The second collision type identifier.
        begin
            Callback called when two shapes first start touching.
        pre_solve
            Callback called before collision forces are calculated.
        post_solve
            Callback called after collision forces are applied.
        separate
            Callback called when two shapes stop touching.
        data
            Optional user data dictionary passed to the callbacks.
        """
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
        """Apply a continuous force to each given Mobject at a local point
        relative to the body's center.

        Parameters
        ----------
        mobs
            The Mobjects whose physical bodies will receive the force.
        force
            The force vector (fx, fy, fz) to apply.
        point
            The local point on the body where the force is applied.
            Defaults to the center (0, 0, 0).
        """
        for mob in mobs:
            self.vspace.apply_force_at_local_point(mob, force, point)

    def apply_force_at_world_point(
        self,
        *mobs: Mobject,
        force: Tuple[float, float, float],
        point: Tuple[float, float, float] = (0, 0, 0),
    ):
        """Apply a continuous force to each given Mobject at a point in
        world (scene) coordinates.

        Parameters
        ----------
        mobs
            The Mobjects whose physical bodies will receive the force.
        force
            The force vector (fx, fy, fz) to apply.
        point
            The world-space point where the force is applied.
            Defaults to (0, 0, 0).
        """
        for mob in mobs:
            self.vspace.apply_force_at_world_point(mob, force, point)

    # impulse setter
    def apply_impulse_at_local_point(
        self,
        *mobs: Mobject,
        impulse: Tuple[float, float, float],
        point: Tuple[float, float, float] = (0, 0, 0),
    ) -> None:
        """Apply an instantaneous impulse to each given Mobject at a local
        point relative to the body's center.

        Parameters
        ----------
        mobs
            The Mobjects whose physical bodies will receive the impulse.
        impulse
            The impulse vector (ix, iy, iz) to apply.
        point
            The local point on the body where the impulse is applied.
            Defaults to the center (0, 0, 0).
        """
        for mob in mobs:
            self.vspace.apply_impulse_at_local_point(mob, impulse, point)

    def apply_impulse_at_world_point(
        self,
        *mobs: Mobject,
        impulse: Tuple[float, float, float],
        point: Tuple[float, float, float] = (0, 0, 0),
    ) -> None:
        """Apply an instantaneous impulse to each given Mobject at a point
        in world (scene) coordinates.

        Parameters
        ----------
        mobs
            The Mobjects whose physical bodies will receive the impulse.
        impulse
            The impulse vector (ix, iy, iz) to apply.
        point
            The world-space point where the impulse is applied.
            Defaults to (0, 0, 0).
        """
        for mob in mobs:
            self.vspace.apply_impulse_at_world_point(mob, impulse, point)

    # pos utils
    def local_to_world(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    ):
        """Convert a point from the Mobject's local body coordinates to
        world (scene) coordinates.

        Parameters
        ----------
        mob
            The Mobject whose body's coordinate system is used.
        point
            The local point (x, y, z) to convert. Defaults to (0, 0, 0).
        """
        self.vspace.local_to_world(mob, point)

    def world_to_local(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    ):
        """Convert a point from world (scene) coordinates to the Mobject's
        local body coordinates.

        Parameters
        ----------
        mob
            The Mobject whose body's coordinate system is used.
        point
            The world point (x, y, z) to convert. Defaults to (0, 0, 0).
        """
        self.vspace.world_to_local(mob, point)

    # custom positon | velocity
    def set_position_func(
        self, *mobs: Mobject, callback: Callable[[pymunk.Body, float], None] = None
    ):
        """Assign a custom position update callback to each Mobject's
        physical body, overriding Pymunk's default position integration.

        Parameters
        ----------
        mobs
            The Mobjects whose bodies will use the custom position function.
        callback
            A function with signature ``(body, dt)``. If ``None``, the
            default Pymunk position update is restored.
        """
        for mob in mobs:
            self.vspace.set_position_func(mob, callback)

    def set_velocity_func(
        self,
        *mobs: Mobject,
        callback: Callable[
            [pymunk.Body, tuple[float, float], float, float], None
        ] = None,
    ):
        """Assign a custom velocity update callback to each Mobject's
        physical body, overriding Pymunk's default velocity integration.

        Parameters
        ----------
        mobs
            The Mobjects whose bodies will use the custom velocity function.
        callback
            A function with signature ``(body, gravity, damping, dt)``.
            If ``None``, the default Pymunk velocity update is restored.
        """
        for mob in mobs:
            self.vspace.set_velocity_func(mob, callback)

    # get velocity info
    def get_velocity_at_local_point(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    )-> Tuple[float, float, float]:
        """Return the velocity of a point on the Mobject's body expressed
        in local body coordinates.

        Parameters
        ----------
        mob
            The Mobject whose body is queried.
        point
            The local point (x, y, z) at which to compute velocity.
            Defaults to (0, 0, 0).

        Returns
        -------
        Tuple[float, float, float]
            The velocity vector (vx, vy, 0) at the given point.
        """
        return self.vspace.velocity_at_local_point(mob, point)

    def velocity_at_world_point(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    )-> Tuple[float, float, float]:
        """Return the velocity of a point on the Mobject's body expressed
        in world (scene) coordinates.

        Parameters
        ----------
        mob
            The Mobject whose body is queried.
        point
            The world point (x, y, z) at which to compute velocity.
            Defaults to (0, 0, 0).

        Returns
        -------
        Tuple[float, float, float]
            The velocity vector (vx, vy, 0) at the given point.
        """
        return self.vspace.velocity_at_world_point(mob, point)

    # get point info
    def get_point_query_info(
        self, mob: Mobject, point: Tuple[float, float, float] = (0, 0, 0)
    ) -> list:
        """Query which shapes of the Mobject contain or are closest to a
        given point in world coordinates.

        Parameters
        ----------
        mob
            The Mobject whose shapes will be queried.
        point
            The world point (x, y, z) to test against. Defaults to (0, 0, 0).

        Returns
        -------
        list
            A list of point query results for each shape of the Mobject.
        """
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
        """Perform a segment (line) query against the Mobject's shapes,
        finding the first intersection along the line segment.

        Parameters
        ----------
        mob
            The Mobject whose shapes will be queried.
        start
            Start point (x, y, z) of the query segment.
        end
            End point (x, y, z) of the query segment.
        stroke_width
            Thickness of the query segment (for hit detection).

        Returns
        -------
        list
            A list of segment query hit results.
        """
        return self.vspace.get_line_query(mob, start, end, stroke_width)

    def get_shapea_shapeb_info(
        self, shape_a: pymunk.Shape, shape_b: pymunk.Shape
    ) -> list:
        """Return collision information between two specific Pymunk shapes,
        such as contact points and normal.

        Parameters
        ----------
        shape_a
            The first Pymunk shape to test.
        shape_b
            The second Pymunk shape to test.

        Returns
        -------
        list
            Collision information between the two shapes.
        """
        return self.vspace.get_shapea_shapeb_info(
            shape_a,
            shape_b,
        )