"""Rubik's Cube mobject built from Manim primitives.

This module exposes a 3D-styled cube model that is useful for puzzles,
visual demonstrations, and algorithm walkthroughs.

Examples
--------

.. manim:: RubiksCubeModuleExample

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class RubiksCubeModuleExample(ThreeDScene):
       def construct(self):
           cube = RubiksCube().scale(0.6)
           self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                            frame_center=cube.get_center())
           self.play(FadeIn(cube))
           self.begin_ambient_camera_rotation(rate=0.5)
           self.wait(8)
"""

from manim.utils.color import *
from manim.constants import ORIGIN
from manim.mobject.mobject import Mobject
from manim.mobject.types.vectorized_mobject import VMobject
import numpy as np
from .cubie import Cubie
import kociemba

sv = kociemba


class RubiksCube(VMobject):
    """A Manim-backed Rubik's Cube model.

    The cube is represented as a 3D voxel grid of :class:`~manim_extensions.rubikscube.cubie.Cubie` objects.
    The coordinate convention matches the project's original API: the cube is
    oriented so that X goes front-to-back, Y goes right-to-left, and Z goes
    down-to-up.

    Parameters
    ----------
    dim : int, optional
        Cube dimension. Must be at least 2.
    colors : list, optional
        Face colours in the order Up, Right, Front, Down, Left, Back.
    x_offset : float, optional
        Spatial offset along the X axis used to lay out the cubies.
    y_offset : float, optional
        Spatial offset along the Y axis used to lay out the cubies.
    z_offset : float, optional
        Spatial offset along the Z axis used to lay out the cubies.

    Examples
    --------
    .. manim:: RubiksCubeDocExample

       from manim import *
       from manim_extensions.rubikscube import RubiksCube

       class RubiksCubeDocExample(ThreeDScene):
           def construct(self):
               cube = RubiksCube().scale(0.6)
               self.move_camera(phi=50 * DEGREES, theta=160 * DEGREES,
                                frame_center=cube.get_center())
               self.play(FadeIn(cube))
               self.begin_ambient_camera_rotation(rate=0.5)
               self.wait(8)
    """

    #If facing the Rubik's Cube, X goes Front to Back, Y goes Right to Left, Z goes Down to Up 
    #Each coordinate starts at 0 and goes to (Dimensions - 1)

    cubies = np.ndarray
    indices = {}

    # Colors are in the order Up, Right, Front, Down, Left, Back
    def __init__(self, dim=3, colors=[WHITE, "#B90000", "#009B48", "#FFD500", "#FF5900", "#0045AD"], x_offset=2.1, y_offset=2.1, z_offset=2.1):#, **kwargs):
        """Initialize the RubiksCube instance."""
        if not (dim >= 2):
            raise Exception("Dimension must be >= 2")

        VMobject.__init__(self)
        self.dimensions = dim
        self.colors = colors
        self.x_offset = [[Mobject.shift, [x_offset, 0, 0]]]
        self.y_offset = [[Mobject.shift, [0, y_offset, 0]]]
        self.z_offset = [[Mobject.shift, [0, 0, z_offset]]]

        self.cubies = np.ndarray((dim, dim, dim), dtype=Cubie)
        self.generate_cubies()#**kwargs)
    
    def get_center(self):
        """Return the geometric center of the cube's bounding box.

        Returns
        -------
        numpy.ndarray
            The (x, y, z) center of the cube computed from the actual
            bounding box of all cubie points.
        """
        all_points = self.get_all_points()
        if len(all_points) == 0:
            return np.zeros(3)
        return (all_points.min(axis=0) + all_points.max(axis=0)) / 2

    def generate_cubies(self):#, **kwargs):
        """Populate the cube with its cubies and apply offsets.

        Returns
        -------
        None
            The cubies are added as submobjects of the cube.
        """
        for x in range(self.dimensions):
            for y in range(self.dimensions):
                for z in range(self.dimensions):
                    cubie = Cubie(x, y, z, self.dimensions, self.colors)#, **kwargs)
                    self.transform_cubie(x, self.x_offset, cubie)
                    self.transform_cubie(y, self.y_offset, cubie)
                    self.transform_cubie(z, self.z_offset, cubie)
                    self.add(cubie)
                    self.cubies[x, y, z] = cubie
        self.move_to(ORIGIN)

    def set_state(self, positions):
        """Apply a colour state to each cube face.

        Parameters
        ----------
        positions : iterable
            A sequence of face letters specifying the cube state.
        """
        colors = {
            "U": self.colors[0],
            "R": self.colors[1],
            "F": self.colors[2],
            "D": self.colors[3],
            "L": self.colors[4],
            "B": self.colors[5],
        }
        positions = list(positions)
        # TODO: Try/except in case a color was not given
        # try:
        for cubie in np.rot90(self.get_face("U", False), 2).flatten():
            cubie.get_face("U").set_fill(colors[positions.pop(0)], 1)

        for cubie in np.rot90(np.flip(self.get_face("R", False), (0, 1)), -1).flatten():
            cubie.get_face("R").set_fill(colors[positions.pop(0)], 1)
        
        for cubie in np.rot90(np.flip(self.get_face("F", False), 0)).flatten():
            cubie.get_face("F").set_fill(colors[positions.pop(0)], 1)
        
        for cubie in np.rot90(np.flip(self.get_face("D", False), 0), 2).flatten():
            cubie.get_face("D").set_fill(colors[positions.pop(0)], 1)
        
        for cubie in np.rot90(np.flip(self.get_face("L", False), 0)).flatten():
            cubie.get_face("L").set_fill(colors[positions.pop(0)], 1)
        
        for cubie in np.rot90(np.flip(self.get_face("B", False), (0, 1)), -1).flatten():
            cubie.get_face("B").set_fill(colors[positions.pop(0)], 1)
        # except:
            # return

    def solve_by_kociemba(self, state):
        """Solve a cube state using the kociemba solver.

        Parameters
        ----------
        state : str
            The cube state in the usual facelet notation accepted by kociemba.

        Returns
        -------
        list[str]
            A list of move tokens.
        """
        return sv.solve(state).replace("3", "'").replace("1", "").split()

    def transform_cubie(self, position, offset, tile):
        """Apply translation offsets to a cubie based on its position.

        Parameters
        ----------
        position : int
            The cubie position along the cube axis.
        offset : list
            The offset metadata used to translate the cubie.
        tile : Cubie
            The cubie to transform.
        """
        offsets_nr = len(offset)
        for i in range(offsets_nr):
            for j in range(int(len(offset[i]) / 2)):
                if position < 0:
                    magnitude = len(range(-i, position, -offsets_nr)) * -1
                    offset[-1 - i][0 + j * 2](
                        tile, magnitude * np.array(offset[-1 - i][1 + j * 2])
                    )
                else:
                    magnitude = len(range(i, position, offsets_nr))
                    offset[i][0 + j * 2](
                        tile, magnitude * np.array(offset[i][1 + j * 2])
                    )

    def get_face(self, face, flatten=True):
        """Return a face of the cube, optionally flattened into a 1D array.

        Parameters
        ----------
        face : str
            The face label to retrieve: one of ``"U"``, ``"R"``, ``"F"``,
            ``"D"``, ``"L"``, or ``"B"``.
        flatten : bool, optional
            Whether to flatten the selected face into a 1D iterable.

        Returns
        -------
        numpy.ndarray
            The selected face values, either as a 2D grid or a flattened array.
        """
        if face == "F":
            face = self.cubies[0, :, :]
        elif face == "B":
            face = self.cubies[self.dimensions-1, :, :]
        elif face == "U":
            face = self.cubies[:, :, self.dimensions-1]
        elif face == "D":
            face = self.cubies[:, :, 0]
        elif face == "L":
            face = self.cubies[:, self.dimensions-1, :]
        elif face == "R":
            face = self.cubies[:, 0, :]

        if flatten:
            return face.flatten()
        else:
            return face
    
    def set_indices(self):
        """Build the position-to-cubie index map for the current cube state."""
        for c in self.cubies.flatten():
            # self.indices[c.get_position()] = c.get_position()
            self.indices[c.get_rounded_center()] = c.position

    def adjust_indices(self, cubies):
        """Rebuild the cube index mapping from a set of cubies.

        Parameters
        ----------
        cubies : numpy.ndarray
            The cubies whose positions should be reindexed.
        """
        for c in cubies.flatten():
            loc = self.indices[c.get_rounded_center()]
            self.cubies[loc[0], loc[1], loc[2]] = c