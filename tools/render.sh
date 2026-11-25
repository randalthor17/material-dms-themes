#!/usr/bin/env bash
# Render a program in a private Xvfb display (never touches the real session) and save PNGs.
# usage: render.sh OUT.png CONFIG_HOME -- command args...   (needs xvfb-run, imagemagick, xdotool)
# RENDER_CLICKS="x:y:name ..." clicks each point after the first shot and saves OUT-name.png; RENDER_WAIT=seconds.
set -eu
out=$1; cfg=$2; shift 3
export XDG_CONFIG_HOME=$cfg GDK_BACKEND=x11 QT_QPA_PLATFORM=xcb OUT=$out
xvfb-run -a -s "-screen 0 1100x800x24" bash -c '
  "$@" >/dev/null 2>&1 &
  sleep "${RENDER_WAIT:-5}"
  import -window root "$OUT"
  for c in ${RENDER_CLICKS:-}; do
    IFS=: read -r x y name <<<"$c"
    xdotool mousemove "$x" "$y" click 1; sleep 1
    import -window root "${OUT%.png}-$name.png"
  done
  kill %1 2>/dev/null || true
' _ "$@"
