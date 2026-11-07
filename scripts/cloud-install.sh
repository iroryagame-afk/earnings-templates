#!/usr/bin/env bash
# Idempotent, keyless check for the static earnings-template workspace.
# No package installs, no network, no secrets.
set -euo pipefail

cd "$(dirname "$0")/.."

command -v python3 >/dev/null 2>&1
command -v google-chrome >/dev/null 2>&1
command -v google-chrome-stable >/dev/null 2>&1

python3 -m py_compile scripts/accept-demo.py

python3 - <<'PY'
import pathlib
import sys

root = pathlib.Path(".")
need = [
    "fixtures/demo/single-poster.html",
    "fixtures/demo/combined-poster.html",
    "fixtures/demo/measure.js",
    "single-company/common.css",
    "single-company/template.html",
    "single-company/assets/LXGWWenKai-Regular.ttf",
    "combined/template.html",
    "combined/assets/LXGWWenKai-Regular.ttf",
]
missing = [path for path in need if not (root / path).is_file()]
if missing:
    raise SystemExit("缺少验收所需文件: " + ", ".join(missing))
print("install ok")
print("python", sys.version.split()[0])
PY

google-chrome-stable --version
