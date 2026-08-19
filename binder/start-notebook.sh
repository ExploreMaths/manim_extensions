#!/bin/bash
echo "=== Manim Extensions Environment Check ==="
echo ""

python -c "
import sys
print(f'Python: {sys.version}')
" 2>&1

python -c "
import manim
print(f'manim: {manim.__version__}')
" 2>&1 || echo '[WARN] manim import failed'

python -c "
import manim_extensions
print('manim_extensions: OK')
" 2>&1 || echo '[WARN] manim_extensions import failed'

python -c "
import moderngl
ctx = moderngl.create_context(standalone=True)
print('OpenGL (moderngl): OK')
" 2>&1 || echo '[WARN] OpenGL not available'

python -c "
import pymunk
s = pymunk.Space()
print('Chipmunk (pymunk): OK')
" 2>&1 || echo '[WARN] pymunk/chipmunk not available'

python -c "
import cv2
print(f'OpenCV: {cv2.__version__}')
" 2>&1 || echo '[WARN] OpenCV not available'

echo ""
echo "=== Starting Jupyter Notebook ==="
exec "$@"