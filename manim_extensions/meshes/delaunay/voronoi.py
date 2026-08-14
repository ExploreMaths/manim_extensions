"""
functions to display voronoi diagram and create delaunay meshes as its dual
"""
# python imports
import numpy as np
# third-party imports
from scipy.spatial import Voronoi  # pylint: disable=no-name-in-module
import manim as m
# local imports
from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh


class VoronoiDelaunay:
    """Class providing methods to visualize the voronoi diagram of a 2D point set and its dual
    delaunay triangulation

    Examples
    --------

    .. manim:: VoronoiDelaunayExample
      :save_last_frame:

        from manim import *
        from manim_extensions.meshes.models.data_models.mesh import Mesh
        from manim_extensions.meshes.models.manim_models.triangle_mesh import TriangleManim2DMesh
        from manim_extensions.meshes.delaunay.voronoi import VoronoiDelaunay

        class VoronoiDelaunayExample(Scene):
            def construct(self):
                import numpy as np
                pts = np.random.RandomState(42).rand(10, 3)
                pts[:, 2] = 0
                vertices = pts.tolist()
                faces = []
                mesh_data = Mesh(vertices, faces)
                tm = TriangleManim2DMesh(mesh_data)
                self.add(tm)
                vd = VoronoiDelaunay(self, tm)
"""

    def __init__(self, scene: m.Scene, triangle_mesh: TriangleManim2DMesh) -> None:
        """Initialise the Voronoi-Delaunay visualisation helper.

        Parameters
        ----------
        scene : m.Scene
            The scene in which the Voronoi/Delaunay diagrams will be drawn.
        triangle_mesh : TriangleManim2DMesh
            A triangle mesh whose vertices are used to build the Voronoi
            diagram. The mesh must already have been added to *scene*.
        """
        self.scene: m.Scene = scene
        self.triangle_mesh: TriangleManim2DMesh = triangle_mesh
        verts = self.triangle_mesh.mesh.get_3d_vertices()
        self.voronoi = Voronoi(verts[:, :2])

    def create_voronoi(self):
        """Build the Voronoi diagram for the mesh vertices and return it as Manim groups.

        The diagram is constructed from the :class:`scipy.spatial.Voronoi`
        computation stored in :attr:`voronoi`.  Both finite and infinite
        ridge segments are converted to :class:`~manim.mobject.geometry.line.Line`
        objects, and Voronoi vertices become :class:`~manim.mobject.geometry.arc.Dot`
        objects.

        Returns
        -------
        tuple[VGroup, VGroup]
            A pair of :class:`~manim.mobject.types.vectorized_mobject.VGroup`
            containers holding the Voronoi vertices (dots) and the connecting
            ridge lines, respectively.

        Notes
        -----
        Based on the logic in :func:`scipy.spatial.voronoi_plot_2d`.
        """
        verts = self.triangle_mesh.mesh.get_3d_vertices()
        vert_group = m.VGroup()
        line_group = m.VGroup()

        center = verts.mean(axis=0)
        ptp_bound = verts.ptp(axis=0)
        voronoi_vertices = np.pad(self.voronoi.vertices, ((0, 0), (0, 1)))

        # add voronoi lines
        for point_indices, segment in zip(self.voronoi.ridge_points, self.voronoi.ridge_vertices):
            segment = np.asarray(segment)
            if np.all(segment >= 0):  # finite segment
                line = m.Line(voronoi_vertices[segment[0]], voronoi_vertices[segment[1]],
                              stroke_width=self.triangle_mesh.edges_width, color=m.WHITE)
                line_group.add(line)
            else:  # infinite segment
                i = segment[segment >= 0][0]  # finite end

                t = verts[point_indices[1]] - verts[point_indices[0]]  # tangent
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0], 0])  # normal

                midpoint = verts[point_indices].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = voronoi_vertices[i] + direction * ptp_bound.max()

                line = m.Line(voronoi_vertices[i], far_point,
                              stroke_width=self.triangle_mesh.edges_width, color=m.WHITE)
                line_group.add(line)

        # add voronoi vertices
        for vert in voronoi_vertices:
            dot = m.Dot(vert, radius=self.triangle_mesh.verts_size, color=m.WHITE)
            vert_group.add(dot)

        return vert_group, line_group

    def get_circum_circle(self, voronoi_vertex_index, color=m.ORANGE):
        """Return the circumscribed circle of the triangle dual to a Voronoi vertex.

        The circle is centred at the Voronoi vertex and passes through the
        three mesh vertices that form the dual triangle.

        Parameters
        ----------
        voronoi_vertex_index : int
            Index of the Voronoi vertex whose dual triangle's circumcircle
            is computed.
        color : ManimColor, optional
            Stroke colour of the returned circle. Defaults to ``ORANGE``.

        Returns
        -------
        m.Circle or None
            A :class:`~manim.mobject.geometry.arc.Circle` representing the
            circumscribed circle, or ``None`` if the vertex index does not
            belong to any triangle ridge.
        """
        verts = self.triangle_mesh.mesh.get_3d_vertices()
        voronoi_vertices = np.pad(self.voronoi.vertices, ((0, 0), (0, 1)))
        for point_indices, segment in zip(self.voronoi.ridge_points, self.voronoi.ridge_vertices):
            if voronoi_vertex_index in segment:
                vert_a = voronoi_vertices[voronoi_vertex_index]
                vert_b = verts[point_indices[0]]
                circle = m.Circle(radius=np.linalg.norm(vert_b - vert_a), stroke_width=2, color=color)
                circle.shift(vert_a)
                return circle
        return None  # should never get here

    def create_triangle(self, voronoi_vertex_index):
        """Create the dual triangle for a given Voronoi vertex and add it to the mesh.

        The triangle is formed by the three mesh vertices whose Voronoi
        regions meet at the specified Voronoi vertex.

        Parameters
        ----------
        voronoi_vertex_index : int
            Index of the Voronoi vertex whose dual triangle is created.
        """

        triangle_indices = set()
        for point_indices, segment in zip(self.voronoi.ridge_points, self.voronoi.ridge_vertices):
            if voronoi_vertex_index in segment:
                triangle_indices.add(point_indices[0])
                triangle_indices.add(point_indices[1])
        _, _ = self.triangle_mesh.add_face(np.array(list(triangle_indices)))