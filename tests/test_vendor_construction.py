# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Smoke tests that construct every zero-argument class in the package.

A class whose ``__init__`` needs no arguments is part of the public surface the
documentation advertises, so it must at least be constructible. These cases are
deliberately shallow: they guard the import graph, the default configuration and
the mobject assembly path without mimicking a full scene.
"""

import importlib

import pytest

CASES = [
    "manim_extensions.algorithm.node:Node",
    "manim_extensions.algorithm.node:NodeConfig",
    "manim_extensions.algorithm.node:NodeSolt",
    "manim_extensions.algorithm.utils.numpy_helper:NumpyHelper",
    "manim_extensions.arabic.text:ArabicTemplate",
    "manim_extensions.automata.mobjects.automata_dependencies.automata:FiniteStateAutomaton",
    "manim_extensions.automata.mobjects.automata_dependencies.automata:PushDownAutomaton",
    "manim_extensions.automata.mobjects.manim_animations:ManimAnimations",
    "manim_extensions.automata.mobjects.manim_automaton:ManimAutomaton",
    "manim_extensions.automata.mobjects.manim_cli:ManimAutomataCLI",
    "manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton:ManimdeterministicFiniteAutomaton",
    "manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton:ManimNondeterministicFiniteAutomaton",
    "manim_extensions.automata.mobjects.manim_pushdown_automaton:ManimPushDownAutomaton",
    "manim_extensions.automata.mobjects.manim_turing_machine:ManimTuringMachine",
    "manim_extensions.chemistry.bohr_atom.bohr_atom:BohrAtom",
    "manim_extensions.chemistry.element.element:Element",
    "manim_extensions.chemistry.future_classes.future_classes:BatterySchema",
    "manim_extensions.chemistry.future_classes.future_classes:Electron",
    "manim_extensions.chemistry.future_classes.future_classes:Element",
    "manim_extensions.chemistry.future_classes.future_classes:ElementFrame",
    "manim_extensions.chemistry.future_classes.future_classes:Hole",
    "manim_extensions.chemistry.future_classes.future_classes:MOSFETTransistor",
    "manim_extensions.chemistry.future_classes.future_classes:NPNTransistor",
    "manim_extensions.chemistry.manim_chemistry_molecule.mc_element:MCElement",
    "manim_extensions.chemistry.manim_chemistry_molecule.mc_molecule:MCMolecule",
    "manim_extensions.chemistry.molecule.abstract_molecule:AbstractMolecule",
    "manim_extensions.chemistry.molecule.molecule:Molecule",
    "manim_extensions.chemistry.orbitals.orbitals:Orbital",
    "manim_extensions.chemistry.orbitals.orbitals:OrbitalBase",
    "manim_extensions.chemistry.orbitals.orbitals:OrbitalNegative",
    "manim_extensions.chemistry.orbitals.orbitals:OrbitalPositive",
    "manim_extensions.chemistry.periodic_table.table_objects:MElementObject",
    "manim_extensions.chemistry.threeD.threedbond:ThreeDCylinder",
    "manim_extensions.chemistry.threeD.threedbond:ThreeDLine",
    "manim_extensions.chemistry.threeD.utils:OpenGLSphere",
    "manim_extensions.chemistry.twoD.atom:MAtomObject",
    "manim_extensions.chemistry.twoD.graph_molecule:SimpleLine",
    "manim_extensions.chemistry.utils.file_handler:IncorrectFormat",
    "manim_extensions.circuit.mobjects:Capacitor",
    "manim_extensions.circuit.mobjects:CurrentSource",
    "manim_extensions.circuit.mobjects:Ground",
    "manim_extensions.circuit.mobjects:Inductor",
    "manim_extensions.circuit.mobjects:Opamp",
    "manim_extensions.circuit.mobjects:Resistor",
    "manim_extensions.circuit.mobjects:VoltageSource",
    "manim_extensions.circuit.utils:Circuit",
    "manim_extensions.circuit.utils:Node",
    "manim_extensions.compass.compass.compass:Compass",
    "manim_extensions.compass.compass.pencil:Pencil",
    "manim_extensions.compass.compass.ruler:Ruler",
    "manim_extensions.compass.scene.compass_scene:CompassScene",
    "manim_extensions.compass.scene.ruler_scene:SingleRulerScene",
    "manim_extensions.economics.ad_as:ADASDiagram",
    "manim_extensions.economics.base:EconDiagram",
    "manim_extensions.economics.is_lm:ISLMDiagram",
    "manim_extensions.economics.linked:LinkedISLM_ADAS",
    "manim_extensions.economics.solow:SolowDiagram",
    "manim_extensions.economics.supply_demand:SupplyDemandDiagram",
    "manim_extensions.fontawesome.manim_fontawesome:Brand",
    "manim_extensions.fontawesome.manim_fontawesome:Regular",
    "manim_extensions.fontawesome.manim_fontawesome:Solid",
    "manim_extensions.machine_learning:ManimMLConfig",
    "manim_extensions.machine_learning.diffusion.mcmc:MCMCAxes",
    "manim_extensions.machine_learning.diffusion.mcmc:MultidimensionalGaussianPosterior",
    "manim_extensions.machine_learning.neural_network.activation_functions.relu:ReLUFunction",
    "manim_extensions.machine_learning.neural_network.activation_functions.sigmoid:SigmoidFunction",
    "manim_extensions.machine_learning.neural_network.animations.dropout:XMark",
    "manim_extensions.machine_learning.neural_network.architectures.variational_autoencoder:VariationalAutoencoder",
    "manim_extensions.machine_learning.neural_network.layers.embedding:EmbeddingLayer",
    "manim_extensions.machine_learning.neural_network.layers.embedding:NeuralNetworkEmbeddingTestScene",
    "manim_extensions.machine_learning.neural_network.layers.max_pooling_2d:MaxPooling2DLayer",
    "manim_extensions.machine_learning.neural_network.layers.parent_layers:ThreeDLayer",
    "manim_extensions.machine_learning.scene:ManimML3DScene",
    "manim_extensions.machine_learning.utils.mobjects.gridded_rectangle:GriddedRectangle",
    "manim_extensions.machine_learning.utils.mobjects.list_group:ListGroup",
    "manim_extensions.meshes.exceptions:BadParameterException",
    "manim_extensions.meshes.exceptions:FaultyVarArrayException",
    "manim_extensions.meshes.exceptions:InvalidMeshException",
    "manim_extensions.meshes.exceptions:InvalidRequestException",
    "manim_extensions.meshes.exceptions:InvalidTypeException",
    "manim_extensions.meshes.exceptions:MeshIndexException",
    "manim_extensions.mindmap.algorithms.alg_catalog:CatalogNode",
    "manim_extensions.mindmap.algorithms.alg_standard:TreeNode",
    "manim_extensions.mindmap.algorithms.alg_tidy_tree:WrappedTree",
    "manim_extensions.mindmap.algorithms.alg_time_line:TimelineNode",
    "manim_extensions.mindmap.algorithms.layout:Layout",
    "manim_extensions.mindmap.algorithms.layout_config:LayoutConfig",
    "manim_extensions.mindmap.algorithms.layout_factory:LayoutFactory",
    "manim_extensions.mindmap.nodes.node:NodeStyle",
    "manim_extensions.mobjects:ChineseMathTex",
    "manim_extensions.mobjects:ThreeDVector",
    "manim_extensions.physics.electromagnetism.electrostatics:Charge",
    "manim_extensions.physics.electromagnetism.electrostatics:ElectricField",
    "manim_extensions.physics.electromagnetism.magnetostatics:MagneticField",
    "manim_extensions.physics.rigid_mechanics.pendulum:Pendulum",
    "manim_extensions.physics.rigid_mechanics.rigid_mechanics:Space",
    "manim_extensions.physics.rigid_mechanics.rigid_mechanics:SpaceScene",
    "manim_extensions.physics.wave:LinearWave",
    "manim_extensions.physics.wave:RadialWave",
    "manim_extensions.physics.wave:StandingWave",
    "manim_extensions.pymunk.constraints.constraint:VConstraint",
    "manim_extensions.pymunk.custom_mobjects.apple:Apple",
    "manim_extensions.pymunk.custom_mobjects.gear:Gear",
    "manim_extensions.pymunk.custom_mobjects.v_spring:VSpring",
    "manim_extensions.pymunk.space.SpaceScene:SpaceScene",
    "manim_extensions.pymunk.space.VSpace:VSpace",
    "manim_extensions.pymunk.utils.logger_tool:SingletonLogger",
    "manim_extensions.rubikscube.cube:RubiksCube",
    "manim_extensions.scenes:ConstantStrokeWidthScene",
    "manim_extensions.sequence_diagram.seq_action:SeqAction",
    "manim_extensions.tikz.template:TikzTemplate",
    "manim_extensions.weighted_line.weighted_line:WeightedLine",
]


@pytest.mark.parametrize("target", CASES)
def test_zero_argument_constructor(target):
    module_name, _, class_name = target.rpartition(":")
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)

    instance = cls()

    assert instance is not None
