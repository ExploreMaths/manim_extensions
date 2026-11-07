# SPDX-FileCopyrightText: 2026 ExploreMaths
# SPDX-License-Identifier: MIT
"""Turn a coverage.py JSON report into a shields.io endpoint badge.

The badge JSON lives in the repository so the README can point shields.io at
``raw.githubusercontent.com``; CI rewrites it on every push to ``main``.
"""

import argparse
import json
from pathlib import Path

# Pick the shield colour from the usual coverage palette, highest first.
COLORS = [
    (90.0, "brightgreen"),
    (80.0, "green"),
    (70.0, "yellowgreen"),
    (60.0, "yellow"),
]


def pick_color(percent):
    """Return the shield colour for a coverage percentage."""
    for floor, color in COLORS:
        if percent >= floor:
            return color
    return "red"


def build_badge(percent):
    """Return the shields.io endpoint payload for a coverage percentage."""
    return {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{percent:.0f}%",
        "color": pick_color(percent),
    }


def read_percent(report):
    """Read the total covered percentage from a coverage.py JSON report."""
    data = json.loads(Path(report).read_text(encoding="utf-8"))
    return float(data["totals"]["percent_covered"])


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="coverage.py JSON report")
    parser.add_argument(
        "--out",
        default=".github/badges/coverage.json",
        help="badge JSON to write (default: .github/badges/coverage.json)",
    )
    args = parser.parse_args()

    badge = build_badge(read_percent(args.report))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Keep the file stable so a run without a change leaves git untouched.
    out.write_text(json.dumps(badge, indent=2) + "\n", encoding="utf-8")
    print(f"{out}: {badge['message']} ({badge['color']})")


if __name__ == "__main__":
    main()
