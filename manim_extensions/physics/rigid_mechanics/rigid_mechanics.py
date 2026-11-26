# SPDX-FileCopyrightText: 2024 Matheart
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)

"""A gravity simulation space.

Most objects can be made into a rigid body (moves according to gravity
and collision) or a static body (stays still within the scene).

To use this feature, the :class:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene` must be used, to access
the specific functions of the space.

.. seealso::

   *   This feature utilizes the pymunk package. Although unnecessary,
       it might make it easier if you knew a few things on how to use it.

       `Official Documentation <http://www.pymunk.org/en/latest/pymunk.html>`_

       `Youtube Tutorial <https://youtu.be/pRk---rdrbo>`_

   *   A low frame rate might cause some objects to pass static objects as
       they don't register collisions finely enough. Trying to increase the
       config frame rate might solve the problem.
"""

from __future__ import annotations
from typing import Any, Protocol, TYPE_CHECKING, cast

import numpy as np

from manim import (
    Circle,
    Line,
    Mobject,
    VMobject,
    Polygon,
    Polygram,
    RIGHT,
    CairoRenderer,
    Rectangle,
    Scene,
    UP,
    Group,
    VGroup,
    angle_between_vectors,
)
from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
from manim.renderer.opengl_renderer import OpenGLRenderer

from ...utils.deps import require

if TYPE_CHECKING:
    import pymunk

__all__ = [
    "Space",
    "_step",
    "_simulate",
    "get_shape",
    "get_angle",
    "SpaceScene",
]


def _load_pymunk() -> Any:
    """Import pymunk lazily, as it belongs to the ``physics`` extra.

    Returns
    -------
        The imported pymunk module.
    """
    return require("physics", "pymunk")


class PhysicsAttributes(Protocol):
    """Structural type of a mobject augmented with pymunk body attributes.

    The attributes are attached dynamically by
    :meth:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene.make_rigid_body`
    and :func:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.get_shape`.

    Examples
    --------
    .. manim:: PhysicsAttributesOverview
       :save_last_frame:

       from manim import *
       from manim_extensions.physics.rigid_mechanics.rigid_mechanics import PhysicsAttributes

       PhysicsAttributesTarget = PhysicsAttributes

       class PhysicsAttributesOverview(Scene):
           def construct(self):
               public = [n for n in dir(PhysicsAttributesTarget) if not n.startswith("_")]
               card = VGroup(
                   Text('PhysicsAttributes', font_size=36),
                   Text('module: manim_extensions.physics.rigid_mechanics.rigid_mechanics', font_size=18, color=GREY),
                   Text('Structural type of a mobject augmented with pymunk body attributes', font_size=22),
                   Text("API: " + ", ".join(public[:6]), font_size=18, color=BLUE),
               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
               card.scale_to_fit_width(11.5).move_to(ORIGIN)
               frame = RoundedRectangle(
                   width=12.1, height=card.height + 0.5, corner_radius=0.2, color=BLUE_D
               ).move_to(card)
               self.add(frame, card)

    .. code-block:: python

        def describe(body: PhysicsAttributes) -> float:
            return body.body.position.x
    """

    body: pymunk.Body
    shape: pymunk.Shape
    angle: float
    spacescene: SpaceScene


class Space(Mobject, metaclass=ConvertToOpenGL):
    """Physics space that manages a pymunk simulation.

    The :class:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.Space` object wraps a :class:`~pymunk.Space` and is automatically
    added to every :class:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene`.  It owns the gravity configuration and
    the simulation step that is called each frame.

    Parameters
    ----------
    gravity
        Gravity vector :math:`(x, y)`.
    **kwargs
        Additional keyword arguments passed to :class:`~manim.mobject.mobject.Mobject`.

    Examples
    --------
    .. manim:: Space

       from manim import *
       from manim_extensions.physics.rigid_mechanics.rigid_mechanics import (
           SpaceScene,
       )

       class Space(SpaceScene):
           GRAVITY = (0, -5)
           def construct(self):
               ground = Line(LEFT * 7, RIGHT * 7).shift(DOWN * 3)
               ceiling = Line(LEFT * 7, RIGHT * 7).shift(UP * 3)
               ball = Circle(radius=0.4, stroke_color=BLUE,
                             fill_color=BLUE, fill_opacity=1)
               ball.shift(ground.get_center() + UP * 4)
               self.play(FadeIn(ground), FadeIn(ceiling), FadeIn(ball))
               self.make_static_body(ground, ceiling)
               self.make_rigid_body(ball)
               self.wait(2)
               self.space.space.gravity = (0, 5)
               self.wait(4)
    """

    def __init__(
        self, gravity: tuple[float, float] = (0, -9.81), **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        pymunk = require("physics", "pymunk")
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.sleep_time_threshold = 5


class SpaceScene(Scene):
    """Scene with built-in pymunk rigid-body physics.

    :class:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene` is the base scene class for all rigid-mechanics
    animations.  It creates a :class:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.Space` instance and sets up the
    simulation updater so that any mobject registered via
    :meth:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene.make_rigid_body` or :meth:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene.make_rigid_body` participates in the
    physics simulation.

    .. tip::

       The gravity vector can be customised by overriding the class
       attribute :attr:`~manim_extensions.physics.rigid_mechanics.rigid_mechanics.SpaceScene.GRAVITY` before instantiation.

    Parameters
    ----------
    renderer
        Renderer name forwarded to the parent :class:`~manim.scene.scene.Scene`.
    **kwargs
        Forwarded to the parent :class:`~manim.scene.scene.Scene`.

    Examples
    --------
    .. manim:: SpaceSceneUsage

       from manim import *
       from manim_extensions.physics.rigid_mechanics.rigid_mechanics import (
           SpaceScene,
       )

       class SpaceSceneUsage(SpaceScene):
           def construct(self):
               circle = Circle().shift(UP)
               circle.set_fill(RED, 1)
               circle.shift(DOWN + RIGHT)
               rect = Square().shift(UP)
               rect.rotate(PI / 4)
               rect.set_fill(YELLOW_A, 1)
               rect.shift(UP * 2)
               rect.scale(0.5)
               ground = Line([-4, -3.5, 0], [4, -3.5, 0])
               wall1 = Line([-4, -3.5, 0], [-4, 3.5, 0])
               wall2 = Line([4, -3.5, 0], [4, 3.5, 0])
               walls = VGroup(ground, wall1, wall2)
               self.play(
                   DrawBorderThenFill(circle),
                   DrawBorderThenFill(rect),
               )
               self.add(walls)
               # Mobjects will move with gravity
               self.make_rigid_body(rect, circle)
               # Mobjects will stay in place
               self.make_static_body(walls)
               self.wait(5)
    """

    #: Default gravity vector applied by the physics space.
    GRAVITY: tuple[float, float] = 0, -9.81

    def __init__(
        self, renderer: CairoRenderer | OpenGLRenderer | None = None, **kwargs: Any
    ) -> None:
        self.space = Space(gravity=self.GRAVITY)
        super().__init__(renderer=renderer, **kwargs)

    def setup(self) -> Any:
        """Add the physics space to the scene and advance it every frame.

        Returns
        -------
            The resulting value.
        """
        self.add(self.space)
        self.space.add_updater(_step)

    def add_body(self, body: Mobject) -> Any:
        """Register a pymunk body's shape in the physics space.

        Parameters
        ----------
        body
            A mobject whose ``body`` and ``shape`` attributes are pymunk
            objects to be added to the simulation space.


        Returns
        -------
            The resulting value.
        """
        if body.body != self.space.space.static_body:
            self.space.space.add(body.body)
        self.space.space.add(body.shape)

    def make_rigid_body(
        self,
        *mobs: Mobject,
        elasticity: float = 0.8,
        density: float = 1,
        friction: float = 0.8,
    ) -> Any:
        """Make any mobject movable by gravity.
        Equivalent to :class:`~manim.scene.scene.Scene`'s ``add`` function.

        Parameters
        ----------
        mobs
            The mobs to be made rigid.
        elasticity
            Elasticity of the mobjects.
        density
            Density of the mobjects.
        friction
            Friction of the mobjects in regards to
            interacting with other rigid and static objects.


        Returns
        -------
            The resulting value.
        """
        pymunk = require("physics", "pymunk")
        for mob in mobs:
            if not hasattr(mob, "body"):
                self.add(mob)
                cast(Any, mob).body = pymunk.Body()
                cast(Any, mob).body.position = mob.get_x(), mob.get_y()
                get_angle(cast(VMobject, mob))
                if not hasattr(mob, "angle"):
                    cast(Any, mob).angle = 0
                cast(Any, mob).body.angle = mob.angle
                get_shape(cast(VMobject, mob))
                cast(Any, mob.shape).density = density
                cast(Any, mob.shape).elasticity = elasticity
                cast(Any, mob.shape).friction = friction
                cast(Any, mob).spacescene = self

                self.add_body(mob)
                mob.add_updater(_simulate)

            else:
                if cast(Any, mob.body).is_sleeping:
                    cast(Any, mob.body).activate()

    def make_static_body(
        self, *mobs: Mobject, elasticity: float = 1, friction: float = 0.8
    ) -> Any:
        """Make any mobject interactable by rigid objects.

        Parameters
        ----------
        mobs
            The mobs to be made static.
        elasticity
            Elasticity of the mobjects.
        friction
            Friction of the mobjects in regards to
            interacting with rigid objects.


        Returns
        -------
            The resulting value.
        """
        for mob in mobs:
            if isinstance(mob, (VGroup, Group)):
                self.make_static_body(*mob)
                return
            cast(Any, mob).body = self.space.space.static_body
            get_shape(cast(VMobject, mob))
            cast(Any, mob.shape).elasticity = elasticity
            cast(Any, mob.shape).friction = friction
            self.add_body(mob)

    def stop_rigidity(self, *mobs: Mobject) -> Any:
        """Stop the mobjects rigidity.

        Parameters
        ----------
        mobs
            Mobs processed by this operation.


        Returns
        -------
            The resulting value.
        """
        for mob in mobs:
            if isinstance(mob, (VGroup, Group)):
                self.stop_rigidity(*mob)
            if hasattr(mob, "body"):
                cast(Any, mob.body).sleep()


def _step(space: Mobject, dt: float = 1 / 60) -> Any:
    """Advance the pymont simulation by one time step.

    Parameters
    ----------
    space
        The physics space containing the simulation.
    dt
        Time step size in seconds.


    Returns
    -------
            The resulting value.
    """
    cast(Any, space).space.step(dt)


def _simulate(b: Mobject) -> Any:
    """Read the current state of a pymont body and update the Manim mobject.

    Parameters
    ----------
    b
        The physics body whose state is synchronised to its mobject.


    Returns
    -------
            The resulting value.
    """
    x, y = cast(Any, b.body).position
    b.move_to(x * RIGHT + y * UP)
    b.rotate(cast(Any, b.body).angle - cast(Any, b).angle)
    cast(Any, b).angle = cast(Any, b.body).angle


def get_shape(mob: VMobject) -> Any:
    """Obtains the shape of the body from the mobject.

    Parameters
    ----------
    mob
        The mobject to manipulate.


    Returns
    -------
            The resulting value.
    """
    pymunk = require("physics", "pymunk")
    if isinstance(mob, Circle):
        cast(Any, mob).shape = pymunk.Circle(body=mob.body, radius=mob.radius)
    elif isinstance(mob, Line):
        cast(Any, mob).shape = pymunk.Segment(
            mob.body,
            (mob.get_start()[0], mob.get_start()[1]),
            (mob.get_end()[0], mob.get_end()[1]),
            mob.stroke_width - 3.95,
        )
    elif issubclass(type(mob), Rectangle):
        width = np.linalg.norm(mob.get_vertices()[1] - mob.get_vertices()[0])
        height = np.linalg.norm(mob.get_vertices()[2] - mob.get_vertices()[1])
        cast(Any, mob).shape = pymunk.Poly.create_box(mob.body, (width, height))
    elif issubclass(type(mob), Polygram):
        vertices = [(a, b) for a, b, _ in mob.get_vertices() - mob.get_center()]
        cast(Any, mob).shape = pymunk.Poly(mob.body, vertices)
    else:
        cast(Any, mob).shape = pymunk.Poly.create_box(mob.body, (mob.width, mob.height))


def get_angle(mob: VMobject) -> Any:
    """Obtains the angle of the body from the mobject.
    Used internally for updaters.

    Parameters
    ----------
    mob
        The mobject to manipulate.


    Returns
    -------
            The resulting value.
    """
    if issubclass(type(mob), Polygon):
        vec1 = mob.get_vertices()[0] - mob.get_vertices()[1]
        vec2 = type(mob)().get_vertices()[0] - type(mob)().get_vertices()[1]
        cast(Any, mob).angle = angle_between_vectors(vec1, vec2)
    elif isinstance(mob, Line):
        cast(Any, mob).angle = mob.get_angle()
