# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT

"""Typed access to the shared machine-learning configuration singleton."""

from __future__ import annotations

from . import ManimMLConfig

#: Shared configuration used by neural-network and layer implementations.
config: ManimMLConfig = ManimMLConfig()
