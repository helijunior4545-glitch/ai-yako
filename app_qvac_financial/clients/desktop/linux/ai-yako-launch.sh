#!/bin/sh
# YAKO_V1062_LINUX_LAUNCHER
set -eu
BASE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$BASE/../../../.." && pwd)
LOGDIR="${XDG_STATE_HOME:-$HOME/.local/state}/ai-yako"
mkdir -p "$LOGDIR"
exec >> "$LOGDIR/desktop-launch.log" 2>&1
printf '\n=== AI Yako V10.62 %s ===\n' "$(date -Is)"
if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo 'ERROR: no graphical desktop session (DISPLAY/WAYLAND_DISPLAY missing)'
  exit 3
fi
for PY in "$ROOT/../.venv/bin/python3" "$ROOT/.venv/bin/python3"; do
  if [ -x "$PY" ]; then
    if "$PY" -c 'from PySide6.QtWebEngineWidgets import QWebEngineView' >/dev/null 2>&1; then
      export PYTHONUNBUFFERED=1
      cd "$ROOT"
      exec "$PY" -u "$BASE/yako_app.py"
    fi
  fi
done
printf 'ERROR: no project virtualenv with PySide6 QtWebEngine.\n' >&2
printf 'Check both .venv locations and install PySide6 in the correct LOCAL virtualenv.\n' >&2
exit 2
