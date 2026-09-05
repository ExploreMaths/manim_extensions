# SPDX-FileCopyrightText: 2026 manim-pymunk
#
# SPDX-License-Identifier: MIT

# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Base constraint class for Pymunk.

This module provides the VConstraint base class for Pymunk constraint visualizations.

"""

from manim import *
from pymunk import Space


class VConstraint(VGroup):
    """The Manim base class for visualizing Pymunk physical constraints.

    Parameters
    ----------
    **kwargs
        Forwarded to the parent :class:`~manim.mobject.types.vectorized_mobject.VGroup`.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__check_data()

    def __check_data(self):
        """ Verify the validity of constraint parameters.
            Requires subclass implementation
        """
        pass

    def install(self, space: Space):
        """Installs physical constraints into the Pymunk physical space.
        This method should be overridden by subclasses to implement the following:

        1. Create Pymunk constraint objects
        2. Initialize the vision component
        3. Add constraints to the physical space
        4. Bind an updater to keep the vision synchronized.
        """
        pass

    def mob_updater(self, mob: Mobject, dt: float):
        """Updates the visual representation of constraints in real time.
        This method should be overridden by subclasses and called in every frame,
        to synchronize the state of the visual components and the physics engine regarding constraints.
        """
        pass