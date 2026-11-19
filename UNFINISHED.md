<!--
SPDX-FileCopyrightText: 2026 ExploreMaths
SPDX-License-Identifier: MIT
-->

# Unfinished work in unmaintained upstream packages

Only packages whose upstream is no longer maintained are listed here. The
vendored copy is already at the last upstream commit, so any functional gap
cannot be fixed by a future vendor sync; it needs a local change.

Last checked: 2026-11-19.

## `manim_extensions/meshes`

- **Upstream:** [`bmmtstb/manim-meshes`](https://github.com/bmmtstb/manim-meshes)
- **Last upstream commit:** 2023-10-24 (`9d6cb83`), synced in this repository.
- **Why local-only:** upstream has had no commits for more than three years.

Status: all previously listed gaps are now implemented locally.

- Edge caches are maintained incrementally with per-edge face reference
  counts for face addition, removal and updates; topology-wide operations
  rebuild the cache once. Edges therefore stay consistent after every mesh
  mutation.
- Part lookup and duplicate-part removal compare face-index sets
  independently of face order, so reordered or non-clockwise parts are
  treated as equal.
- `FastManimMesh` supports `set_mesh`, `add_face`, `remove_face` and
  `update_vertex`; each mutation rebuilds its point and triangle-index
  shader arrays.
- Delaunay base-case face insertion now goes through the documented
  `_refresh_renderer` helper instead of an ad-hoc renderer call.

## `manim_extensions/machine_learning`

- **Upstream:** [`helblazer811/ManimML`](https://github.com/helblazer811/ManimML)
- **Last upstream commit:** 2023-11-04 (`5e8f7cb`), synced in this repository.
- **Why local-only:** `VENDORED.md` records the upstream as archived; in
  practice it has had no commits for about three years.

Status: no known unfinished feature remains. The local vendored copy already
implements the upstream stubs that were missing (see the `machine_learning`
entry in `VENDORED.md`), including `DecisionTreeEmbedding`, tree/surface
unfolding, `NeuralNetwork.replace_layer`, and the variational-autoencoder
forward passes.
