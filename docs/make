#!/usr/bin/env bash
# Simple make wrapper for Sphinx documentation.
# Run from the docs/ directory: ./make clean && ./make html

set -e

export PATH="/c/Program Files/Graphviz/bin:$PATH"

case "${1:-html}" in
  clean)
    rm -rf _build/html
    echo "Cleaned _build/html"
    ;;
  html)
    rm -rf _build/html
    sphinx-build -b html . _build/html
    ;;
  *)
    echo "Usage: $0 {clean|html}"
    exit 1
    ;;
esac
