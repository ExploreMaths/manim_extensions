#!/bin/bash
LOGFILE=/manim/binder_startup.log

echo "========================================" > $LOGFILE
echo "  Manim Extensions Binder Startup" >> $LOGFILE
echo "========================================" >> $LOGFILE
echo "" >> $LOGFILE

echo "--- System ---" >> $LOGFILE
echo "Date: $(date)" >> $LOGFILE
echo "User: $(whoami)" >> $LOGFILE
echo "HOME: $HOME" >> $LOGFILE
echo "" >> $LOGFILE

echo "--- Python ---" >> $LOGFILE
python -c "import sys; print(f'Python {sys.version}')" >> $LOGFILE 2>&1
echo "" >> $LOGFILE

echo "--- OpenGL / Xvfb ---" >> $LOGFILE
XVFB_WHD="${XVFB_WHD:-1280x720x24}"
Xvfb :99 -screen 0 "${XVFB_WHD}" +ac &
XVFB_PID=$!
sleep 1
export DISPLAY=:99
echo "Xvfb PID=${XVFB_PID}, DISPLAY=${DISPLAY}" >> $LOGFILE
if command -v glxinfo >/dev/null 2>&1; then
    glxinfo -b 2>&1 | head -5 >> $LOGFILE
fi
echo "" >> $LOGFILE

echo "--- manim ---" >> $LOGFILE
python -c "import manim; print(f'manim {manim.__version__}')" >> $LOGFILE 2>&1 || echo "manim: IMPORT FAILED" >> $LOGFILE
echo "" >> $LOGFILE

echo "--- moderngl ---" >> $LOGFILE
python -c "
import moderngl
ctx = moderngl.create_context(standalone=True)
print(f'OpenGL: {ctx.version} | {ctx.renderer}')
" >> $LOGFILE 2>&1 || echo "moderngl: IMPORT FAILED" >> $LOGFILE
echo "" >> $LOGFILE

echo "--- manim_extensions ---" >> $LOGFILE
python -c "import manim_extensions; print('OK')" >> $LOGFILE 2>&1 || echo "manim_extensions: IMPORT FAILED" >> $LOGFILE
echo "" >> $LOGFILE

echo "--- ffmpeg ---" >> $LOGFILE
ffmpeg -version 2>&1 | head -1 >> $LOGFILE || echo "ffmpeg: NOT FOUND" >> $LOGFILE
echo "" >> $LOGFILE

echo "--- Chipmunk (pymunk) ---" >> $LOGFILE
python -c "import pymunk; s=pymunk.Space(); print('OK')" >> $LOGFILE 2>&1 || echo "pymunk: IMPORT FAILED" >> $LOGFILE
echo "" >> $LOGFILE

echo "--- OpenCV ---" >> $LOGFILE
python -c "import cv2; print(f'OpenCV {cv2.__version__}')" >> $LOGFILE 2>&1 || echo "opencv: IMPORT FAILED" >> $LOGFILE
echo "" >> $LOGFILE

echo "========================================" >> $LOGFILE
echo "  Starting Jupyter..." >> $LOGFILE
echo "========================================" >> $LOGFILE
echo "" >> $LOGFILE

cat $LOGFILE

exec "$@"