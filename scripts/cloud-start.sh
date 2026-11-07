#!/usr/bin/env bash
# Static preview only. Safe to run again: if 8765 is open, exit 0.
set -euo pipefail

cd "$(dirname "$0")/.."
PORT=8765

if bash -c "echo >/dev/tcp/127.0.0.1/${PORT}" >/dev/null 2>&1; then
  echo "static preview already listening on ${PORT}"
  exit 0
fi

echo "starting static preview on 0.0.0.0:${PORT}"
exec python3 -m http.server "${PORT}" --bind 0.0.0.0
