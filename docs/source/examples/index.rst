.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Example Gallery
===============

The examples below use Manim's ``.. manim::`` directive to render the scene
inline. Each example demonstrates one of the core extension modules.

.. manim:: LabelDotExample
   :save_last_frame:
   :ref_classes: LabelDot

   from manim import *
   from manim_extensions import LabelDot

   class LabelDotExample(Scene):
       def construct(self):
           a = LabelDot("A", [-2, -1, 0], label_pos=DOWN, buff=0.2, color=RED)
           b = LabelDot("B", [1, 2, 0], label_pos=UP, buff=0.2, color=GREEN)
           c = LabelDot("C", [3, -1, 0], label_pos=DOWN, buff=0.2, color=BLUE)

           triangle = Polygon(
               a.get_center(), b.get_center(), c.get_center(),
               color=PURE_YELLOW, fill_opacity=0.1
           )

           self.add(triangle, a, b, c)

.. manim:: MathTexHelpersExample
   :save_last_frame:
   :ref_classes: MathTexLine MathTexBrace MathTexDoublearrow

   from manim import *
   from manim_extensions import MathTexLine, MathTexBrace, MathTexDoublearrow

   class MathTexHelpersExample(Scene):
       def construct(self):
           line = Line(LEFT * 3, RIGHT * 3)
           self.add(line)

           slope = MathTexLine(MathTex("y = x"), direction=UP, color=BLUE).next_to(line, UP*2, buff=1.0)
           brace = MathTexBrace(line, MathTex(r"\Delta x"), direction=UP)
           arrow = MathTexDoublearrow(MathTex(r"\Leftrightarrow"), direction=DOWN).next_to(line, DOWN, buff=1.0)

           self.add(slope, brace, arrow)

.. manim:: GeometryHelpersExample
   :save_last_frame:
   :ref_classes: ExtendedLine PerpendicularLine PerpendicularSign

   from manim import *
   from manim_extensions import ExtendedLine, PerpendicularLine, PerpendicularSign

   class GeometryHelpersExample(Scene):
       def construct(self):
           base = Line(LEFT * 3, RIGHT * 3, color=BLUE)
           ext = ExtendedLine(base, extend_distance=1.0)
           perp = PerpendicularLine(UP * 1.5, base, color=PURE_YELLOW)
           sign = PerpendicularSign(base, perp, length=0.3, color=WHITE)

           self.add(base, ext, perp, sign)

.. manim:: VMobjectIntExample
   :save_last_frame:
   :ref_classes: LabelDot
   :ref_functions: VMobjectInt

   from manim import *
   from manim_extensions import VMobjectInt, LabelDot

   class VMobjectIntExample(Scene):
       def construct(self):
           c1 = Circle(radius=2.5, color=BLUE).shift(LEFT)
           c2 = Circle(radius=2.5, color=GREEN).shift(RIGHT)
           pts = sorted(VMobjectInt(c1, c2), key=lambda p: p[1])

           self.add(c1, c2)
           self.add(LabelDot("P_1", pts[1], label_pos=UP, buff=0.1))
           self.add(LabelDot("P_2", pts[0], label_pos=DOWN, buff=0.1))

           line = Line(pts[0], pts[1], color=PURE_YELLOW, stroke_width=2)
           self.add(line)

.. manim:: TextAnimationsExample
   :ref_classes: TypeWriter WriteRandom FadeOutRandom

   from manim import *
   from manim_extensions import TypeWriter, WriteRandom, FadeOutRandom

   class TextAnimationsExample(Scene):
       def construct(self):
           t1 = Text("Hello World").shift(UP * 1.5)
           self.play(TypeWriter(t1, interval=0.08))
           self.wait(0.5)

           t2 = Text("Fade Me Out")
           self.add(t2)
           self.play(FadeOutRandom(t2))
           self.wait(0.5)

           t3 = Text("Random Write!").shift(DOWN * 1.5)
           self.play(WriteRandom(t3))
           self.wait(1)

.. manim:: ColorTextExample
   :save_last_frame:
   :ref_classes: ColorText

   from manim import *
   from manim_extensions import ColorText

   class ColorTextExample(Scene):
       def construct(self):
           t1 = ColorText([255, 80, 80]).shift(UP * 2)
           t2 = ColorText([80, 200, 255])
           t3 = ColorText([150, 255, 100]).shift(DOWN * 2)

           self.add(t1, t2, t3)

.. manim:: FileTreeExample
   :save_last_frame:
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
           })

           self.add(tree)

.. manim:: TreeDiagramExample
   :save_last_frame:
   :ref_classes: TreeDiagram

   from manim import *
   from manim_extensions import TreeDiagram

   class TreeDiagramExample(Scene):
       def construct(self):
           tree = {
               "Root": {
                   "Branch A": {"Leaf 1", "Leaf 2"},
                   "Branch B": {"Leaf 3", "Leaf 4"},
                   "Branch C": {"Leaf 5"},
               }
           }
           diagram = TreeDiagram(tree)
           diagram.scale_to_fit_width(9)

           self.add(diagram)

.. manim:: HighlightAnimationsExample
   :ref_classes: PassingRectangle HighLightWithLines

   from manim import *
   from manim_extensions import PassingRectangle, HighLightWithLines

   class HighlightAnimationsExample(Scene):
       def construct(self):
           mob = Text("Hello World")
           self.add(mob)

           box = SurroundingRectangle(mob, color=PURE_YELLOW)
           self.play(PassingRectangle(box))
           self.wait(0.5)
           self.play(HighLightWithLines(mob, color=GREEN))
           self.wait(1)

.. manim:: DecorationHelpersExample
   :save_last_frame:
   :ref_classes: ShadowAround ObjectBorder

   from manim import *
   from manim_extensions import ShadowAround, ObjectBorder

   class DecorationHelpersExample(Scene):
       def construct(self):
           c = Circle(radius=1.4, fill_color=TEAL, fill_opacity=1, stroke_width=0).shift(LEFT * 3)
           shadow = ShadowAround(c, blur_width=0.4, shadow_color=WHITE)

           t = Text("Stylized", font_size=40).shift(RIGHT * 3)
           border = ObjectBorder(t)

           self.add(shadow, c)
           self.add(t, border)

.. manim:: TrailExample
   :ref_classes: Trail

   from manim import *
   from manim_extensions import Trail

   class TrailExample(Scene):
       def construct(self):
           circle = Circle(radius=2.5, color=GREY, stroke_width=1)
           self.add(circle)

           dot = Dot(color=BLUE).shift(LEFT * 2.5)
           trail = Trail(dot, trail_color=BLUE, nums=30).start_trace()
           self.add(trail)

           self.play(Rotating(dot, about_point=ORIGIN, rate_func=linear), run_time=3)

.. manim:: ChineseMathTexExample
   :save_last_frame:
   :ref_classes: ChineseMathTex

   from manim import *
   from manim_extensions import ChineseMathTex

   class ChineseMathTexExample(Scene):
       def construct(self):
           tex1 = ChineseMathTex(r"勾股定理：a^{2} + b^{2} = c^{2}").shift(UP * 1.5)
           tex2 = ChineseMathTex(r"二次方程：x = \frac{-b \pm \sqrt{b^{2}-4ac}}{2a}").shift(DOWN * 1.5)

           self.add(tex1)
           self.add(tex2)

.. manim:: ThreeDVectorExample
   :save_last_frame:
   :ref_classes: ThreeDVector

   from manim import *
   from manim_extensions import ThreeDVector

   class ThreeDVectorExample(ThreeDScene):
       def construct(self):
           self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)

           axes = ThreeDAxes(x_range=[-3, 4], y_range=[-3, 4], z_range=[-2, 3])
           self.add(axes)

           v1 = ThreeDVector([2, 1, 1.5], color=PURE_YELLOW)
           v2 = ThreeDVector([-1, 2, 2], color=RED)
           v3 = ThreeDVector([1, -1, 1], color=GREEN)

           l1 = MathTex(r"\mathbf{v}_1", color=PURE_YELLOW).next_to([2, 1, 1.5], UP + RIGHT, buff=0.3)
           l2 = MathTex(r"\mathbf{v}_2", color=RED).next_to([-1, 2, 2], UP + LEFT, buff=0.3)
           l3 = MathTex(r"\mathbf{v}_3", color=GREEN).next_to([1, -1, 1], DOWN + RIGHT, buff=0.3)

           self.add(v1, v2, v3)
           self.add_fixed_in_frame_mobjects(l1, l2, l3)

.. manim:: MoreAnimationsExample
   :ref_classes: ReversedWrite FadeInRandom GrowRandom LaggedCreation

   from manim import *
   from manim_extensions import ReversedWrite, FadeInRandom, GrowRandom, LaggedCreation

   class MoreAnimationsExample(Scene):
       def construct(self):
           text = Text("Animation")
           self.add(text)

           self.play(ReversedWrite(text))
           self.wait(0.5)
           self.play(GrowRandom(text))
           self.wait(0.5)

           box = SurroundingRectangle(text, color=BLUE)
           self.play(LaggedCreation(box, lag_ratio=0.2))
           self.wait(1)

.. manim:: AlgorithmExample
   :save_last_frame:
   :ref_classes: manim_extensions.algorithm.node.Node Array Queue

   from manim import *
   from manim_extensions.algorithm import Node, Array, Queue

   class AlgorithmExample(Scene):
       def construct(self):
           nodes = VGroup(
               Node("1"), Node("2"), Node("3"), Node("4")
           ).arrange(RIGHT, buff=0.6)
           nodes.scale_to_fit_width(8)

           arr = Array([10, 20, 30, 40], total_width=6).next_to(nodes, DOWN, buff=1.2)
           arr.scale_to_fit_width(8)

           q = Queue(5, init_data=[1, 2, 3], total_width=6).next_to(arr, DOWN, buff=1.2)
           q.scale_to_fit_width(8)

           self.add(nodes)
           self.add(arr)
           self.add(q)

.. manim:: CircuitExample
   :save_last_frame:
   :ref_classes: VoltageSource Resistor Ground Circuit

   from manim import *
   from manim_extensions.circuit import VoltageSource, Resistor, Ground
   from manim_extensions.circuit.utils import Circuit

   class CircuitExample(Scene):
       def construct(self):
           vs = VoltageSource(value=10).shift(LEFT * 3 + UP * 0.5)
           r1 = Resistor(label="10k").next_to(vs, RIGHT, buff=3.0)
           r2 = Resistor(label="20k").next_to(r1, DOWN, buff=2.2)
           g = Ground().next_to(r2, DOWN, buff=1.3)

           circuit = Circuit()
           circuit.add_components(vs, r1, r2, g)

           circuit.add_wire(vs.get_terminals("positive"), r1.get_terminals("left"))
           circuit.add_wire(r1.get_terminals("right"), r2.get_terminals("left"))
           circuit.add_wire(r2.get_terminals("right"), g.get_terminals())
           circuit.add_wire(g.get_terminals(), vs.get_terminals("negative"))

           self.add(circuit)

.. manim:: CompassExample
   :ref_classes: ExtendedLine CompassScene DrawPath
   :ref_functions: VMobjectInt

   from manim import *
   from manim_extensions import VMobjectInt, ExtendedLine
   from manim_extensions.compass import CompassScene, DrawPath

   class CompassExample(CompassScene):
       def construct(self):
           self.play(FadeIn(self.pencil, self.ruler))
           self.draw_line(
               start=LEFT * 3,
               end=RIGHT * 3,
               run_time=1.5,
               color=WHITE
           )
           self.put_ruler_aside(run_time=0.5)
           self.put_pencil_away(5 * RIGHT, run_time=0.5)
           self.play(FadeIn(self.compass))
           self.compass_move_niddle_tip_to(LEFT)
           self.compass_split_span(5)
           arc1 = self.draw_arc(
               niddle_point=LEFT * 2,
               pen_point=UP*3+LEFT*2,
               angle=-PI
           )
           self.compass_move_niddle_tip_to(RIGHT)
           self.compass_split_span(5)
           arc2 = self.draw_arc(
               niddle_point=RIGHT * 2,
               pen_point=UP*3+RIGHT*2,
               angle=PI
           )
           self.play(FadeOut(self.compass))
           pts = VMobjectInt(arc1, arc2)
           base_line = Line(pts[0], pts[1], color=PURE_YELLOW)
           perp = ExtendedLine(base_line, extend_distance=0.5)
           self.set_ruler(start=perp.get_start(), end=perp.get_end(), with_pencil=True)
           self.play(DrawPath(self.pencil, perp))
           self.put_pencil_away(5 * RIGHT, run_time=0.5)
           self.put_ruler_aside(run_time=0.5)
           self.wait()

.. manim:: DataStructuresExample
   :save_last_frame:
   :ref_classes: MArray MVariable

   from manim import *
   from manim_extensions.data_structures import MArray, MVariable

   class DataStructuresExample(Scene):
       def construct(self):
           arr = MArray(self, [10, 20, 30, 40, 50], label="arr")
           var = MVariable(self, value="42", index="x").next_to(arr, DOWN, buff=1.5)

           self.add(arr, var)

.. manim:: GearboxExample
   :save_last_frame:
   :ref_classes: Gear Rack

   from manim import *
   import numpy as np
   from manim_extensions.gearbox import Gear, Rack

   class GearboxExample(Scene):
       def construct(self):
           gear1 = Gear(12, module=0.3, stroke_opacity=0, fill_color=BLUE, fill_opacity=1).shift(LEFT * 3)
           gear2 = Gear(8, module=0.3, stroke_opacity=0, fill_color=RED, fill_opacity=1)
           gear2.mesh_to(gear1)

           rack = Rack(12, module=gear1.m, stroke_opacity=0, fill_color=GREEN, fill_opacity=0.7)
           rack_width = rack.z * rack.pitch
           rack_center = gear1.get_center() + DOWN * gear1.rp
           rack.shift(np.array([rack_center[0] - rack_width / 2, rack_center[1], 0]))

           self.add(gear1, gear2, rack)

.. manim:: NeuralNetworkExample
   :save_last_frame:
   :ref_classes: NeuralNetworkMobject

   from manim import *
   from manim_extensions.neural_network import NeuralNetworkMobject

   class NeuralNetworkExample(Scene):
       def construct(self):
           nn = NeuralNetworkMobject([3, 5, 4, 2])
           nn.scale_to_fit_width(9)

           self.add(nn)

.. manim:: MeshesExample
   :save_last_frame:
   :ref_classes: Mesh Manim2DMesh

   from manim import *
   from manim_extensions import LabelDot
   from manim_extensions.meshes.models.data_models.mesh import Mesh
   from manim_extensions.meshes.models.manim_models.basic_mesh import Manim2DMesh

   class MeshesExample(Scene):
       def construct(self):
           vertices = [[0, 0, 0], [3, 0, 0], [1.5, 3, 0]]
           faces = [[0, 1, 2]]
           mesh_data = Mesh(vertices, faces)
           manim_mesh = Manim2DMesh(mesh_data)

           v0 = LabelDot("V0", [0, 0, 0], label_pos=DOWN + LEFT, buff=0.1).set_color(PURE_YELLOW)
           v1 = LabelDot("V1", [3, 0, 0], label_pos=DOWN + RIGHT, buff=0.1).set_color(PURE_YELLOW)
           v2 = LabelDot("V2", [1.5, 3, 0], label_pos=UP, buff=0.1).set_color(PURE_YELLOW)

           self.add(manim_mesh)
           self.add(v0, v1, v2)

.. manim:: MindMapExample
   :save_last_frame:
   :ref_classes: MindMap

   from manim import *
   from manim_extensions.mindmap import MindMap

   class MindMapExample(Scene):
       def construct(self):
           data = {
               'node': MathTex(r"\text{Manim Extensions}"),
               'child': [
                   {
                       'node': MathTex(r"\text{Physics}"),
                       'child': [
                           {'node': MathTex(r"\text{Optics}")},
                           {'node': MathTex(r"\text{Mechanics}")},
                           {'node': MathTex(r"\text{Waves}")},
                       ]
                   },
                   {
                       'node': MathTex(r"\text{Geometry}"),
                       'child': [
                           {'node': MathTex(r"\text{Circuit}")},
                           {'node': MathTex(r"\text{Compass}")},
                       ]
                   },
                   {
                       'node': MathTex(r"\text{Algorithms}"),
                       'child': [
                           {'node': MathTex(r"\text{Automata}")},
                           {'node': MathTex(r"\text{Data Structures}")},
                       ]
                   },
               ]
           }
           mm = MindMap(data)
           mm.scale_to_fit_width(10)
           self.add(mm)

.. manim:: SequenceDiagramExample
   :ref_classes: SeqActor SeqObject SeqAction

   from manim import *
   from manim_extensions.sequence_diagram import SeqActor, SeqObject, SeqAction

   class SequenceDiagramExample(Scene):
       def construct(self):
           client = SeqActor("Client").shift(LEFT * 4)
           server = SeqActor("Server").shift(RIGHT * 4)

           request = SeqObject("HTTP Request")
           response = SeqObject("HTTP Response")

           self.play(*SeqAction.introduce_actors(client, server))
           self.wait(0.5)

           for anim in SeqAction.subject_gives_gift_to_target(client, request, server):
               self.play(anim)
           self.wait(1)

           for anim in SeqAction.subject_gives_gift_to_target(server, response, client):
               self.play(anim)
           self.wait(2)

.. manim:: TikzExample
   :save_last_frame:
   :ref_classes: Tikz

   from manim import *
   from manim_extensions.tikz import Tikz

   class TikzExample(Scene):
       def construct(self):
           tikz = Tikz(
               r"""
               \draw[fill=blue!20, draw=blue, thick] (0,0) rectangle (3,2);
               \draw[fill=red!30, draw=red, thick] (1,1) circle (0.6);
               \draw[->, thick] (3.5,1) -- (5,1) node[right] {input};
               \node at (1.5, 2.5) {Diagram};
               """,
               use_pdf=False,
           )
           self.add(tikz)

.. manim:: PhysicsOpticsExample
   :save_last_frame:
   :ref_classes: Lens Ray

   from manim import *
   from manim_extensions.physics import Lens, Ray

   class PhysicsOpticsExample(Scene):
       def construct(self):
           lens = Lens(f=1.5, d=0.4)
           object = Triangle(color=RED).scale(0.45).shift(LEFT * 3 + DOWN * 0.5)
           rays = VGroup(
               Ray(start=LEFT * 3 + UP * 0.5, direction=RIGHT, init_length=5, color=PURE_YELLOW),
               Ray(start=LEFT * 3, direction=RIGHT, init_length=5, color=PURE_YELLOW),
               Ray(start=LEFT * 3 + DOWN * 0.5, direction=RIGHT, init_length=5, color=PURE_YELLOW),
           )

           self.add(object, lens, rays)

.. manim:: PhysicsWavesExample
   :save_last_frame:
   :ref_classes: StandingWave

   from manim import *
   from manim_extensions.physics import StandingWave

   class PhysicsWavesExample(Scene):
       def construct(self):
           wave = StandingWave()

           self.add(wave)

.. manim:: PhysicsEMExample
   :save_last_frame:
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
   :ref_classes: Pendulum

   from manim import *
   from manim_extensions.physics import Pendulum

   class PhysicsMechanicsExample(Scene):
       def construct(self):
           p = Pendulum(length=3, initial_theta=0.4)

           self.add(p)

.. manim:: AutomataExample
   :save_last_frame:
   :ref_classes: ManimdeterministicFiniteAutomaton

   from manim import *
   from manim_extensions.automata import ManimdeterministicFiniteAutomaton

   class AutomataExample(Scene):
       def construct(self):
           dfa_json = {
               'structure': {
                   'type': 'fa',
                   'automaton': {
                       'state': [
                           {'@id': '0', '@name': 'q0', 'x': '80.0', 'y': '100.0', 'initial': None},
                           {'@id': '1', '@name': 'q1', 'x': '250.0', 'y': '100.0', 'final': None},
                       ],
                       'transition': [
                           {'from': '0', 'to': '0', 'read': '0'},
                           {'from': '0', 'to': '1', 'read': '1'},
                           {'from': '1', 'to': '1', 'read': '0'},
                           {'from': '1', 'to': '0', 'read': '1'},
                       ]
                   }
               }
           }
           dfa = ManimdeterministicFiniteAutomaton(json_template=dfa_json)
           self.add(dfa)