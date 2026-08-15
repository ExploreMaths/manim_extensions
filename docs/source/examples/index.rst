Example Gallery
===============

The examples below use Manim's ``.. manim::`` directive to render the scene
inline. Each example demonstrates one of the core extension modules.

.. manim:: LabelDotExample
   :save_last_frame:
   :no_title:
   :ref_classes: LabelDot

   from manim_extensions import LabelDot

   class LabelDotExample(Scene):
       def construct(self):
           dot = LabelDot("A", [0, 0, 0], label_pos=UP, buff=0.2)
           self.add(dot)

.. manim:: MathTexHelpersExample
   :save_last_frame:
   :no_title:
   :ref_classes: MathTexLine MathTexBrace MathTexDoublearrow

   from manim import *
   from manim_extensions import MathTexLine, MathTexBrace, MathTexDoublearrow

   class MathTexHelpersExample(Scene):
       def construct(self):
           line = Line(LEFT * 3, RIGHT * 3)
           self.add(line)
           self.add(MathTexLine(MathTex("y = x"), direction=UP, color=BLUE).next_to(line, UP, buff=1.0))
           self.add(MathTexBrace(line, MathTex(r"\Delta x"), direction=UP))
           self.add(MathTexDoublearrow(MathTex(r"\Leftrightarrow"), direction=DOWN).next_to(line, DOWN, buff=1.0))

.. manim:: GeometryHelpersExample
   :save_last_frame:
   :no_title:
   :ref_classes: ExtendedLine PerpendicularLine PerpendicularSign

   from manim import *
   from manim_extensions import ExtendedLine, PerpendicularLine, PerpendicularSign

   class GeometryHelpersExample(Scene):
       def construct(self):
           base = Line(LEFT * 3, RIGHT * 3, color=BLUE)
           ext = ExtendedLine(base, extend_distance=1.0, color=RED)
           perp = PerpendicularLine(UP * 1.5, base, color=YELLOW)
           sign = PerpendicularSign(base, perp, length=0.25, color=WHITE)
           self.add(base, ext, perp, sign)

.. manim:: CircleIntExample
   :save_last_frame:
   :no_title:
   :ref_classes: CircleInt

   from manim import *
   from manim_extensions import CircleInt, LabelDot

   class CircleIntExample(Scene):
       def construct(self):
           c1 = Circle(radius=2, color=BLUE).shift(LEFT)
           c2 = Circle(radius=2, color=GREEN).shift(RIGHT)
           pts = CircleInt(c1, c2)

           self.add(c1, c2)
           if pts:
               for i, p in enumerate(pts):
                   self.add(LabelDot(f"P{i+1}", p, label_pos=UP, buff=0.1))

.. manim:: TextAnimationsExample
   :no_title:
   :ref_classes: TypeWriter WriteRandom FadeOutRandom

   from manim import *
   from manim_extensions import TypeWriter, WriteRandom, FadeOutRandom

   class TextAnimationsExample(Scene):
       def construct(self):
           text = Text("Hello World").scale(1.5)
           self.play(TypeWriter(text, interval=0.08))
           self.wait()
           self.play(FadeOutRandom(text))
           new_text = Text("Random!").scale(1.5)
           self.play(WriteRandom(new_text))
           self.wait()

.. manim:: ColorTextExample
   :save_last_frame:
   :no_title:
   :ref_classes: ColorText

   from manim import *
   from manim_extensions import ColorText

   class ColorTextExample(Scene):
       def construct(self):
           self.add(ColorText([150, 60, 200]).scale(0.9))

.. manim:: FileTreeExample
   :save_last_frame:
   :no_title:
   :ref_classes: FileTree

   from manim import *
   from manim_extensions import FileTree

   class FileTreeExample(Scene):
       def construct(self):
           tree = FileTree({
               "src": {
                   "main.py": None,
                   "utils": {
                       "helpers.py": None,
                   },
               },
               "README.md": None,
               "tests": {
                   "test_main.py": None,
               },
           }).scale(0.7)
           self.add(tree)

.. manim:: TreeDiagramExample
   :save_last_frame:
   :no_title:
   :ref_classes: TreeDiagram

   from manim import *
   from manim_extensions import TreeDiagram

   class TreeDiagramExample(Scene):
       def construct(self):
           tree = {"A": {"B": {"D", "E"}, "C": {"F", "G"}}}
           self.add(TreeDiagram(tree).shift(LEFT * 2))

.. manim:: HighlightAnimationsExample
   :no_title:
   :ref_classes: PassingRectangle HighLightWithLines

   from manim import *
   from manim_extensions import PassingRectangle, HighLightWithLines

   class HighlightAnimationsExample(Scene):
       def construct(self):
           mob = Text("Hello").scale(2)
           self.add(mob)
           self.play(PassingRectangle(SurroundingRectangle(mob)))
           self.wait()
           self.play(HighLightWithLines(mob))
           self.wait()

.. manim:: DecorationHelpersExample
   :save_last_frame:
   :no_title:
   :ref_classes: ShadowAround ObjectBorder

   from manim import *
   from manim_extensions import ShadowAround, ObjectBorder

   class DecorationHelpersExample(Scene):
       def construct(self):
           c = Circle(radius=1.2, fill_color=TEAL, fill_opacity=1, stroke_width=0).shift(LEFT * 2)
           self.add(ShadowAround(c, blur_width=0.4, shadow_color=WHITE))
           self.add(c)
           t = Text("Hi").scale(2).shift(RIGHT * 2)
           self.add(t, ObjectBorder(t))

.. manim:: TrailExample
   :no_title:
   :ref_classes: Trail

   from manim import *
   from manim_extensions import Trail

   class TrailExample(Scene):
       def construct(self):
           dot = Dot(color=BLUE).shift(LEFT * 2)
           trail = Trail(dot, trail_color=BLUE, nums=30).start_trace()
           self.add(trail)
           self.play(Rotating(dot, about_point=ORIGIN, rate_func=linear))

.. manim:: VisDrawArcExample
   :no_title:
   :ref_functions: VisDrawArc

   from manim import *
   from manim_extensions import VisDrawArc

   class VisDrawArcExample(Scene):
       def construct(self):
           arc = Arc(start_angle=0, angle=PI, radius=2, color=YELLOW)
           VisDrawArc(self, arc, axis=OUT, run_time=2)

.. manim:: ChineseMathTexExample
   :save_last_frame:
   :no_title:
   :ref_classes: ChineseMathTex

   from manim import *
   from manim_extensions import ChineseMathTex

   class ChineseMathTexExample(Scene):
       def construct(self):
           tex = ChineseMathTex(r"$E = mc^2$").scale(1.5)
           self.add(tex)

.. manim:: ThreeDVectorExample
   :save_last_frame:
   :no_title:
   :ref_classes: ThreeDVector

   from manim import *
   from manim_extensions import ThreeDVector

   class ThreeDVectorExample(ThreeDScene):
       def construct(self):
           self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)
           self.add(ThreeDAxes())
           self.add(ThreeDVector([2, 1, 1.5], color=YELLOW))

.. manim:: MoreAnimationsExample
   :no_title:
   :ref_classes: ReversedWrite FadeInRandom GrowRandom LaggedCreation UnHighLightWithLines

   from manim import *
   from manim_extensions import ReversedWrite, FadeInRandom, GrowRandom, LaggedCreation

   class MoreAnimationsExample(Scene):
       def construct(self):
           text = Text("Animation").scale(2)
           self.add(text)
           self.play(ReversedWrite(text))
           self.wait()
           self.play(GrowRandom(text))
           self.wait()

.. manim:: AlgorithmExample
   :save_last_frame:
   :no_title:
   :ref_classes: Node Array Queue

   from manim import *
   from manim_extensions.algorithm import Node, Array, Queue

   class AlgorithmExample(Scene):
       def construct(self):
           title = Text("Algorithm Primitives", font_size=28).to_edge(UP)
           nodes = VGroup(
               Node("1"), Node("2"), Node("3")
           ).arrange(RIGHT, buff=0.5).next_to(title, DOWN, buff=1)
           arr = Array([10, 20, 30, 40], total_width=6).next_to(nodes, DOWN, buff=1)
           q = Queue([Square(side_length=0.3, fill_color=BLUE, fill_opacity=0.8) for _ in range(3)]).next_to(arr, DOWN, buff=1)
           self.add(title, nodes, arr, q)

.. manim:: CircuitExample
   :save_last_frame:
   :no_title:
   :ref_classes: VoltageSource Resistor Capacitor Ground

   from manim import *
   from manim_extensions.circuit import VoltageSource, Resistor, Capacitor, Ground

   class CircuitExample(Scene):
       def construct(self):
           vs = VoltageSource(value=5).shift(LEFT * 3)
           r = Resistor(label="10k").next_to(vs, RIGHT, buff=2)
           c = Capacitor(label="100n").next_to(r, RIGHT, buff=2)
           g = Ground().next_to(vs, DOWN, buff=1.5)
           self.add(vs, r, c, g)

.. manim:: CompassExample
   :save_last_frame:
   :no_title:
   :ref_classes: Compass Pencil Ruler

   from manim import *
   from manim_extensions.compass import Compass, Pencil, Ruler

   class CompassExample(Scene):
       def construct(self):
           c = Compass().shift(LEFT * 2)
           p = Pencil().shift(UP * 2 + RIGHT * 2)
           r = Ruler().shift(RIGHT * 2)
           self.add(c, p, r)

.. manim:: DataStructuresExample
   :save_last_frame:
   :no_title:
   :ref_classes: MArray MVariable

   from manim import *
   from manim_extensions.data_structures import MArray, MVariable

   class DataStructuresExample(Scene):
       def construct(self):
           arr = MArray([1, 2, 3, 4, 5])
           var = MVariable("x", value="42").next_to(arr, DOWN, buff=1)
           self.add(arr, var)

.. manim:: GearboxExample
   :save_last_frame:
   :no_title:
   :ref_classes: Gear Rack

   from manim import *
   from manim_extensions.gearbox import Gear, Rack

   class GearboxExample(Scene):
       def construct(self):
           gear = Gear(teeth=12, radius=1, color=BLUE).shift(LEFT * 2)
           rack = Rack(teeth=10, length=4, color=RED).next_to(gear, RIGHT, buff=1)
           self.add(gear, rack)

.. manim:: NeuralNetworkExample
   :save_last_frame:
   :no_title:
   :ref_classes: NeuralNetworkMobject

   from manim import *
   from manim_extensions.neural_network import NeuralNetworkMobject

   class NeuralNetworkExample(Scene):
       def construct(self):
           nn = NeuralNetworkMobject([3, 5, 2])
           self.add(nn)

.. manim:: MeshesExample
   :save_last_frame:
   :no_title:
   :ref_classes: ManimMesh

   from manim import *
   from manim_extensions.meshes.models.data_models.mesh import Mesh
   from manim_extensions.meshes.models.manim_models.basic_mesh import ManimMesh

   class MeshesExample(Scene):
       def construct(self):
           vertices = [[0, 0, 0], [1, 0, 0], [0.5, 1, 0]]
           faces = [[0, 1, 2]]
           mesh_data = Mesh(vertices, faces)
           manim_mesh = ManimMesh(mesh_data)
           self.add(manim_mesh)

.. manim:: MindMapExample
   :save_last_frame:
   :no_title:
   :ref_classes: MindMap

   from manim import *
   from manim_extensions.mindmap import MindMap

   class MindMapExample(Scene):
       def construct(self):
           mm = MindMap()
           self.add(mm)

.. manim:: SequenceDiagramExample
   :save_last_frame:
   :no_title:
   :ref_classes: SeqActor SeqObject

   from manim import *
   from manim_extensions.sequence_diagram import SeqActor, SeqObject

   class SequenceDiagramExample(Scene):
       def construct(self):
           actor1 = SeqActor("Client", side=LEFT)
           actor2 = SeqActor("Server", side=RIGHT)
           obj = SeqObject("Request").next_to(actor1, RIGHT, buff=2)
           self.add(actor1, actor2, obj)

.. manim:: TikzExample
   :save_last_frame:
   :no_title:
   :ref_classes: Tikz

   from manim import *
   from manim_extensions.tikz import Tikz

   class TikzExample(Scene):
       def construct(self):
           tikz = Tikz(
               r"\draw[fill=green!30, draw=blue, thick] (0,0) rectangle (2,1);",
               use_pdf=False,
           )
           self.add(tikz)

.. manim:: PhysicsOpticsExample
   :save_last_frame:
   :no_title:
   :ref_classes: Lens Ray

   from manim import *
   from manim_extensions.physics import Lens, Ray

   class PhysicsOpticsExample(Scene):
       def construct(self):
           lens = Lens(f=1.0, d=0.4)
           ray = Ray(start=LEFT * 3, end=RIGHT * 3, color=YELLOW)
           self.add(lens, ray)

.. manim:: PhysicsWavesExample
   :save_last_frame:
   :no_title:
   :ref_classes: StandingWave

   from manim import *
   from manim_extensions.physics import StandingWave

   class PhysicsWavesExample(Scene):
       def construct(self):
           wave = StandingWave()
           self.add(wave)

.. manim:: PhysicsEMExample
   :save_last_frame:
   :no_title:
   :ref_classes: Charge ElectricField

   from manim import *
   from manim_extensions.physics import Charge, ElectricField

   class PhysicsEMExample(Scene):
       def construct(self):
           c1 = Charge(+1).shift(LEFT)
           c2 = Charge(-1).shift(RIGHT)
           field = ElectricField(c1, c2)
           self.add(c1, c2, field)

.. manim:: PhysicsMechanicsExample
   :save_last_frame:
   :no_title:
   :ref_classes: Pendulum

   from manim import *
   from manim_extensions.physics import Pendulum

   class PhysicsMechanicsExample(Scene):
       def construct(self):
           p = Pendulum()
           self.add(p)

.. manim:: AutomataExample
   :save_last_frame:
   :no_title:
   :ref_classes: ManimDeterminsticFiniteAutomaton

   from manim import *
   from manim_extensions.automata import ManimDeterminsticFiniteAutomaton

   class AutomataExample(Scene):
       def construct(self):
           dfa = ManimDeterminsticFiniteAutomaton()
           self.add(dfa)

.. manim:: RubiksCubeExample
   :save_last_frame:
   :no_title:
   :ref_classes: RubiksCube

   from manim import *
   from manim_extensions.rubikscube import RubiksCube

   class RubiksCubeExample(Scene):
       def construct(self):
           cube = RubiksCube(dim=3).scale(0.5)
           self.add(cube)