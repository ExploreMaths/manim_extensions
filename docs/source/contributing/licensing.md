<!--
SPDX-FileCopyrightText: 2026 ExploreMaths
SPDX-License-Identifier: MIT
-->

# Licensing and REUSE

The project uses the [REUSE](https://reuse.software/) specification for licensing. Every file must have a clear license and copyright declaration.

## New original files

Add an SPDX header at the very top:

```python
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
```

## Canonical header format

All header blocks follow this single canonical layout, enforced by
`workflow/validate_headers.py`:

```python
# SPDX-FileCopyrightText: <upstream authors>
# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
# patched: <reason for the local change>

"""Module docstring."""
```

Rules:

- The block is contiguous: no empty lines and no bare `#` lines between
  copyright and license.
- Exactly **one** `SPDX-License-Identifier` line, placed after every
  `SPDX-FileCopyrightText` line. Duplicate blocks from vendoring are merged.
- Each copyright holder appears once, and a year is written once
  (`2026 ExploreMaths`, not `2026 2026 ExploreMaths`).
- Project copyright (`2026 ExploreMaths`) comes last.
- Every `# patched: <reason>` line comes **after** the license line, never
  inside the SPDX block.
- Exactly one blank line separates the header from the module docstring or
  first import.

Run the checker (or let it rewrite all headers in place):

```bash
python workflow/validate_headers.py
python workflow/validate_headers.py --fix
```

## Vendored / third-party code

When vendoring an external package, record its copyright, license, and upstream source in `REUSE.toml` under a `[[annotations]]` block for the relevant path. See the existing entries (e.g. `algorithm`, `chemistry`, `physics`) for the format.

CI runs `reuse lint` and `validate_headers.py` — a missing or incorrectly
formatted license declaration will fail the build.
