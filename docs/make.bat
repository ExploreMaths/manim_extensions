#!/usr/bin/env bash
# Bash equivalent of the original Sphinx ``make.bat`` (Windows batch).
# The docs build on Unix / bash shells is done with this script or the
# GNU ``Makefile``. Usage:  bash docs/make.bat <target>   (e.g. html, clean, help)

set -euo pipefail

cd "$(dirname "$0")"

SPHINXBUILD="${SPHINXBUILD:-sphinx-build}"
SOURCEDIR="source"
BUILDDIR="build"

# Make sure sphinx-build is available.
if ! command -v "$SPHINXBUILD" >/dev/null 2>&1; then
    echo "The 'sphinx-build' command was not found. Make sure you have Sphinx"
    echo "installed (e.g. 'pip install -e .[docs]'), or set the SPHINXBUILD"
    echo "environment variable to the full path of the 'sphinx-build' executable."
    echo "https://www.sphinx-doc.org/"
    exit 1
fi

if [ "$#" -eq 0 ]; then
    "$SPHINXBUILD" -M help "$SOURCEDIR" "$BUILDDIR" ${SPHINXOPTS:-} ${O:-}
else
    "$SPHINXBUILD" -M "$*" "$SOURCEDIR" "$BUILDDIR" ${SPHINXOPTS:-} ${O:-}
fi
