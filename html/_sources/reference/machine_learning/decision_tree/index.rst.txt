.. SPDX-FileCopyrightText: 2026 ExploreMaths
.. SPDX-License-Identifier: MIT

decision_tree
=============

.. module:: manim_extensions.machine_learning.decision_tree

Classes
-------

.. autosummary::
   :nosignatures:

   ~decision_tree.DecisionTreeContainer
   ~decision_tree.DecisionTreeDiagram
   ~decision_tree.LeafNode
   ~decision_tree.SplitNode

Usage
-----

Pass a fitted scikit-learn tree to the diagram; feature names and class names are optional labels.

.. code-block:: python

   from sklearn.tree import DecisionTreeClassifier
   from manim_extensions.machine_learning.decision_tree.decision_tree import (
       DecisionTreeDiagram,
   )

   clf = DecisionTreeClassifier(max_depth=2).fit(X, y)
   diagram = DecisionTreeDiagram(
       clf.tree_,
       feature_names=["sepal length", "sepal width"],
       class_names=["setosa", "versicolor", "virginica"],
   )

Modules
-------

.. autosummary::
   :nosignatures:

   ~decision_tree
   ~decision_tree_embedding
   ~decision_tree_surface
   ~helpers

.. toctree::
   :hidden:
   :maxdepth: 1

   decision_tree
   decision_tree_embedding
   decision_tree_surface
   helpers
