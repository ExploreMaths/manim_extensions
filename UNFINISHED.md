<!--
SPDX-FileCopyrightText: 2026 ExploreMaths
SPDX-License-Identifier: MIT
-->

# Unfinished work in unmaintained upstream packages

Only packages whose upstream is no longer maintained are listed here.  The
vendored copy is already at the last upstream commit, so these gaps cannot be
fixed by a future vendor sync; they need a local change.

Last checked: 2026-11-18.

## `manim_extensions/meshes`

- **Upstream:** [`bmmtstb/manim-meshes`](https://github.com/bmmtstb/manim-meshes)
- **Last upstream commit:** 2023-10-24 (`9d6cb83`), synced in this repository.
- **Why local-only:** upstream has had no commits for more than three years.

Unfinished:

- `models/data_models/mesh.py`: vertex/face/part updates only refresh part of
  the edge cache (`# Fixme: update only partly`, eight sites around lines 586,
  664, 691, 722, 861, 1397 and 1420).  Edges can become stale after a mesh
  mutation.
- `models/data_models/mesh.py`: face-equality question at line 536 — whether
  two faces remain equal when their vertices are randomly sorted and not
  clockwise.
- `models/manim_models/opengl_mesh.py`: `FastManimMesh` only displays an
  existing mesh; it does not implement mesh manipulation (line 25).
- `delaunay/divide_and_conquer.py`: incremental Delaunay update is marked
  `# update hack` (line 209).

## `manim_extensions/machine_learning`

- **Upstream:** [`helblazer811/ManimML`](https://github.com/helblazer811/ManimML)
- **Last upstream commit:** 2023-11-04 (`5e8f7cb`), synced in this repository.
- **Why local-only:** `VENDORED.md` records the upstream as archived; in
  practice it has had no commits for about three years.

The local vendored copy already implements the upstream stubs that were
missing (see the `machine_learning` entry in `VENDORED.md`), including
`DecisionTreeEmbedding`, tree/surface unfolding, `NeuralNetwork.replace_layer`,
and the variational-autoencoder forward passes.  No known unfinished feature
remains; any future functional work has to be done locally.
