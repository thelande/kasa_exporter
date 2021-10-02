$cmdOutput = pip freeze

if (-Not ($cmdOutput -Match '^build\W+')) {
    pip install build
}

python -m build
