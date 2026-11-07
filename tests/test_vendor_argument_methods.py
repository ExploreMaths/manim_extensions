# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Single-argument method calls on the constructed mobjects."""

import importlib

import numpy as np
import pytest
from manim import Circle, Line

CASES = [
    ("manim_extensions.algorithm.node:Node", "set_value", (1,)),
    ("manim_extensions.algorithm.utils.numpy_helper:NumpyHelper", "normalize_vector", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.automata:FiniteStateAutomaton", "get_state", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.automata:FiniteStateAutomaton", "get_state_by_id", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.automata:FiniteStateAutomaton", "get_transition_by_id", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.automata:PushDownAutomaton", "get_state", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.automata:PushDownAutomaton", "get_state_by_id", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.automata:PushDownAutomaton", "get_transition_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_automaton:ManimAutomaton", "construct_automaton_input", ('text',)),
    ("manim_extensions.automata.mobjects.manim_automaton:ManimAutomaton", "determine_input", (1,)),
    ("manim_extensions.automata.mobjects.manim_automaton:ManimAutomaton", "get_state", (1,)),
    ("manim_extensions.automata.mobjects.manim_automaton:ManimAutomaton", "get_state_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_automaton:ManimAutomaton", "get_transition_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton:ManimdeterministicFiniteAutomaton", "construct_automaton_input", ('text',)),
    ("manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton:ManimdeterministicFiniteAutomaton", "determine_input", (1,)),
    ("manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton:ManimdeterministicFiniteAutomaton", "get_state", (1,)),
    ("manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton:ManimdeterministicFiniteAutomaton", "get_state_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_deterministic_finite_state_automaton:ManimdeterministicFiniteAutomaton", "get_transition_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton:ManimNondeterministicFiniteAutomaton", "construct_automaton_input", ('text',)),
    ("manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton:ManimNondeterministicFiniteAutomaton", "determine_input", (1,)),
    ("manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton:ManimNondeterministicFiniteAutomaton", "get_state", (1,)),
    ("manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton:ManimNondeterministicFiniteAutomaton", "get_state_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_non_deterministic_finite_state_automaton:ManimNondeterministicFiniteAutomaton", "get_transition_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_pushdown_automaton:ManimPushDownAutomaton", "construct_automaton_input", ('text',)),
    ("manim_extensions.automata.mobjects.manim_pushdown_automaton:ManimPushDownAutomaton", "determine_input", (1,)),
    ("manim_extensions.automata.mobjects.manim_pushdown_automaton:ManimPushDownAutomaton", "get_state", (1,)),
    ("manim_extensions.automata.mobjects.manim_pushdown_automaton:ManimPushDownAutomaton", "get_state_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_pushdown_automaton:ManimPushDownAutomaton", "get_transition_by_id", (1,)),
    ("manim_extensions.automata.mobjects.manim_pushdown_automaton:ManimPushDownAutomaton", "push", (1,)),
    ("manim_extensions.chemistry.molecule.abstract_molecule:AbstractMolecule", "mc_molecule_to_atoms_and_bonds", (1,)),
    ("manim_extensions.chemistry.threeD.threedbond:ThreeDCylinder", "set_direction", (np.array([0., 0., 0.]),)),
    ("manim_extensions.chemistry.threeD.threedbond:ThreeDLine", "pointify", (1,)),
    ("manim_extensions.chemistry.threeD.threedbond:ThreeDLine", "set_direction", (np.array([0., 0., 0.]),)),
    ("manim_extensions.chemistry.twoD.atom:MAtomObject", "set_atom_color", (1,)),
    ("manim_extensions.chemistry.twoD.atom:MAtomObject", "set_representation", (1,)),
    ("manim_extensions.circuit.mobjects:Capacitor", "get_terminals", (1,)),
    ("manim_extensions.circuit.mobjects:CurrentSource", "get_terminals", (1,)),
    ("manim_extensions.circuit.mobjects:CurrentSource", "rotate", (1,)),
    ("manim_extensions.circuit.mobjects:Inductor", "get_terminals", (1,)),
    ("manim_extensions.circuit.mobjects:Inductor", "rotate", (1,)),
    ("manim_extensions.circuit.mobjects:Resistor", "get_terminals", (1,)),
    ("manim_extensions.circuit.mobjects:Resistor", "rotate", (1,)),
    ("manim_extensions.circuit.mobjects:VoltageSource", "get_terminals", (1,)),
    ("manim_extensions.circuit.mobjects:VoltageSource", "rotate", (1,)),
    ("manim_extensions.circuit.utils:Node", "add_dot", (1,)),
    ("manim_extensions.compass.compass.compass:Compass", "get_compass_rotate_angle_with_span", (1,)),
    ("manim_extensions.compass.compass.compass:Compass", "move_niddle_tip_to", (1,)),
    ("manim_extensions.compass.compass.compass:Compass", "split_copass_with_gain_angle", (1,)),
    ("manim_extensions.economics.ad_as:ADASDiagram", "adverse_supply_shock", (1,)),
    ("manim_extensions.economics.ad_as:ADASDiagram", "positive_supply_shock", (1,)),
    ("manim_extensions.economics.ad_as:ADASDiagram", "shift_lras", (1,)),
    ("manim_extensions.economics.is_lm:ISLMDiagram", "fiscal_contraction", (1,)),
    ("manim_extensions.economics.is_lm:ISLMDiagram", "fiscal_expansion", (1,)),
    ("manim_extensions.economics.is_lm:ISLMDiagram", "monetary_contraction", (1,)),
    ("manim_extensions.economics.is_lm:ISLMDiagram", "monetary_expansion", (1,)),
    ("manim_extensions.economics.linked:LinkedISLM_ADAS", "adverse_supply_shock", (1,)),
    ("manim_extensions.economics.linked:LinkedISLM_ADAS", "fiscal_contraction", (1,)),
    ("manim_extensions.economics.linked:LinkedISLM_ADAS", "fiscal_expansion", (1,)),
    ("manim_extensions.economics.linked:LinkedISLM_ADAS", "monetary_contraction", (1,)),
    ("manim_extensions.economics.linked:LinkedISLM_ADAS", "monetary_expansion", (1,)),
    ("manim_extensions.economics.linked:LinkedISLM_ADAS", "positive_supply_shock", (1,)),
    ("manim_extensions.economics.solow:SolowDiagram", "decrease_savings", (1,)),
    ("manim_extensions.economics.solow:SolowDiagram", "increase_depreciation", (1,)),
    ("manim_extensions.economics.solow:SolowDiagram", "increase_savings", (1,)),
    ("manim_extensions.economics.solow:SolowDiagram", "population_growth", (1,)),
    ("manim_extensions.machine_learning.diffusion.mcmc:MCMCAxes", "visualize_gaussian_proposal_about_point", (np.array([0., 0., 0.]),)),
    ("manim_extensions.machine_learning.neural_network.activation_functions.relu:ReLUFunction", "apply_function", (1,)),
    ("manim_extensions.machine_learning.neural_network.activation_functions.sigmoid:SigmoidFunction", "apply_function", (1,)),
    ("manim_extensions.machine_learning.neural_network.layers.embedding:EmbeddingLayer", "remove_gaussian_distribution", (1,)),
    ("manim_extensions.machine_learning.utils.mobjects.gridded_rectangle:GriddedRectangle", "set_color", (1,)),
    ("manim_extensions.machine_learning.utils.mobjects.list_group:ListGroup", "add", (1,)),
    ("manim_extensions.machine_learning.utils.mobjects.list_group:ListGroup", "index_of", (1,)),
    ("manim_extensions.machine_learning.utils.mobjects.list_group:ListGroup", "set_z_index", (1,)),
    ("manim_extensions.mindmap.algorithms.alg_catalog:CatalogNode", "from_data", (1,)),
    ("manim_extensions.mindmap.algorithms.alg_standard:TreeNode", "add_child", (Circle,)),
    ("manim_extensions.mindmap.algorithms.alg_time_line:TimelineNode", "from_node", (1,)),
    ("manim_extensions.mindmap.algorithms.layout_config:LayoutConfig", "get_layout_direction", (1,)),
    ("manim_extensions.mindmap.nodes.node:NodeStyle", "get_line_style", (1,)),
    ("manim_extensions.mindmap.nodes.node:NodeStyle", "get_node_style", (1,)),
    ("manim_extensions.mindmap.nodes.node:NodeStyle", "get_text_style", (1,)),
    ("manim_extensions.pymunk.constraints.constraint:VConstraint", "install", (1,)),
    ("manim_extensions.pymunk.space.SpaceScene:SpaceScene", "set_wildcard_collision_handler", (1,)),
    ("manim_extensions.pymunk.space.VSpace:VSpace", "set_position_func", (1,)),
    ("manim_extensions.pymunk.space.VSpace:VSpace", "set_velocity_func", (1,)),
]


@pytest.mark.parametrize(
    "target,meth,args",
    CASES,
    ids=["%s.%s" % (case[0], case[1]) for case in CASES],
)
def test_single_argument_method(target, meth, args):
    module_name, _, class_name = target.rpartition(":")
    module = importlib.import_module(module_name)
    instance = getattr(module, class_name)()

    getattr(instance, meth)(*args)
