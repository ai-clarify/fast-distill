#!/bin/bash

set -e

if python - <<'PY'
import importlib.util
import sys

has_xdist = importlib.util.find_spec("xdist") is not None
has_xdist = has_xdist or importlib.util.find_spec("pytest_xdist") is not None
sys.exit(0 if has_xdist else 1)
PY
then
    exec pytest -n auto tests/unit
fi

exec pytest tests/unit
