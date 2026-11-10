#!/usr/bin/env bash
set -o errexit

if command -v uv >/dev/null 2>&1; then
    uv venv --python 3.12 /tmp/build_venv
    source /tmp/build_venv/bin/activate
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

python manage.py collectstatic --no-input --clear
