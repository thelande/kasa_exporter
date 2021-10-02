#!/bin/sh
#
set -e

if ! pip freeze | grep -q -E '^build\W+'; then
  pip install build
fi

python -m build --wheel
