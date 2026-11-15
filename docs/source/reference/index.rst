.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

Reference Manual
================

The reference manual contains the complete API for ``manim_extensions``.

Inheritance Graphs
------------------

The full inheritance graph of every public class in the library, in a single
diagram. Classes defined by ``manim_extensions`` are shown in green, classes
from base Manim in blue.

.. inheritance-diagram::
   manim_extensions.mobjects
   manim_extensions.animations
   manim_extensions.gearbox.gear_mobjects.gear_mobject
   manim_extensions.mindmap.mindmap.mindmap
   manim_extensions.mindmap.nodes.node
   manim_extensions.mindmap.animations.animations
   manim_extensions.compass.compass.compass
   manim_extensions.compass.compass.pencil
   manim_extensions.compass.compass.ruler
   manim_extensions.compass.scene.compass_scene
   manim_extensions.algorithm.node.Node
   manim_extensions.algorithm.array.Array
   manim_extensions.algorithm.queue.Queue
   manim_extensions.automata.mobjects.manim_automaton.ManimAutomaton
   manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton.ManimdeterministicFiniteAutomaton
   manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton.ManimNondeterministicFiniteAutomaton
   manim_extensions.automata.mobjects.manim_pushdown_automaton.ManimPushDownAutomaton
   manim_extensions.automata.mobjects.manim_state.ManimState
   manim_extensions.automata.mobjects.manim_transition.ManimTransition
   manim_extensions.automata.mobjects.manim_transition.ManimPushDownAutomatonTransition
   manim_extensions.automata.mobjects.manim_automaton_input.ManimAutomataInput
   manim_extensions.automata.mobjects.manim_automaton_input.Token
   manim_extensions.automata.mobjects.manim_turing_machine.ManimTuringMachine
   manim_extensions.circuit.utils.Source
   manim_extensions.circuit.utils.Circuit
   manim_extensions.circuit.utils.Node
   manim_extensions.circuit.mobjects.VoltageSource
   manim_extensions.circuit.mobjects.CurrentSource
   manim_extensions.circuit.mobjects.Inductor
   manim_extensions.circuit.mobjects.Resistor
   manim_extensions.circuit.mobjects.Capacitor
   manim_extensions.circuit.mobjects.Ground
   manim_extensions.circuit.mobjects.Opamp
   manim_extensions.cad_drawing_utils.dimensions.Pointer_Label_Free
   manim_extensions.cad_drawing_utils.dimensions.Pointer_To_Mob
   manim_extensions.cad_drawing_utils.dimensions.Linear_Dimension
   manim_extensions.cad_drawing_utils.dimensions.Angle_Dimension_3point
   manim_extensions.cad_drawing_utils.dimensions.Angle_Dimension_Mob
   manim_extensions.cad_drawing_utils.dimensions.CAD_ArrowHead
   manim_extensions.cad_drawing_utils.hatch.Hatch_lines
   manim_extensions.cad_drawing_utils.path_mapper.Path_mapper
   manim_extensions.cad_drawing_utils.path_mapper.Dashed_line_mobject
   manim_extensions.cad_drawing_utils.path_mapper.DashDot_mobject
   manim_extensions.cad_drawing_utils.path_mapper.Path_Offset_Mobject
   manim_extensions.cad_drawing_utils.path_mapper.Curve_Warp
   manim_extensions.cad_drawing_utils.utils.Bezier_Handlebars
   manim_extensions.radar.animations.Shockwave
   manim_extensions.radar.animations.RadarMorph
   manim_extensions.radar.animations.RadarReveal
   manim_extensions.radar.animations.RadarBurstIn
   manim_extensions.radar.animations.RadarFade
   manim_extensions.radar.animations.GlitchFlash
   manim_extensions.radar.backdrop.DeepSpace
   manim_extensions.radar.camera.CameraRig
   manim_extensions.radar.chart.RadarChart
   manim_extensions.radar.config.RadarConfig
   manim_extensions.radar.data.RadarData
   manim_extensions.radar.legacy.RadarV1Scene
   manim_extensions.radar.legacy.RadarV2Scene
   manim_extensions.radar.numbers.RollingNumber
   manim_extensions.radar.overflow.OverflowRadarChart
   manim_extensions.radar.poly.PolyRadarChart
   manim_extensions.radar.poly.PolyMorph
   manim_extensions.radar.reel.RadarReel
   manim_extensions.radar.theme.RadarTheme
   manim_extensions.three_d.core.GaussianSurface
   manim_extensions.three_d.core.SaddleSurface
   manim_extensions.three_d.core.ParaboloidSurface
   manim_extensions.three_d.core.EllipsoidSurface
   manim_extensions.three_d.core.TorusSurface
   manim_extensions.three_d.core.HyperboloidOneSheet
   manim_extensions.three_d.core.GaussianSurfaceScene
   manim_extensions.three_d.core.SaddleSurfaceScene
   manim_extensions.three_d.core.ParaboloidSurfaceScene
   manim_extensions.three_d.core.EllipsoidSurfaceScene
   manim_extensions.three_d.core.TorusSurfaceScene
   manim_extensions.three_d.core.HyperboloidOneSheetScene
   manim_extensions.code_blocks.manim_code_blocks.Theme
   manim_extensions.code_blocks.manim_code_blocks.ProgrammingLanguage
   manim_extensions.code_blocks.manim_code_blocks.CodeBlock
   manim_extensions.data_structures.m_array.MArrayElement
   manim_extensions.data_structures.m_array.MArray
   manim_extensions.data_structures.m_array.MArrayPointer
   manim_extensions.data_structures.m_array.MArraySlidingWindow
   manim_extensions.data_structures.m_variable.MVariable
   manim_extensions.meshes.models.manim_models.basic_mesh.ManimMesh
   manim_extensions.meshes.models.manim_models.basic_mesh.Manim2DMesh
   manim_extensions.meshes.models.manim_models.triangle_mesh.TriangleManim2DMesh
   manim_extensions.meshes.models.manim_models.opengl_mesh.FastManimMesh
   manim_extensions.meshes.models.data_models.mesh.Mesh
   manim_extensions.physics.wave.RadialWave
   manim_extensions.physics.wave.LinearWave
   manim_extensions.physics.wave.StandingWave
   manim_extensions.physics.rigid_mechanics.rigid_mechanics.Space
   manim_extensions.physics.rigid_mechanics.pendulum.MultiPendulum
   manim_extensions.physics.rigid_mechanics.pendulum.Pendulum
   manim_extensions.physics.optics.rays.Ray
   manim_extensions.physics.optics.lenses.Lens
   manim_extensions.physics.electromagnetism.magnetostatics.Wire
   manim_extensions.physics.electromagnetism.magnetostatics.MagneticField
   manim_extensions.physics.electromagnetism.electrostatics.Charge
   manim_extensions.physics.electromagnetism.electrostatics.ElectricField
   manim_extensions.rubikscube.cube.RubiksCube
   manim_extensions.rubikscube.cubie.Cubie
   manim_extensions.rubikscube.cube_animations.CubeMove
   manim_extensions.sequence_diagram.seq_object.SeqObject
   manim_extensions.sequence_diagram.seq_actor.SeqActor
   manim_extensions.sequence_diagram.seq_action.SeqAction
   manim_extensions.tikz.tikz.Tikz
   manim_extensions.tikz.template.TikzTemplate
   manim_extensions.arabic.text
   manim_extensions.chemistry.element.element.Element
   manim_extensions.chemistry.periodic_table.table_objects.PeriodicTable
   manim_extensions.chemistry.twoD.molecule.MMoleculeObject
   manim_extensions.chemistry.twoD.graph_molecule.GraphMolecule
   manim_extensions.chemistry.threeD.threedmolecule.ThreeDMolecule
   manim_extensions.chemistry.bohr_atom.bohr_atom.BohrAtom
   manim_extensions.economics.base.EconDiagram
   manim_extensions.economics.supply_demand.SupplyDemandDiagram
   manim_extensions.economics.ad_as.ADASDiagram
   manim_extensions.economics.is_lm.ISLMDiagram
   manim_extensions.economics.solow.SolowDiagram
   manim_extensions.fontawesome.manim_fontawesome
   manim_extensions.machine_learning.neural_network.neural_network.NeuralNetwork
   manim_extensions.machine_learning.decision_tree.decision_tree.DecisionTreeDiagram
   manim_extensions.pymunk.space.SpaceScene.SpaceScene
   manim_extensions.pymunk.space.VSpace.VSpace
   manim_extensions.pymunk.custom_mobjects.v_spring.VSpring
   manim_extensions.pymunk.constraints.constraint.VConstraint
   manim_extensions.qr_codes.qr
   manim_extensions.svg_animations.html_parsed_vmobject.HTMLParsedVMobject
   manim_extensions.table.table.Table
   manim_extensions.table.row.Row
   manim_extensions.table.cell.Cell
   manim_extensions.weighted_line.weighted_line.WeightedLine
   manim_extensions.nerdfont.icons.NerdFontIcon
   :parts: 1
   :private-bases:
   :top-classes: manim.mobject.mobject.Mobject, manim.animation.animation.Animation, manim.mobject.types.vectorized_mobject.VMobject, manim.mobject.types.vectorized_mobject.SVGMobject, manim.mobject.geometry.line.Line, manim.animation.composition.AnimationGroup

Module Index
------------

.. toctree::
   :hidden:
   :maxdepth: 3
   :titlesonly:

   algorithm/index
   arabic/index
   automata/index
   basic/index
   chemistry/index
   circuit/index
   cad_drawing_utils/index
   compass/index
   code_blocks/index
   data_structures/index
   economics/index
   fontawesome/index
   gearbox/index
   machine_learning/index
   meshes/index
   mindmap/index
   mobject_svg/index
   nerdfont/index
   physics/index
   pymunk/index
   qr_codes/index
   radar/index
   rubikscube/index
   sequence_diagram/index
   svg_animations/index
   table/index
   three_d/index
   tikz/index
   utils/index
   weighted_line/index

* :vendorstatus:`algorithm`
* :vendorstatus:`arabic`
* :vendorstatus:`automata`
* :vendorstatus:`basic`
* :vendorstatus:`cad_drawing_utils`
* :vendorstatus:`chemistry`
* :vendorstatus:`circuit`
* :vendorstatus:`code_blocks`
* :vendorstatus:`compass`
* :vendorstatus:`data_structures`
* :vendorstatus:`economics`
* :vendorstatus:`fontawesome`
* :vendorstatus:`gearbox`
* :vendorstatus:`machine_learning`
* :vendorstatus:`meshes`
* :vendorstatus:`mindmap`
* :vendorstatus:`mobject_svg`
* :vendorstatus:`nerdfont`
* :vendorstatus:`physics`
* :vendorstatus:`pymunk`
* :vendorstatus:`qr_codes`
* :vendorstatus:`radar`
* :vendorstatus:`rubikscube`
* :vendorstatus:`sequence_diagram`
* :vendorstatus:`svg_animations`
* :vendorstatus:`table`
* :vendorstatus:`three_d`
* :vendorstatus:`tikz`
* :vendorstatus:`utils`
* :vendorstatus:`weighted_line`
