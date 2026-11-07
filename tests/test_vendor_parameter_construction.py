# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Constructors that need one plain argument, exercised through smoke tests.

Many mobjects accept a single required argument such as a size, a text value or
a submobject. These cases pin down that the constructor builds a usable object
for the literal each documentation example uses.
"""

import importlib

import numpy as np
import pytest
from manim import Circle, Line, Square

CASES = [
    ("manim_extensions.algorithm.array:Array", ('text',)),
    ("manim_extensions.algorithm.queue:Queue", (1,)),
    ("manim_extensions.arabic.text:ArabicText", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.state:State", (1,)),
    ("manim_extensions.automata.mobjects.automata_dependencies.transition:Transition", (Circle, Circle)),
    ("manim_extensions.automata.mobjects.manim_automaton_input:Token", (1, 1)),
    ("manim_extensions.chemistry.manim_chemistry_molecule.mc_atom:MCAtom", (1,)),
    ("manim_extensions.chemistry.manim_chemistry_molecule.mc_bond:MCBond", (1,)),
    ("manim_extensions.chemistry.twoD.chemical_formula:ChemicalFormula", ('text',)),
    ("manim_extensions.data_structures.m_array:MArray", (1,)),
    ("manim_extensions.data_structures.m_array:MArrayElement", (1,)),
    ("manim_extensions.data_structures.m_variable:MVariable", (1,)),
    ("manim_extensions.gearbox.gear_mobjects.gear_mobject:Gear", (1,)),
    ("manim_extensions.gearbox.gear_mobjects.gear_mobject:Rack", (1,)),
    ("manim_extensions.machine_learning.decision_tree.decision_tree:SplitNode", (1, 1)),
    ("manim_extensions.machine_learning.decision_tree.decision_tree_surface:AABB", (1,)),
    ("manim_extensions.machine_learning.neural_network.layers.convolutional_2d:Convolutional2DLayer", (1,)),
    ("manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_feed_forward:Convolutional2DToFeedForward", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.convolutional_2d_to_max_pooling_2d:Convolutional2DToMaxPooling2D", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.embedding_to_feed_forward:EmbeddingToFeedForward", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.feed_forward:FeedForwardLayer", (1,)),
    ("manim_extensions.machine_learning.neural_network.layers.feed_forward_to_embedding:FeedForwardToEmbedding", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.feed_forward_to_feed_forward:FeedForwardToFeedForward", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.feed_forward_to_image:FeedForwardToImage", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.feed_forward_to_math_operation:FeedForwardToMathOperation", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.feed_forward_to_vector:FeedForwardToVector", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.image:ImageLayer", (1,)),
    ("manim_extensions.machine_learning.neural_network.layers.image_to_convolutional_2d:ImageToConvolutional2DLayer", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.image_to_feed_forward:ImageToFeedForward", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.max_pooling_2d_to_feed_forward:MaxPooling2DToFeedForward", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.paired_query_to_feed_forward:PairedQueryToFeedForward", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.triplet_to_feed_forward:TripletToFeedForward", (Circle, Circle)),
    ("manim_extensions.machine_learning.neural_network.layers.vector:VectorLayer", (1,)),
    ("manim_extensions.meshes.delaunay.divide_and_conquer:DivideAndConquer", (Circle, Circle)),
    ("manim_extensions.meshes.exceptions:InvalidMeshDimensionsException", (Circle, Circle)),
    ("manim_extensions.mindmap.algorithms.alg_catalog:CatalogLayout", (1,)),
    ("manim_extensions.mindmap.algorithms.alg_standard:StandardLayout", (1,)),
    ("manim_extensions.mindmap.algorithms.alg_tidy_tree:IYLNode", (Circle, Circle)),
    ("manim_extensions.mindmap.algorithms.alg_tidy_tree:TidyTreeLayout", (1,)),
    ("manim_extensions.mindmap.algorithms.alg_time_line:TimeLineLayout", (1,)),
    ("manim_extensions.mobjects:ColorText", (np.array([0., 0., 0.]),)),
    ("manim_extensions.mobjects:CropImageMobject", (np.array([0., 0., 0.]),)),
    ("manim_extensions.mobjects:MathTexDoublearrow", (Circle,)),
    ("manim_extensions.mobjects:MathTexLine", (Circle,)),
    ("manim_extensions.mobjects:TreeDiagram", ([0, 1],)),
    ("manim_extensions.nerdfont.icons:NerdFontIcon", (1,)),
    ("manim_extensions.physics.optics.lenses:Lens", (1, 1)),
    ("manim_extensions.physics.optics.rays:Ray", (1, 1)),
    ("manim_extensions.pymunk.constraints.VDampedSpring:VDampedSpring", (Circle, Circle)),
    ("manim_extensions.pymunk.constraints.VGearJoint:VGearJoint", (Circle, Circle)),
    ("manim_extensions.pymunk.constraints.VGrooveJoint:VGrooveJoint", (Circle, Circle)),
    ("manim_extensions.pymunk.constraints.VPivotJoint:VPivotJoint", (Circle, Circle)),
    ("manim_extensions.pymunk.constraints.VRotaryLimitJoint:VRotaryLimitJoint", (Circle, Circle)),
    ("manim_extensions.pymunk.constraints.VSimpleMotor:VSimpleMotor", (Circle, Circle)),
    ("manim_extensions.pymunk.constraints.VSlideJoint:VSlideJoint", (Circle, Circle)),
    ("manim_extensions.sequence_diagram.seq_actor:SeqActor", ('text',)),
    ("manim_extensions.sequence_diagram.seq_object:SeqObject", ('text',)),
    ("manim_extensions.table.cell:Cell", ('text',)),
    ("manim_extensions.table.row:Row", ('text',)),
    ("manim_extensions.tikz.tikz:Tikz", ('text',)),
]


@pytest.mark.parametrize("target,args", CASES, ids=[case[0] for case in CASES])
def test_single_argument_constructor(target, args):
    module_name, _, class_name = target.rpartition(":")
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)

    instance = cls(*args)

    assert instance is not None
