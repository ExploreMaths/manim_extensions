from manim.constants import *

def get_axis_from_face(face):
    """Return the rotation axis corresponding to a Rubik's cube face.

    Parameters
    ----------
    face : str
        Face identifier. One of ``"F"`` (front), ``"B"`` (back), ``"U"`` (up),
        ``"D"`` (down), ``"L"`` (left), or ``"R"`` (right).

    Returns
    -------
    numpy.ndarray
        The axis vector (``X_AXIS``, ``Y_AXIS``, or ``Z_AXIS``) about which the
        specified face rotates.
    """
    if face == "F" or face == "B":
        return X_AXIS
    elif face == "U" or face == "D":
        return Z_AXIS
    else:
        return Y_AXIS

def get_direction_from_face(face):
    """Return the rotation direction for a given face.

    .. note::

        This function is a placeholder and currently returns ``None``.
        Clockwise/counterclockwise mapping for each face is not yet implemented.

    Parameters
    ----------
    face : str
        Face identifier (``"F"``, ``"B"``, ``"U"``, ``"D"``, ``"L"``, or ``"R"``).

    Returns
    -------
    None
        Direction value. Not yet implemented.
    """
    return

def get_cubie_colors_from_state(state):
    """Extract individual cubie colours from a cube state string.

    The state string follows the standard cube notation where each
    character represents the colour of one face.

    Parameters
    ----------
    state : str
        Cube state string (e.g. from ``kociemba``).

    Returns
    -------
    list
        A list of colour characters grouped by cubie.
    """
    pass

def get_all_states(cube):
    """Return the current state of every cubie in the cube.

    Parameters
    ----------
    cube : RubiksCube
        The cube whose state is queried.

    Returns
    -------
    str
        Concatenated face-state string for all cubies.
    """
    pass

def get_type_of_cubie(dim, position):
    """Classify a cubie by its position within the cube.

    Parameters
    ----------
    dim : int
        Size of the cube (e.g. ``3`` for a standard 3x3x3 cube).
    position : tuple of int
        ``(x, y, z)`` coordinates of the cubie.

    Returns
    -------
    str
        One of ``"corner"``, ``"edge"``, or ``"center"`` depending on the
        cubie's location.
    """
    if (position[1] == 0 or position[1] == dim-1) and (position[2] == 0 or position[2] == dim-1):
        return "corner"
    elif position[1] == 0 or position[1] == dim-1:
        return "edge"
    else:
        return "center"

def get_faces_of_cubie(dim, position):
    """Return the outward-facing directions for a cubie at a given position.

    Parameters
    ----------
    dim : int
        Size of the cube (e.g. ``3`` for a standard 3x3x3 cube).
    position : tuple of int
        ``(x, y, z)`` coordinates of the cubie.

    Returns
    -------
    list of numpy.ndarray
        A list of direction vectors (e.g. :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.LEFT`, :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.RIGHT`, :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.UP`, :attr:`~manim_extensions.data_structures.m_enum.MArrayDirection.DOWN`,
        ``IN``, ``OUT``) indicating which faces of the cubie are exposed on the
        cube's surface.
    """
    dim = dim-1
    try:
        faces = {
            #Front corners
            (0, 0, 0): [LEFT, DOWN, IN],
            (0, 0, dim): [LEFT, DOWN, OUT],
            (0, dim, 0): [LEFT, UP, IN],
            (0, dim, dim): [LEFT, UP, OUT],
            #Back corners
            (dim, 0, 0): [RIGHT, DOWN, IN],
            (dim, 0, dim): [RIGHT, DOWN, OUT],
            (dim, dim, 0): [RIGHT, UP, IN],
            (dim, dim, dim): [RIGHT, UP, OUT],
        }
        return faces[position]
    except:
        x = position[0]
        y = position[1]
        z = position[2]

        if x == 0:
            if y == 0:
                return [DOWN, LEFT]
            elif y == dim:
                return [UP, LEFT]
            else:
                if z == 0:
                    return [IN, LEFT]
                elif z == dim:
                    return [OUT, LEFT]
                else:
                    return [LEFT]
        elif x == dim:
            if y == 0:
                return [DOWN, RIGHT]
            elif y == dim:
                return [UP, RIGHT]
            else:
                if z == 0:
                    return [IN, RIGHT]
                elif z == dim:
                    return [OUT, RIGHT]
                else:
                    return [RIGHT]
        else:
            if y == 0:
                if z == 0:
                    return [IN, DOWN]
                elif z == dim:
                    return [OUT, DOWN]
                else:
                    return [DOWN]
            elif y == dim:
                if z == 0:
                    return [IN, UP]
                elif z == dim:
                    return [OUT, UP]
                else:
                    return [UP]
            else:
                if z == 0:
                    return [IN]
                elif z == dim:
                    return [OUT]
                else:
                    return []