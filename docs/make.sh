#!/usr/bin/env bash
# Bash helper for Sphinx documentation (bash equivalent of make.bat).
# Works alongside the Makefile; use this on shells where `make` is unavailable.
# Usage: ./docs/make.sh [help|html|clean|qhelp|latexpdf|...]
set -e

# Always run from this script's directory (docs/) so relative paths resolve.
cd "$(dirname "$0")"

: "${SPHINXBUILD:=sphinx-build}"
SOURCEDIR="source"
BUILDDIR="build"

# Verify sphinx-build is available.
if ! command -v "$SPHINXBUILD" >/dev/null 2>&1 ; then
    echo "The 'sphinx-build' command was not found. Make sure you have Sphinx"
    echo "installed (e.g. 'pip install -e .[docs]'), or set the SPHINXBUILD"
    echo "environment variable to the full path of the 'sphinx-build' executable."
    echo "https://www.sphinx-doc.org/"
    exit 1
fi

if [ "$#" -eq 0 ]; then
    "$SPHINXBUILD" -M help "$SOURCEDIR" "$BUILDDIR" ${SPHINXOPTS} ${O}
else
    "$SPHINXBUILD" -M "$*" "$SOURCEDIR" "$BUILDDIR" ${SPHINXOPTS} ${O}
fi
