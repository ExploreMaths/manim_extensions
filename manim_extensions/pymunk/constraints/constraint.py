# SPDX-FileCopyrightText: 2026 manim-pymunk
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: lazy-import pymunk (physics extra)
"""Base constraint class for Pymunk.

This module provides the VConstraint base class for Pymunk constraint visualizations.

"""

from __future__ import annotations

from manim import Mobject, VGroup
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymunk import Space


class VConstraint(VGroup):
    """The Manim base class for visualizing Pymunk physical constraints.

    Parameters
    ----------
    a_mob
        The first Mobject to be connected.
    b_mob
        The second Mobject to be connected.
    **kwargs
        Forwarded to the parent :class:`~manim.mobject.types.vectorized_mobject.VGroup`.

    Examples
    --------
    .. manim:: VConstraintExample
       :save_last_frame:

       from manim import *
       from manim_extensions.pymunk.constraints.constraint import VConstraint

       class VConstraintExample(Scene):
           def construct(self):
               mob_a = Dot(LEFT)
               mob_b = Dot(RIGHT)
               self.add(mob_a, mob_b, VConstraint(mob_a, mob_b))
    """

    def __init__(self, a_mob: Mobject = None, b_mob: Mobject = None, **kwargs):
        """Initialize the base VConstraint by calling the parent VGroup
        constructor, storing the two connected mobjects, and validating
        constraint parameters.
        """
        super().__init__(**kwargs)
        self.a_mob = a_mob
        self.b_mob = b_mob
        self.constraint = None
        self._check_data()

    def _check_data(self):
        """Verify the validity of constraint parameters.

        Override in subclasses to perform subclass-specific validation.
        """
        pass

    def _get_bodies(self, error_msg: str = None):
        """Extract pymunk bodies from the two connected mobjects and validate them.

        Parameters
        ----------
        error_msg
            Custom error message for the ValueError raised when a body is missing.
            If None, a default message using the class name is generated.

        Returns
        -------
        tuple
            A (a_body, b_body) tuple of pymunk Body objects.

        Raises
        ------
        ValueError
            If either mobject does not have a pymunk body attached.
        """
        a_body = getattr(self.a_mob, "body", None)
        b_body = getattr(self.b_mob, "body", None)
        if not a_body or not b_body:
            if error_msg is None:
                error_msg = (
                    f"{self.__class__.__name__} connected objects "
                    "must have Pymunk bodies."
                )
            raise ValueError(error_msg)
        return a_body, b_body

    def _finalize_install(self, space: Space):
        """Finalize the installation by adding the constraint to the space
        and registering the per-frame updater.

        This is a common final step called at the end of every ``install`` method.
        """
        space.add(self.constraint)
        self.add_updater(self.mob_updater)

    def install(self, space: Space):
        """Installs physical constraints into the Pymunk physical space.
        This method should be overridden by subclasses to implement the following:

        1. Create Pymunk constraint objects
        2. Initialize the vision component
        3. Add constraints to the physical space
        4. Bind an updater to keep the vision synchronized.

        Parameters
        ----------
        space : Space
            The Pymunk space to install the constraint into.
        """
        pass

    def mob_updater(self, mob: Mobject, dt: float):
        """Updates the visual representation of constraints in real time.
        This method should be overridden by subclasses and called in every frame,
        to synchronize the state of the visual components and the physics engine regarding constraints.

        Parameters
        ----------
        mob : Mobject
            The constraint mobject being updated.
        dt : float
            Time step since the last frame, in seconds.
        """
        pass