#!/bin/sh
set -eu
APP_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$APP_DIR"
.venv/bin/python -m unittest discover -v
./run.sh --headless --frames 3
.venv/bin/python tools/verify.py
