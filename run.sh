#!/bin/sh
set -eu
APP_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$APP_DIR"
if [ ! -x .venv/bin/python ]; then
    printf '%s\n' 'Create a CPython 3.12 virtual environment first (clean install not yet verified):' 'python3.12 -m venv .venv' '.venv/bin/python -m pip install --only-binary=:all: -r requirements.txt'
    exit 1
fi
exec .venv/bin/python -m algoviz.app "$@"
